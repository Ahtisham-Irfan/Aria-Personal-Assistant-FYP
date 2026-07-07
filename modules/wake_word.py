from PySide6.QtCore import QThread, Signal
import speech_recognition as sr


DEFAULT_WAKE_PHRASES = [
    "hey aria", "hi aria", "ok aria", "aria"
]


class _WakeThread(QThread):
    detected = Signal()
    error = Signal(str)

    def __init__(self, phrases, parent=None):
        super().__init__(parent)
        self.phrases = phrases

    def run(self):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(
                    source, duration=0.4
                )
                audio = recognizer.listen(
                    source, timeout=6, phrase_time_limit=4
                )
            text = recognizer.recognize_google(
                audio, language="en-US"
            ).lower().strip()
            print(f"Wake word heard: {text}")

            if any(p in text for p in self.phrases):
                self.detected.emit()
            else:
                self.error.emit(
                    "Wake word not detected. Try again."
                )
        except sr.WaitTimeoutError:
            self.error.emit("I did not hear anything.")
        except sr.UnknownValueError:
            self.error.emit("Could not understand. Try again.")
        except sr.RequestError:
            self.error.emit(
                "No internet for wake word detection."
            )
        except Exception as e:
            self.error.emit(str(e))


class WakeWordDetector:
    """
    Lightweight wake-word check: listens once for a short
    phrase and checks it against the configured wake words
    (e.g. 'Hey Aria'). Not a true always-listening wake-word
    engine (that would need something like Porcupine), but a
    push-to-talk style confirmation step.
    """

    def __init__(self):
        self.phrases = list(DEFAULT_WAKE_PHRASES)
        self._thread = None

    def set_wake_word(self, phrase):
        phrase = phrase.lower().strip()
        if phrase and phrase not in self.phrases:
            self.phrases.insert(0, phrase)

    def start_once(self, on_detected=None, on_error=None):
        self.stop()
        self._thread = _WakeThread(self.phrases)
        if on_detected:
            self._thread.detected.connect(on_detected)
        if on_error:
            self._thread.error.connect(on_error)
        self._thread.start()

    def stop(self):
        if self._thread and self._thread.isRunning():
            self._thread.requestInterruption()
            self._thread.wait(200)
        self._thread = None
