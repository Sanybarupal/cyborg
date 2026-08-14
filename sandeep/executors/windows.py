"""
SANDEEP Windows Executor — Real Windows control via PowerShell Start-Process.
Uses PowerShell Start-Process to launch apps in the INTERACTIVE user session
so they appear visibly on the desktop (not as hidden background processes).
"""
import os
import subprocess
import datetime
import glob
import ctypes
import time

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def _ps_launch(exe_path: str) -> bool:
    """
    Launch an executable using PowerShell Start-Process.
    This ensures the app appears in the interactive user session (visible window).
    """
    try:
        safe_path = exe_path.replace("'", "''")
        cmd = ["powershell", "-WindowStyle", "Hidden", "-Command",
               f"Start-Process '{safe_path}'"]
        result = subprocess.run(cmd, capture_output=True, timeout=10)
        if result.returncode != 0:
            err = result.stderr.decode("utf-8", errors="replace").strip()
            print(f"[PS Launch Error] {err}")
            return False
        return True
    except Exception as e:
        print(f"[PS Launch Exception] {e}")
        return False


def _ps_launch_uri(uri: str) -> bool:
    """Launch a URI/protocol handler via PowerShell Start-Process (e.g. whatsapp:)."""
    try:
        safe_uri = uri.replace("'", "''")
        cmd = ["powershell", "-WindowStyle", "Hidden", "-Command",
               f"Start-Process '{safe_uri}'"]
        subprocess.run(cmd, capture_output=True, timeout=10)
        return True
    except Exception as e:
        print(f"[PS URI Launch Exception] {e}")
        return False


def _ps_launch_url(url: str) -> bool:
    """Open a URL in the default browser via PowerShell Start-Process."""
    try:
        safe_url = url.replace("'", "''")
        cmd = ["powershell", "-WindowStyle", "Hidden", "-Command",
               f"Start-Process '{safe_url}'"]
        subprocess.run(cmd, capture_output=True, timeout=10)
        return True
    except Exception as e:
        print(f"[PS URL Launch Exception] {e}")
        return False


