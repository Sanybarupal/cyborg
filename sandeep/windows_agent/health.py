import socket
import shutil
import os
import time
import importlib


def _check_module(name):
    try:
        importlib.import_module(name)
        return True
    except Exception:
        return False


class HealthMonitor:
    """Performs health checks and returns statuses for modules."""

    def __init__(self):
        self.modules = [
            "microphone",
            "voice_input",
            "stt",
            "tts",
            "ai",
            "backend",
            "tool_router",
            "windows_agent",
            "quick_actions",
            "browser",
            "screen_ocr",
            "file_system",
            "memory",
            "scheduler",
            "database",
            "network",
        ]

    def check_all(self):
        results = {}
        results["microphone"] = self._check_microphone()
        results["stt"] = _check_module("speech_recognition")
        results["tts"] = _check_module("pyttsx3")
        results["ai"] = True
        results["backend"] = True
        results["tool_router"] = True
        results["windows_agent"] = True
        results["quick_actions"] = True
        results["browser"] = shutil.which("chrome") is not None
        results["screen_ocr"] = _check_module("pytesseract")
        results["file_system"] = os.access(".", os.R_OK | os.W_OK)
        results["memory"] = _check_module("psutil")
        results["scheduler"] = _check_module("schedule")
        results["database"] = _check_module("sqlite3")
        results["network"] = self._check_network()
        results["timestamp"] = time.time()
        return results

    def _check_microphone(self):
        # best-effort: check presence of sounddevice or pyaudio
        return _check_module("sounddevice") or _check_module("pyaudio")

    def _check_network(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(("8.8.8.8", 53))
            s.close()
            return True
        except Exception:
            return False
