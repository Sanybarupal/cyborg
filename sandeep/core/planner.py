"""
SANDEEP Task Planner — breaks natural language into executable steps.
"""
import json
from .brain import AIBrain

PLANNER_SYSTEM_PROMPT = """You are SANDEEP's task planner. Break down a natural language command into executable steps.
Available actions:
- open_app (target: app name like whatsapp, chrome, code, notepad, calculator, terminal, etc.)
- close_app (target: app name)
- open_drive (target: drive letter like C, D, E)
- open_folder (target: full folder path)
- create_folder (target: full folder path)
- delete_file (target: full file/folder path)
- open_file (target: full file path)
- rename_file (target: current path, destination: new path)
- copy_file (target: source path, destination: target path)
- move_file (target: source path, destination: target path)
- get_time
- get_system_status
- get_system_info (target: CPU, RAM, storage, open apps)
- change_wallpaper
- browser_search (target: search query)
- browser_open (target: URL)
- browser_action (target: new_tab, get_title)
- ocr_screen (target: text to find, if any)
- capture_screenshot
- terminal_execute (target: command string)
- whatsapp_send (target: contact_name, message: text)
- whatsapp_read (target: contact_name)

Respond with ONLY a JSON object:
{"plan": [{"step": 1, "action": "whatsapp_send", "target": "Mummy", "message": "I am fine", "description": "Send WhatsApp message"}]}
If the command requires multiple steps, list them in order.
If the command is just conversation (greeting, question), return: {"plan": []}
"""


class TaskPlanner:
    def __init__(self, brain: AIBrain):
        self.brain = brain

    def create_plan(self, command: str) -> list:
        raw = self.brain.extract_json(command, PLANNER_SYSTEM_PROMPT)
        try:
            # Strip markdown fences if present
            clean = raw.strip()
            if clean.startswith("```"):
                clean = "\n".join(clean.split("\n")[1:])
            if clean.endswith("```"):
                clean = "\n".join(clean.split("\n")[:-1])
            data = json.loads(clean.strip())
            return data.get("plan", [])
        except json.JSONDecodeError:
            print(f"[Planner] Failed to decode JSON: {raw[:200]}")
            return []
