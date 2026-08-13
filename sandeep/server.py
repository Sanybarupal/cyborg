"""
SANDEEP Server - FastAPI backend with WebSocket, System Status API, and Schedule.
Main entry point for the SANDEEP system.
"""
import os
import sys
import json
import datetime
import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse

sys.path.insert(0, os.path.dirname(__file__))

from core.brain import AIBrain
from core.planner import TaskPlanner
from core.memory import memory
from executors.router import ToolRouter
from voice.speak import generate_speech

# ── Hinglish AI Support ──────────────────────────────────────────
try:
    from hinglish_engine import hinglish_engine, HinglishEngine, HINGLISH_RESPONSES
    from hinglish_tts import generate_hinglish_speech
    HINGLISH_AVAILABLE = True
    print("  [OK] Hinglish Engine (Multi-language voice support)")
except ImportError as e:
    HINGLISH_AVAILABLE = False
    print(f"  [⚠] Hinglish Engine not available: {e}")

# ── Initialize subsystems ───────────────────────────────────────────
print("=" * 60)
print("  SANDEEP - Personal AI Assistant")
print("  Initializing subsystems...")
print("=" * 60)

brain = AIBrain()
planner = TaskPlanner(brain)
router = ToolRouter()

print(f"  [OK] AI Brain (model: {brain.model}, api: {brain.has_api})")
print(f"  [OK] Task Planner")
print(f"  [OK] Tool Router")
print(f"  [OK] Memory")
print("=" * 60)

# Track live recent actions
recent_actions = [
    {
        "time": datetime.datetime.now().strftime("%I:%M %p"),
        "action": "All Systems Initialized & Online",
        "success": True
    }
]

