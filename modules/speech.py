import speech_recognition as sr
from PySide6.QtCore import QThread, Signal


class SpeechThread(QThread):
    text_received = Signal(str)
    error_occurred = Signal(str)
    listening_started = Signal()
    listening_stopped = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = False
        self.recognizer = sr.Recognizer()

        # Tuned for fast accurate response
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.6
        self.recognizer.phrase_threshold = 0.2
        self.recognizer.non_speaking_duration = 0.3

    def run(self):
        self.is_running = True
        with sr.Microphone() as source:
            # Quick noise calibration
            self.recognizer.adjust_for_ambient_noise(
                source, duration=0.5
            )
            self.listening_started.emit()

            while self.is_running:
                try:
                    audio = self.recognizer.listen(
                        source,
                        timeout=8,
                        phrase_time_limit=8
                    )
                    if not self.is_running:
                        break

                    try:
                        text = self.recognizer\
                            .recognize_google(
                            audio,
                            language="en-US"
                        ).strip()

                        if text:
                            print(f"Heard: {text}")
                            self.text_received.emit(text)
                            self.is_running = False
                            break

                    except sr.UnknownValueError:
                        # Try alternate recognition
                        try:
                            result = self.recognizer\
                                .recognize_google(
                                audio,
                                language="en-US",
                                show_all=True
                            )
                            if (
                                result
                                and isinstance(result, dict)
                            ):
                                alts = result.get(
                                    'alternative', []
                                )
                                if alts:
                                    best = alts[0].get(
                                        'transcript', ''
                                    )
                                    if best:
                                        self.text_received\
                                            .emit(best)
                                        self.is_running = False
                                        break
                        except Exception:
                            pass
                        continue

                    except sr.RequestError:
                        self.error_occurred.emit(
                            "No internet for speech recognition."
                        )
                        self.is_running = False
                        break

                except sr.WaitTimeoutError:
                    self.error_occurred.emit(
                        "I did not hear anything. Try again."
                    )
                    self.is_running = False
                    break

                except Exception as e:
                    print(f"Speech error: {e}")
                    self.is_running = False
                    break

        self.listening_stopped.emit()

    def stop(self):
        self.is_running = False


class SpeechRecognizer:
    def __init__(self):
        self.thread = None
        self._active = False

    def start_listening(
        self,
        on_text=None,
        on_start=None,
        on_stop=None,
        on_error=None
    ):
        self.stop_listening()

        self.thread = SpeechThread()

        if on_text:
            self.thread.text_received.connect(on_text)
        if on_start:
            self.thread.listening_started.connect(on_start)
        if on_stop:
            self.thread.listening_stopped.connect(on_stop)
        if on_error:
            self.thread.error_occurred.connect(on_error)

        self.thread.listening_stopped.connect(
            self._on_done
        )
        self.thread.start()
        self._active = True

    def _on_done(self):
        self._active = False

    def stop_listening(self):
        if self.thread and self._active:
            self.thread.stop()
            self.thread.wait(2000)
            self._active = False

    def is_active(self):
        return self._active