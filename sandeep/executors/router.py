"""
SANDEEP Tool Router — Central hub that routes planned tasks to the correct executor.
"""
from .windows import WindowsExecutor
from .files import FileExecutor
from .vision import VisionExecutor


class ToolRouter:
    WINDOWS_ACTIONS = {"open_app", "close_app", "get_time", "get_system_status",
                       "change_wallpaper", "volume_up", "volume_down", "volume_mute"}
    FILE_ACTIONS = {"open_drive", "open_folder", "create_folder", "delete_file", "search_file"}
    VISION_ACTIONS = {"ocr_screen", "capture_screenshot"}

    def __init__(self):
        self.windows = WindowsExecutor()
        self.files = FileExecutor()
        self.vision = VisionExecutor()

    def execute_step(self, step: dict) -> dict:
        action = step.get("action", "")
        target = step.get("target")
        desc = step.get("description", action)

        print(f"  [Router] Step {step.get('step', '?')}: {desc} (action={action}, target={target})")

        try:
            if action in self.WINDOWS_ACTIONS:
                result = self.windows.execute(action, target)
                module = "WINDOWS AGENT"
            elif action in self.FILE_ACTIONS:
                result = self.files.execute(action, target)
                module = "FILE SYSTEM"
            elif action in self.VISION_ACTIONS:
                result = self.vision.execute(action, target)
                module = "SCREEN/OCR"
            elif action == "browser_search":
                result = self._browser_search(target)
                module = "BROWSER"
            elif action == "browser_open":
                result = self._browser_open(target)
                module = "BROWSER"
            elif action == "terminal_execute":
                result = self._terminal_execute(target)
                module = "TERMINAL"
            else:
                result = {"success": False, "message": f"No executor found for action: {action}"}
                module = "TOOL ROUTER"
                
            if not result.get("success"):
                result["module"] = result.get("module", module)
                result["fix"] = result.get("fix", f"Check {module} configuration or logs.")
                
        except Exception as e:
            result = {
                "success": False,
                "message": f"Unexpected execution error: {str(e)}",
                "module": "TOOL ROUTER",
                "fix": "Check backend server logs for exceptions."
            }

        print(f"  [Router] Result: {result.get('message', 'N/A')}")
        return result

    def execute_plan(self, plan: list) -> list:
        results = []
        for step in plan:
            result = self.execute_step(step)
            results.append({
                "step": step.get("step", "?"),
                "action": step.get("action", ""),
                "description": step.get("description", ""),
                **result
            })
            # If a step fails critically, continue but note it
            if not result.get("success"):
                print(f"  [Router] Step {step.get('step')} failed, continuing...")
        return results

    # ── Browser — uses PowerShell Start-Process for visible window ──
    def _browser_search(self, query: str) -> dict:
        import subprocess
        if not query:
            return {"success": False, "message": "No search query provided."}
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        try:
            safe_url = url.replace("'", "''")
            subprocess.run(
                ["powershell", "-WindowStyle", "Hidden", "-Command", f"Start-Process '{safe_url}'"],
                capture_output=True, timeout=10
            )
            return {"success": True, "message": f"Searching Google for '{query}'."}
        except Exception as e:
            return {"success": False, "message": f"Browser search failed: {e}"}

    def _browser_open(self, url: str) -> dict:
        import subprocess
        if not url:
            return {"success": False, "message": "No URL provided."}
        if not url.startswith("http"):
            url = "https://" + url
        try:
            safe_url = url.replace("'", "''")
            subprocess.run(
                ["powershell", "-WindowStyle", "Hidden", "-Command", f"Start-Process '{safe_url}'"],
                capture_output=True, timeout=10
            )
            return {"success": True, "message": f"Opened {url} in browser."}
        except Exception as e:
            return {"success": False, "message": f"Failed to open URL: {e}"}

    def _terminal_execute(self, command: str) -> dict:
        # Terminal execution is intentionally disabled until an authenticated,
        # allowlisted command broker is provided. Never pass user input to a shell.
        if command:
            return {
                "success": False,
                "message": "Terminal execution is disabled for safety.",
                "fix": "Use an authenticated allowlisted command broker.",
            }
        return {"success": False, "message": "No command provided."}
