import os
import subprocess
import time
from .executor import open_application, open_path, change_wallpaper, get_system_status, verify_process_running


class WindowsAgent:
    """Responsible for executing real Windows actions and verifying results."""

    def __init__(self):
        self.connected = True

    def execute(self, tool: str, target: str = None, args: dict = None) -> dict:
        args = args or {}
        result = {"tool": tool, "target": target, "ok": False, "error": None}
        try:
            if tool == "open_application":
                pid = open_application(target, args)
                result.update({"ok": True, "pid": pid})
                # verify
                time.sleep(0.5)
                result["verified"] = verify_process_running(pid) if pid else False
            elif tool == "open_path":
                ok = open_path(target)
                result.update({"ok": ok, "verified": ok})
            elif tool == "change_wallpaper":
                ok = change_wallpaper(target)
                result.update({"ok": ok, "verified": ok})
            elif tool == "system_status":
                status = get_system_status()
                result.update({"ok": True, "status": status})
            else:
                result.update({"error": f"Unknown tool: {tool}"})
        except Exception as e:
            result.update({"error": str(e)})
        return result