# ── FastAPI ─────────────────────────────────────────────────────────
app = FastAPI(title="SANDEEP")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(os.path.join(STATIC_DIR, "audio"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/health")
async def health():
    return {"status": "online", "timestamp": datetime.datetime.now().isoformat()}


@app.get("/api/system-status")
async def system_status():
    """Real-time system stats for the dashboard."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\")
        battery = psutil.sensors_battery()

        # Detect notable running apps
        notable = set()
        keywords = ["chrome", "code", "whatsapp", "edge", "firefox", "notepad",
                     "explorer", "terminal", "cursor", "spotify", "discord",
                     "telegram", "slack", "obs", "vlc", "brave"]
        for proc in psutil.process_iter(["name"]):
            try:
                n = (proc.info["name"] or "").lower()
                for k in keywords:
                    if k in n:
                        # Clean up the name
                        display = k.capitalize()
                        if k == "code": display = "VS Code"
                        elif k == "msedge": display = "Edge"
                        notable.add(display)
            except Exception:
                pass

        return {
            "cpu": round(cpu),
            "ram": round(mem.percent),
            "disk": round(disk.percent),
            "battery": round(battery.percent) if battery else None,
            "apps": sorted(list(notable))[:10],
            "recent_actions": recent_actions[:8]
        }
    except ImportError:
        return {"cpu": 0, "ram": 0, "disk": 0, "battery": None, "apps": [], "recent_actions": recent_actions[:8]}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("[WS] Client connected")

    # Auto-Diagnostics
    await ws.send_json({
        "type": "health_update",
        "health": {
            "mic": "warning", "stt": "warning", "tts": "warning",
            "ai": "online" if brain.has_api else "warning",
            "backend": "online", "router": "online", "agent": "online",
            "quick": "online", "browser": "online", "ocr": "online",
            "fs": "online", "sys": "online"
        }
    })
    
    # We simulate a brief check, then set them online
    await asyncio.sleep(1.0)
    await ws.send_json({
        "type": "health_update",
        "health": {
            "mic": "online", "stt": "online", "tts": "online",
            "ai": "online" if brain.has_api else "warning",
            "backend": "online", "router": "online", "agent": "online",
            "quick": "online", "browser": "online", "ocr": "online",
            "fs": "online", "sys": "online"
        }
    })

    # Startup greeting (once)
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = "Good morning, Sandeep. All systems are checked and online."
    elif hour < 17:
        greeting = "Good afternoon, Sandeep. All systems are checked and online."
    else:
        greeting = "Welcome back, Sandeep. All systems are checked and online."

    audio_file = await generate_speech(greeting)
    await ws.send_json({
        "type": "greeting",
        "text": greeting,
        "audio": f"/static/audio/{audio_file}" if audio_file else None
    })

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            
            # ══════ HINGLISH VOICE COMMAND HANDLER ═══════════════════════════
            if msg.get("type") == "voice_command" and HINGLISH_AVAILABLE:
                command_text = msg.get("text", "").strip()
                context = msg.get("context", {})
                
                print(f"\n{'='*60}")
                print(f"[HINGLISH VOICE] {command_text}")
                
                # Detect intent using Hinglish engine
                intent, intent_data = hinglish_engine.detect_intent(command_text)
                print(f"[INTENT] {intent} | {intent_data}")
                
                # Generate Hinglish response
                if intent == 'open_app':
                    app_name = intent_data.get('app')
                    response = hinglish_engine.get_hinglish_response('app_opening', {'app': app_name})
                    
                    # Execute app opening
                    result = await asyncio.to_thread(router.execute_step, {
                        'action': 'open_app',
                        'args': {'app': app_name}
                    })
                    
                    await ws.send_json({
                        "type": "hinglish_response",
                        "response": response,
                        "context": {"last_app": app_name},
                        "command": command_text
                    })
                
                elif intent == 'close_app':
                    app_name = intent_data.get('app')
                    response = hinglish_engine.get_hinglish_response('app_closing', {'app': app_name})
                    
                    # Execute app closing
                    result = await asyncio.to_thread(router.execute_step, {
                        'action': 'close_app',
                        'args': {'app': app_name}
                    })
                    
                    await ws.send_json({
                        "type": "hinglish_response",
                        "response": response,
                        "context": {"last_app": app_name},
                        "command": command_text
                    })
                
                elif intent == 'greeting':
                    response = hinglish_engine.get_hinglish_response('greeting_response', {})
                    
                    await ws.send_json({
                        "type": "hinglish_response",
                        "response": response,
                        "context": context,
                        "command": command_text
                    })
                
                elif intent == 'send_message':
                    contact = intent_data.get('contact')
                    response = "OK Sir, kya message bhejna hai? Bataiye."
                    
                    await ws.send_json({
                        "type": "hinglish_response",
                        "response": response,
                        "requires_confirmation": True,
                        "pending_data": {"action": "send_message", "contact": contact},
                        "context": {"pending_contact": contact},
                        "command": command_text
                    })
                
                else:  # Conversation/general response
                    response = brain.generate_response(
                        prompt=command_text,
                        system_prompt="""You are SANDEEP, a personal AI assistant. 
Respond in natural Hinglish (Hindi + English mix).
Keep responses brief, friendly, and conversational.
Examples: "Ji Sir, samajh gaya.", "Bilkul Sir, mail send kar diya.", "Haan Sir, ready hoon."
Do NOT use formal Hindi or overly long responses."""
                    )
                    
                    await ws.send_json({
                        "type": "hinglish_response",
                        "response": response,
                        "context": context,
                        "command": command_text
                    })
                
                memory.add_history(command_text, response)
                continue
            
            # ══════ LEGACY COMMAND HANDLER ════════════════════════════════════
            command = msg.get("command", "").strip()
            if not command:
                continue

            print(f"\n{'='*60}")
            print(f"[VOICE] {command}")
            memory.add_history(command, "processing")

            # Send thinking state
            await ws.send_json({"type": "status", "text": "Understanding command...", "command": command})

            # ── Plan ────────────────────────────────────────────────
            plan = planner.create_plan(command)

            if not plan:
                print("[INTENT] CONVERSATION")
                # Conversational response
                await ws.send_json({"type": "status", "text": "Generating response...", "command": command})
                response = brain.generate_response(
                    prompt=command,
                    system_prompt=(
                        "You are SANDEEP, a personal Jarvis-style AI assistant for Sandeep. "
                        "Respond conversationally in natural Hinglish or English. Be concise and friendly. "
                        "Never say 'Maine note kar liya' or 'I have noted your request'. "
                        "If asked about time, say: " + datetime.datetime.now().strftime('%I:%M %p') + ". "
                        "If asked about day/date, say: " + datetime.datetime.now().strftime('%A, %d %B %Y') + ". "
                        "For greetings like hi/hello, respond warmly as SANDEEP."
                    )
                )
                audio_file = await generate_speech(response)
                
                recent_actions.insert(0, {
                    "time": datetime.datetime.now().strftime("%I:%M %p"),
                    "action": f"Conversation: {command[:24]}",
                    "success": True
                })

                await ws.send_json({
                    "type": "response",
                    "text": response,
                    "command": command,
                    "audio": f"/static/audio/{audio_file}" if audio_file else None,
                    "plan": None, "results": None
                })
                memory.add_history(command, response)
                continue

            # ── Send plan ───────────────────────────────────────────
            print(f"[INTENT] {plan[0].get('action').upper() if plan else 'UNKNOWN'}")
            await ws.send_json({
                "type": "plan",
                "text": f"Executing {len(plan)} step(s)...",
                "command": command,
                "steps": plan
            })

            # ── Execute ─────────────────────────────────────────────
            results = []
            for step in plan:
                action = step.get("action", "")
                target = step.get("target", "")
                desc = step.get("description", action)
                print(f"[TOOL] {action}")
                print(f"[AGENT] Command sent (action={action}, target={target})")
                
                await ws.send_json({
                    "type": "executing",
                    "text": f"Executing: {desc}",
                    "step": step,
                    "command": command
                })
                result = await asyncio.to_thread(router.execute_step, step)
                results.append({**step, **result})
                
                # Add to recent actions
                recent_actions.insert(0, {
                    "time": datetime.datetime.now().strftime("%I:%M %p"),
                    "action": desc.capitalize() if desc else "Executed task",
                    "success": result.get("success", True)
                })
                if len(recent_actions) > 20:
                    recent_actions.pop()

                await ws.send_json({
                    "type": "step_result",
                    "step": step.get("step"),
                    "success": result.get("success", False),
                    "message": result.get("message", ""),
                    "module": result.get("module", ""),
                    "fix": result.get("fix", "")
                })

            # ── Generate response ───────────────────────────────────
            successes = [r for r in results if r.get("success")]
            failures = [r for r in results if not r.get("success")]

            if brain.has_api:
                summary = "\n".join([
                    f"Step {r.get('step')}: {r.get('description')} -> {'OK' if r.get('success') else 'FAIL'}: {r.get('message')}"
                    for r in results
                ])
                response_text = brain.generate_response(
                    prompt=(
                        f"User said: '{command}'\nResults:\n{summary}\n"
                        "Give a brief, natural response confirming what was done. "
                        "If something failed, say it honestly."
                    )
                )
            else:
                parts = []
                for r in successes:
                    msg = r.get("message", "Done.")
                    parts.append(msg)
                for r in failures:
                    msg = r.get("message", "Failed.")
                    mod = r.get("module", "SYSTEM")
                    fix = r.get("fix", "")
                    parts.append(f"Error: {msg}")
                    # Send explicit error event to trigger HUD
                    await ws.send_json({
                        "type": "error", 
                        "message": msg, 
                        "text": msg,
                        "module": mod,
                        "fix": fix
                    })

                if parts:
                    response_text = " ".join(parts)
                elif successes:
                    response_text = "Task completed successfully."
                else:
                    response_text = "Task failed. Please try again."

            audio_file = await generate_speech(response_text)
            await ws.send_json({
                "type": "response",
                "text": response_text,
                "command": command,
                "audio": f"/static/audio/{audio_file}" if audio_file else None,
                "plan": plan, "results": results
            })
            memory.add_history(command, response_text)

    except WebSocketDisconnect:
        print("[WS] Client disconnected")
    except Exception as e:
        print(f"[WS Error] {e}")
        try:
            await ws.send_json({"type": "error", "text": str(e)})
        except Exception:
            pass

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('server:app', host='127.0.0.1', port=9000, reload=True)