class WindowsExecutor:
    # ── Comprehensive application discovery map ─────────────────────
    APP_MAP = {
        "whatsapp": [
            {"type": "exe", "path": r"C:\Users\{user}\AppData\Local\WhatsApp\WhatsApp.exe"},
            {"type": "exe", "path": r"C:\Users\{user}\AppData\Local\Programs\WhatsApp\WhatsApp.exe"},
            {"type": "uri", "path": "whatsapp:"},
            {"type": "url", "path": "https://web.whatsapp.com"},
        ],
        "chrome": [
            {"type": "exe", "path": r"C:\Program Files\Google\Chrome\Application\chrome.exe"},
            {"type": "exe", "path": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"},
            {"type": "exe", "path": r"C:\Users\{user}\AppData\Local\Google\Chrome\Application\chrome.exe"},
            {"type": "exe", "path": "chrome.exe"},
        ],
        "youtube":    [{"type": "url", "path": "https://www.youtube.com"}],
        "google":     [{"type": "url", "path": "https://www.google.com"}],
        "chatgpt":    [{"type": "url", "path": "https://chatgpt.com"}],
        "edge": [
            {"type": "exe", "path": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"},
            {"type": "exe", "path": r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"},
            {"type": "exe", "path": "msedge.exe"},
        ],
        "firefox": [
            {"type": "exe", "path": r"C:\Program Files\Mozilla Firefox\firefox.exe"},
            {"type": "exe", "path": r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"},
            {"type": "exe", "path": "firefox.exe"},
        ],
        "code": [
            {"type": "exe", "path": r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe"},
            {"type": "exe", "path": r"C:\Program Files\Microsoft VS Code\Code.exe"},
            {"type": "exe", "path": "code.exe"},
        ],
        "vs code": [
            {"type": "exe", "path": r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe"},
            {"type": "exe", "path": r"C:\Program Files\Microsoft VS Code\Code.exe"},
            {"type": "exe", "path": "code.exe"},
        ],
        "cursor": [
            {"type": "exe", "path": r"C:\Users\{user}\AppData\Local\Programs\cursor\Cursor.exe"},
            {"type": "exe", "path": "cursor.exe"},
        ],
        "notepad":    [{"type": "exe", "path": "notepad.exe"}],
        "calculator": [
            {"type": "shell", "path": "shell:AppsFolder\\Microsoft.WindowsCalculator_8wekyb3d8bbwe!App"},
            {"type": "exe", "path": "calc.exe"},
        ],
        "paint":      [{"type": "exe", "path": "mspaint.exe"}],
        "terminal":   [{"type": "exe", "path": "wt.exe"}, {"type": "exe", "path": "powershell.exe"}],
        "powershell": [{"type": "exe", "path": "powershell.exe"}],
        "cmd":        [{"type": "exe", "path": "cmd.exe"}],
        "explorer":   [{"type": "exe", "path": "explorer.exe"}],
        "spotify": [
            {"type": "exe", "path": r"C:\Users\{user}\AppData\Roaming\Spotify\Spotify.exe"},
            {"type": "uri", "path": "spotify:"},
            {"type": "url", "path": "https://open.spotify.com"},
        ],
    }

    # ── Process name map for verification ───────────────────────────
    PROCESS_NAME_MAP = {
        "notepad":    ["notepad.exe"],
        "chrome":     ["chrome.exe"],
        "edge":       ["msedge.exe"],
        "code":       ["code.exe"],
        "vs code":    ["code.exe"],
        "cursor":     ["cursor.exe"],
        "whatsapp":   ["whatsapp.exe", "whatsapp.root.exe"],
        "spotify":    ["spotify.exe"],
        "terminal":   ["wt.exe", "windowsterminal.exe"],
        "powershell": ["powershell.exe"],
        "cmd":        ["cmd.exe"],
        "explorer":   ["explorer.exe"],
        "firefox":    ["firefox.exe"],
        "calculator": ["applicationframehost.exe", "calculator.exe"],
    }

    def execute(self, action: str, target: str = None) -> dict:
        if os.name != 'nt':
            return {
                'success': False,
                'message': f"Windows desktop action '{action}' is unavailable in this web deployment.",
                'fix': 'Run the SANDEEP local Windows agent for desktop control.'
            }
        method = getattr(self, action, None)
        if method:
            return method(target)
        return {"success": False, "message": f"Unknown action: {action}"}

    def _verify_app_running(self, app_key: str, wait_time: float = 5.0) -> bool:
        """Wait up to wait_time seconds for the process to appear and ensure it's not in Session 0."""
        if not PSUTIL_AVAILABLE:
            return True

        check_names = self.PROCESS_NAME_MAP.get(app_key, [app_key, f"{app_key}.exe"])
        print(f"[VERIFY] Waiting for '{app_key}' process (checking: {check_names})...")

        start = time.time()
        while time.time() - start < wait_time:
            for proc in psutil.process_iter(["name", "pid"]):
                try:
                    name = (proc.info.get("name") or "").lower()
                    if any(check.lower() in name for check in check_names):
                        pid = proc.info.get("pid")
                        
                        # Check Session ID
                        session_id = ctypes.c_uint32()
                        if ctypes.windll.kernel32.ProcessIdToSessionId(pid, ctypes.byref(session_id)):
                            sid = session_id.value
                            print(f"[VERIFY] Process detected: {name} (PID: {pid}, Session: {sid})")
                            if sid == 0:
                                print("[VERIFY ERROR] App launched in Session 0 (Invisible Service Session).")
                                # It's running but invisible, consider it a failure for UI purposes
                                return False
                        else:
                            print(f"[VERIFY] Process detected: {name}")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            time.sleep(0.4)

        print(f"[VERIFY] Process NOT detected after {wait_time}s")
        return False

    # ── Application Control ─────────────────────────────────────────
    def open_app(self, app_name: str) -> dict:
        if not app_name:
            return {"success": False, "message": "No application name provided."}

        app_key = app_name.lower().strip()
        print(f"\n[WINDOWS] Launching: {app_name}")
        user = os.environ.get("USERNAME", "boysa")

        candidates = self.APP_MAP.get(app_key, [])

        # Alias resolution
        aliases = {
            "vs code": "code", "vscode": "code", "visual studio code": "code",
            "whats app": "whatsapp", "what's app": "whatsapp",
            "google chrome": "chrome",
            "command prompt": "cmd", "file explorer": "explorer",
            "file manager": "explorer",
        }
        if not candidates and app_key in aliases:
            candidates = self.APP_MAP.get(aliases[app_key], [])

        # Generic fallback
        if not candidates:
            candidates = [
                {"type": "exe", "path": f"{app_name}.exe"},
                {"type": "exe", "path": app_name},
            ]

        launched = False
        for entry in candidates:
            ctype = entry.get("type", "exe")
            path = entry.get("path", "").replace("{user}", user)

            try:
                if ctype == "url":
                    print(f"[AGENT] Opening URL: {path}")
                    if _ps_launch_url(path):
                        launched = True
                        break

                elif ctype == "uri":
                    print(f"[AGENT] Opening URI: {path}")
                    if _ps_launch_uri(path):
                        launched = True
                        break

                elif ctype == "shell":
                    # Windows Store / UWP apps via shell: URI
                    print(f"[AGENT] Start-Process (shell): {path}")
                    if _ps_launch_uri(f"shell:{path.replace('shell:', '')}"):
                        launched = True
                        break

                elif ctype == "exe":
                    if os.path.isabs(path) and not os.path.exists(path):
                        continue
                    print(f"[AGENT] Start-Process: {path}")
                    if _ps_launch(path):
                        launched = True
                        break

            except Exception as e:
                print(f"[AGENT Error] candidate={path}: {e}")
                continue

        # Fallback: search Start Menu shortcuts
        if not launched:
            print("[AGENT] Trying Start Menu search...")
            res = self._search_and_launch(app_name)
            if res.get("success"):
                launched = True

        if not launched:
            print("[RESULT] FAILED TO LAUNCH")
            return {
                "success": False, 
                "message": f"Could not find or open '{app_name}'. Application not installed or not found.",
                "fix": f"Install {app_name} or add its path to WindowsExecutor.APP_MAP."
            }

        # Web-only apps have no local process to verify
        if candidates and all(e.get("type") == "url" for e in candidates):
            print("[RESULT] SUCCESS (web app)")
            return {"success": True, "message": f"Opened {app_name} in browser."}

        if self._verify_app_running(app_key):
            print("[RESULT] SUCCESS")
            return {"success": True, "message": f"Opened {app_name}."}

        web_fallback_keys = {"youtube", "google", "chatgpt", "whatsapp"}
        if app_key in web_fallback_keys:
            print("[RESULT] SUCCESS (web fallback assumed)")
            return {"success": True, "message": f"Opened {app_name}."}

        print("[RESULT] VERIFICATION FAILED - Process not detected")
        return {
            "success": False, 
            "message": f"Launched {app_name} but could not verify it opened. Try checking your desktop.",
            "fix": "Ensure the application runs visibly and isn't blocked by Windows permissions."
        }

    def _search_and_launch(self, app_name: str) -> dict:
        """Fallback: search Start Menu shortcuts."""
        search_dirs = [
            os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs"),
        ]
        for d in search_dirs:
            for lnk in glob.glob(os.path.join(d, "**", "*.lnk"), recursive=True):
                if app_name.lower() in os.path.basename(lnk).lower():
                    try:
                        print(f"[AGENT] Start Menu shortcut: {lnk}")
                        _ps_launch(lnk)
                        return {"success": True, "message": f"Opened {app_name} from Start Menu."}
                    except Exception:
                        continue
        return {"success": False, "message": f"Could not find '{app_name}'. Application not found."}

    def close_app(self, app_name: str) -> dict:
        if not app_name:
            return {"success": False, "message": "No application name provided."}

        print(f"\n[WINDOWS] Closing: {app_name}")
        app_key = app_name.lower().strip()
        check_names = self.PROCESS_NAME_MAP.get(app_key, [app_key, f"{app_key}.exe"])

        if not PSUTIL_AVAILABLE:
            exe = check_names[0].replace(".exe", "")
            try:
                subprocess.run(["powershell", "-Command", f"Stop-Process -Name '{exe}' -Force -ErrorAction SilentlyContinue"],
                               capture_output=True, timeout=10)
                return {"success": True, "message": f"Closed {app_name}."}
            except Exception as e:
                return {"success": False, "message": f"Failed to close {app_name}: {e}"}

        count = 0
        for proc in psutil.process_iter(["name", "pid"]):
            try:
                pname = (proc.info.get("name") or "").lower()
                if any(check.lower() in pname for check in check_names):
                    print(f"[AGENT] Killing PID {proc.pid} ({pname})")
                    proc.kill()
                    count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        print(f"[VERIFY] Checking if '{app_name}' is closed...")
        time.sleep(1.2)
        still_running = any(
            any(check.lower() in (proc.info.get("name") or "").lower() for check in check_names)
            for proc in psutil.process_iter(["name"])
        )

        if still_running:
            print("[RESULT] VERIFICATION FAILED - Still running")
            return {
                "success": False, 
                "message": f"Failed to close {app_name}. It may still be running.",
                "fix": "Close the application manually or run SANDEEP as Administrator."
            }

        if count > 0:
            print("[RESULT] SUCCESS")
            return {"success": True, "message": f"Closed {app_name} ({count} process(es) terminated)."}

        print("[RESULT] FAILED - Not found")
        return {
            "success": False, 
            "message": f"'{app_name}' was not running.",
            "fix": "No action needed, the application is already closed."
        }

    # ── Volume Control ───────────────────────────────────────────────
    def volume_up(self, _=None) -> dict:
        """Increase system volume by pressing Volume Up key."""
        try:
            import subprocess
            # Use PowerShell to simulate VolumeUp key press 5 times
            ps_cmd = (
                "$wshell = New-Object -com 'Wscript.Shell'; "
                "for ($i=0; $i -lt 5; $i++) { $wshell.SendKeys([char]175) }"  # 175 = VolumeUp
            )
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, timeout=5)
            print("[WINDOWS] Volume increased")
            return {"success": True, "message": "Volume badh gayi!"}
        except Exception as e:
            return {"success": False, "message": f"Volume control failed: {e}"}

    def volume_down(self, _=None) -> dict:
        """Decrease system volume by pressing Volume Down key."""
        try:
            import subprocess
            ps_cmd = (
                "$wshell = New-Object -com 'Wscript.Shell'; "
                "for ($i=0; $i -lt 5; $i++) { $wshell.SendKeys([char]174) }"  # 174 = VolumeDown
            )
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, timeout=5)
            print("[WINDOWS] Volume decreased")
            return {"success": True, "message": "Volume kam ho gayi!"}
        except Exception as e:
            return {"success": False, "message": f"Volume control failed: {e}"}

    def volume_mute(self, _=None) -> dict:
        """Toggle system mute."""
        try:
            import subprocess
            ps_cmd = (
                "$wshell = New-Object -com 'Wscript.Shell'; "
                "$wshell.SendKeys([char]173)"  # 173 = VolumeMute
            )
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, timeout=5)
            print("[WINDOWS] Volume toggled mute")
            return {"success": True, "message": "Volume mute toggle ho gayi!"}
        except Exception as e:
            return {"success": False, "message": f"Volume mute failed: {e}"}

    # ── System Information ──────────────────────────────────────────
    def get_time(self, _=None) -> dict:
        now = datetime.datetime.now()
        return {"success": True, "message": f"Abhi {now.strftime('%I:%M %p')} ho rahe hain. Date: {now.strftime('%A, %d %B %Y')}."}

    def get_system_status(self, _=None) -> dict:
        if not PSUTIL_AVAILABLE:
            return {"success": False, "message": "psutil not installed."}
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\")
        battery = psutil.sensors_battery()
        batt_str = f"Battery: {battery.percent}%" if battery else "Battery: N/A (desktop)"

        running = []
        for proc in psutil.process_iter(["name"]):
            try:
                n = proc.info["name"]
                if n and n not in running and not n.startswith("svchost"):
                    running.append(n)
            except Exception:
                pass

        top_apps = [a for a in running if any(k in a.lower() for k in [
            "chrome", "code", "whatsapp", "edge", "firefox", "notepad",
            "explorer", "terminal", "cursor", "spotify"
        ])]

        return {
            "success": True,
            "message": (
                f"CPU: {cpu}% | RAM: {mem.percent}% ({mem.used // (1024**3)}GB / {mem.total // (1024**3)}GB) | "
                f"Disk C: {disk.percent}% used | {batt_str} | "
                f"Notable apps running: {', '.join(top_apps[:8]) if top_apps else 'None detected'}"
            )
        }

    # ── Wallpaper ───────────────────────────────────────────────────
    def change_wallpaper(self, path: str = None) -> dict:
        if not path:
            candidates = [
                r"C:\Windows\Web\Wallpaper\Windows\img0.jpg",
                r"C:\Windows\Web\Wallpaper\Theme1\img1.jpg",
                r"C:\Windows\Web\Wallpaper\Theme1\img2.jpg",
            ]
            for c in candidates:
                if os.path.exists(c):
                    path = c
                    break
        if path and os.path.exists(path):
            SPI_SETDESKWALLPAPER = 20
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3)
            return {"success": True, "message": f"Wallpaper changed to {os.path.basename(path)}."}
        return {"success": False, "message": "No wallpaper image found."}
