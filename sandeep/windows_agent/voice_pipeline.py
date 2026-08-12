import speech_recognition as sr
import pyttsx3


class VoicePipeline:
    """Simple voice pipeline: capture -> STT -> return text. Minimal checks only."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()

    def check_microphone(self):
        try:
            mic_list = sr.Microphone.list_microphone_names()
            return len(mic_list) > 0
        except Exception:
            return False

    def listen_once(self, timeout: float = 5.0) -> dict:
        if not self.check_microphone():
            return {"ok": False, "error": "No microphone available"}
        with sr.Microphone() as source:
            try:
                audio = self.recognizer.listen(source, timeout=timeout)
            except Exception as e:
                return {"ok": False, "error": str(e)}
        try:
            text = self.recognizer.recognize_google(audio)
            return {"ok": True, "transcript": text}
        except sr.UnknownValueError:
            return {"ok": False, "error": "STT could not understand audio"}
        except sr.RequestError as e:
            return {"ok": False, "error": f"STT request error: {e}"}

    def speak(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()
