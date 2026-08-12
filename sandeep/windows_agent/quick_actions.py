from .tool_router import ToolRouter


class QuickActions:
    """Defines quick actions and executes them through the tool router."""

    DEFAULTS = [
        {"name": "Open WhatsApp", "action": "open_application", "target": "WhatsApp.exe"},
        {"name": "Open YouTube", "action": "open_application", "target": "chrome", "args": {"url": "https://youtube.com"}},
        {"name": "Open Chrome", "action": "open_application", "target": "chrome"},
        {"name": "Open Notepad", "action": "open_application", "target": "notepad"},
        {"name": "Open VS Code", "action": "open_application", "target": "code"},
        {"name": "System Status", "action": "system_status", "target": None},
    ]

    def __init__(self, router: ToolRouter = None):
        self.router = router or ToolRouter()

    def list_actions(self):
        return self.DEFAULTS

    def run(self, idx: int):
        if idx < 0 or idx >= len(self.DEFAULTS):
            return {"ok": False, "error": "invalid quick action index"}
        cmd = self.DEFAULTS[idx]
        return self.router.route({"action": cmd["action"], "target": cmd.get("target"), "args": cmd.get("args", {})})
