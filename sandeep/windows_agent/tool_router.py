from .agent import WindowsAgent


class ToolRouter:
    """Routes commands from the AI/CLI to the WindowsAgent."""

    def __init__(self):
        self.agent = WindowsAgent()

    def route(self, command: dict) -> dict:
        """command: {action: str, target: str, args: {}}
        returns execution result dict
        """
        action = command.get("action")
        target = command.get("target")
        args = command.get("args", {})
        return self.agent.execute(action, target, args)
