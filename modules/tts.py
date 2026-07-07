from PySide6.QtCore import QThread, Signal


class _SpeakThread(QThread):
    started_speaking = Signal()
    finished_speaking = Signal()

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text

    def run(self):
        self.started_speaking.emit()
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 170)
            engine.setProperty('volume', 0.9)
            engine.say(self.text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"TTS error: {e}")
        self.finished_speaking.emit()


class TTSEngine:
    """
    Simple threaded text-to-speech wrapper around pyttsx3
    so speaking never blocks the UI thread.
    """

    def __init__(self):
        self._thread = None
        self.rate = 150
        self.volume = 0.9

    def set_rate(self, rate):
        self.rate = rate

    def set_volume(self, volume):
        # expects 0-100
        self.volume = max(0.0, min(1.0, volume / 100))

    def speak(self, text, on_start=None, on_finish=None):
        if not text:
            if on_finish:
                on_finish()
            return

        self.stop()

        self._thread = _SpeakThread(text)
        if on_start:
            self._thread.started_speaking.connect(on_start)
        if on_finish:
            self._thread.finished_speaking.connect(on_finish)
        self._thread.start()

    def stop(self):
        if self._thread and self._thread.isRunning():
            self._thread.terminate()
            self._thread.wait(500)
        self._thread = None
