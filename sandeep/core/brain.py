"""
SANDEEP AI Brain — Modular AI Provider Layer
Uses litellm for provider abstraction (Gemini, OpenAI, local models).
Falls back to a simple rule-based engine if no API key is set.
"""
import os
import json
import re

# Only import litellm if available
try:
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False


class AIBrain:
    def __init__(self, model: str = "gemini/gemini-2.0-flash"):
        self.model = model
        self.has_api = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY"))

    def generate_response(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        if LITELLM_AVAILABLE and self.has_api:
            return self._llm_response(prompt, system_prompt, temperature)
        return self._fallback_response(prompt)

    def extract_json(self, prompt: str, system_prompt: str = None) -> str:
        if LITELLM_AVAILABLE and self.has_api:
            return self._llm_json(prompt, system_prompt)
        return self._fallback_plan(prompt)

    # ── LLM-backed methods ──────────────────────────────────────────
    def _llm_response(self, prompt, system_prompt, temperature):
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        msgs.append({"role": "user", "content": prompt})
        try:
            r = completion(model=self.model, messages=msgs, temperature=temperature)
            return r.choices[0].message.content
        except Exception as e:
            print(f"[Brain LLM Error]: {e}")
            return self._fallback_response(prompt)

    def _llm_json(self, prompt, system_prompt):
        sys_msg = (system_prompt or "You are SANDEEP, a Jarvis-style AI.") + "\nAlways respond with valid JSON only."
        try:
            r = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            return r.choices[0].message.content
        except Exception as e:
            print(f"[Brain JSON Error]: {e}")
            return self._fallback_plan(prompt)

    # ── Offline fallback -- rule-based intent mapping ────────────────
    def _fallback_response(self, prompt: str) -> str:
        p = prompt.lower().strip()
        if re.search(r'\b(hello|hey|namaste|bro)\b', p) or re.match(r'^hi\b', p):
            return "Hello, Sandeep. Main ready hoon, bolo kya karna hai?"
        if any(w in p for w in ["time", "samay", "waqt", "baje"]):
            import datetime
            return f"Abhi {datetime.datetime.now().strftime('%I:%M %p')} ho rahe hain."
        if any(w in p for w in ["day", "din", "date", "tarikh"]):
            import datetime
            return f"Aaj {datetime.datetime.now().strftime('%A, %d %B %Y')} hai."
        if any(w in p for w in ["kya kar", "kaise ho", "kya chal", "kaisa hai"]):
            return "Main bilkul ready hoon, Sandeep. Aapke next command ka wait kar raha hoon."
        if any(w in p for w in ["kaun ho", "who are", "what are"]):
            return "Main SANDEEP hoon, aapka personal AI assistant. Aapke computer ko control karne ke liye ready hoon."
        return "Main aapki baat samajh gaya. Batao kya karna hai?"

    def _fallback_plan(self, prompt: str) -> str:
        p = prompt.lower().strip()
        plan = []

        # ── Normalize Hinglish/Urdu to English ─────────────────────
        hinglish_map = [
            ("kholo", "open"), ("khol do", "open"), ("khulao", "open"),
            ("chalu karo", "open"), ("shuru karo", "open"),
            ("open karo", "open"), ("open kero", "open"),
            ("band karo", "close"), ("band kero", "close"), ("band kar", "close"),
            ("band kerna", "close"), ("hatao", "close"), ("rok do", "close"),
            ("dhundo", "search"), ("dhundho", "search"), ("search karo", "search"),
            ("search kero", "search"), ("talash karo", "search"),
            ("volume badho", "volume up"), ("awaz badho", "volume up"), ("tez karo", "volume up"),
            ("volume ghato", "volume down"), ("awaz ghato", "volume down"),
            ("mute karo", "mute"), ("chup karo", "mute"), ("awaaz band", "mute"),
            ("screenshot lo", "screenshot"), ("screenshot le", "screenshot"),
            ("wallpaper badlo", "change wallpaper"), ("background badlo", "change wallpaper"),
            ("waqt batao", "time"), ("samay batao", "time"),
            ("tarikh batao", "date"), ("aaj ki tarikh", "date"),
            ("c drive kholo", "open c drive"), ("d drive kholo", "open d drive"),
            ("folder banao", "create folder"), ("naya folder", "create folder"),
            ("banao", "create"), ("delete karo", "delete"), ("rename karo", "rename"),
            ("copy karo", "copy"), ("move karo", "move"),
            ("karo", ""), ("kero", ""), (" kar", ""), ("please", ""),
        ]
        for hindi, english in hinglish_map:
            p = p.replace(hindi, english)
        p = " ".join(p.split())

        is_close = any(k in p for k in ["close", "quit", "exit", "band"])

        # ── App map ─────────────────────────────────────────────────
        app_map = {
            "whatsapp": "whatsapp", "whatsap": "whatsapp", "whats app": "whatsapp",
            "watsap": "whatsapp",
            "chrome": "chrome", "google chrome": "chrome",
            "youtube": "youtube", "you tube": "youtube", "yt": "youtube",
            "edge": "edge", "microsoft edge": "edge",
            "firefox": "firefox",
            "vs code": "code", "vscode": "code", "visual studio code": "code",
            "visual studio": "code",
            "cursor": "cursor",
            "notepad": "notepad", "note pad": "notepad",
            "calculator": "calculator", "calc": "calculator", "hisab": "calculator",
            "terminal": "terminal", "windows terminal": "terminal",
            "powershell": "powershell",
            "cmd": "cmd", "command prompt": "cmd",
            "explorer": "explorer", "file explorer": "explorer",
            "this pc": "explorer", "my computer": "explorer",
            "spotify": "spotify",
            "chatgpt": "chatgpt", "chat gpt": "chatgpt", "openai": "chatgpt",
            "google": "google",
            "paint": "paint", "ms paint": "paint",
            "word": "word", "ms word": "word",
            "excel": "excel", "ms excel": "excel",
            "powerpoint": "powerpoint", "ppt": "powerpoint",
            "discord": "discord", "telegram": "telegram", "slack": "slack",
        }

        # Multi-step splitting by " aur ", " and ", ","
        # To keep it simple, we will just parse primary intent for fallback, 
        # or split by comma for multiple.
        steps_text = re.split(r',| aur | and | then ', p)
        
        step_idx = 1
        for stext in steps_text:
            stext = stext.strip()
            if not stext: continue
            
            added = False
            
            # File ops (create folder)
            if "create folder" in stext or "folder create" in stext:
                # Naive extract: 'create folder project'
                words = [w for w in stext.replace("create folder", "").replace("folder create", "").split() if len(w) > 2]
                fname = words[0].capitalize() if words else "NewFolder"
                plan.append({"step": step_idx, "action": "create_folder", "target": f"C:\\{fname}", "description": f"Create folder {fname}"})
                step_idx += 1
                added = True
                continue

            # Drive open
            dm = re.search(r'(?:open\s+)?([a-z])\s*drive', stext)
            if dm:
                plan.append({"step": step_idx, "action": "open_drive", "target": dm.group(1).upper(), "description": f"Open {dm.group(1).upper()} drive"})
                step_idx += 1
                added = True
                continue

            # System info
            if any(w in stext for w in ["time", "clock", "samay", "waqt"]):
                plan.append({"step": step_idx, "action": "get_time", "target": None, "description": "Get current time"})
                step_idx += 1
                added = True; continue
            elif any(w in stext for w in ["battery", "cpu", "ram", "storage", "apps"]):
                plan.append({"step": step_idx, "action": "get_system_info", "target": stext, "description": "Get system info"})
                step_idx += 1
                added = True; continue
            elif any(w in stext for w in ["system status", "status", "health"]):
                plan.append({"step": step_idx, "action": "get_system_status", "target": None, "description": "Get system status"})
                step_idx += 1
                added = True; continue

            # Browser Search
            if "search" in stext or "google" in stext:
                query = stext
                for rem in ["search", "find", "google", "on", "par", "ke liye", "open"]:
                    query = query.replace(rem, "").strip()
                if query:
                    plan.append({"step": step_idx, "action": "browser_search", "target": query, "description": f"Search: {query}"})
                    step_idx += 1
                    added = True
                    continue

            # App open/close
            for name, target in app_map.items():
                if name in stext:
                    action = "close_app" if is_close else "open_app"
                    plan.append({"step": step_idx, "action": action, "target": target, "description": f"{action} {target}"})
                    step_idx += 1
                    added = True
                    break

        return json.dumps({"plan": plan})
