import os
import subprocess
import shutil
import psutil
import ctypes


def open_application(name: str, args: dict = None):
    """Try to open an application by name or path. Returns PID on success."""
    args = args or {}
    # Try executable lookup
    path = shutil.which(name) or name
    try:
        if os.path.isfile(path):
            p = subprocess.Popen([path])
        else:
            # try startfile for known app names or URL-like
            os.startfile(path)
            return True
        return p.pid
    except Exception:
        # fallback: try common locations for Chrome/Notepad/Code
        common = {
            "notepad": r"C:\\Windows\\system32\\notepad.exe",
            "code": r"C:\\Program Files\\Microsoft VS Code\\Code.exe",
            "chrome": r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "whatsapp": r"C:\\Users\\%USERNAME%\\AppData\\Local\\WhatsApp\\WhatsApp.exe",
        }
        key = name.lower() if name else ""
        guess = common.get(key)
        if guess and os.path.exists(guess):
            try:
                p = subprocess.Popen([guess])
                return p.pid
            except Exception:
                return None
        return None


def open_path(path: str) -> bool:
    try:
        os.startfile(path)
        return True
    except Exception:
        return False


def verify_process_running(pid: int) -> bool:
    try:
        return psutil.pid_exists(int(pid))
    except Exception:
        return False


def change_wallpaper(image_path: str) -> bool:
    try:
        SPI_SETDESKWALLPAPER = 20
        result = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)
        return bool(result)
    except Exception:
        return False


def get_system_status() -> dict:
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:").percent
        batt = None
        try:
            batt = psutil.sensors_battery().percent if psutil.sensors_battery() else None
        except Exception:
            batt = None
        return {"cpu": cpu, "memory": mem, "disk_C": disk, "battery": batt}
    except Exception as e:
        return {"error": str(e)}
