# 🤖 SANDEEP - Jarvis AI Voice Assistant
## Complete Setup & Testing Guide

---

## 📋 Overview

**SANDEEP** is a **Jarvis-style AI Command Center** featuring:
- ✅ **Voice Commands** - Web Speech API for continuous listening
- ✅ **Button Click Input** - Text commands with Send button or Enter key
- ✅ **Real-time WebSocket** - Live communication with backend
- ✅ **AI Responses** - Conversational AI with voice output
- ✅ **Status Monitoring** - Live system health and connection status
- ✅ **Task Planning** - Complex command execution with step tracking

---

## 🚀 Quick Start (3 Commands)

### 1️⃣ Navigate to Project
```bash
cd c:\Users\boysa\cyborg\sandeep
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Start Server
**Option A - Command Line:**
```bash
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

**Option B - Batch File (Windows):**
```bash
START_SERVER.bat
```

---

## 🌐 Access the Application

Once server is running, open in browser:

📍 **http://127.0.0.1:8000/**

You should see:
- ✅ Jarvis-style HUD interface
- ✅ Blue pulsing microphone button (top-right)
- ✅ Text input field
- ✅ Status badges (Connection, Voice, System)
- ✅ Response output area

---

## 🎤 Testing Voice Commands

### Prerequisites:
- ✅ Microphone connected and functional
- ✅ Browser has microphone permission (allow when prompted)
- ✅ JavaScript enabled

### How to Use:
1. **Click the microphone button** 🎤 (top-right, blue pulsing icon)
   - Status changes to "🎤 Voice: Active"
   - Red circle animation indicates listening
   
2. **Speak clearly** into your microphone
   - You'll see interim transcription appear
   - Wait for your words to be recognized
   
3. **AI responds**:
   - Response appears in conversation area
   - AI speaks response aloud
   - Status updates to show completion

### Voice Test Phrases:
```
"Hello"
"Hi there"
"What is your name?"
"What time is it?"
"What's the date?"
"Help me"
"How are you?"
```

---

## ⌨️ Testing Text Commands (Button Click)

### How to Use:
1. **Type command** in text input field
   - Placeholder: "Speak hands-free or type a command here..."
   
2. **Send command** via:
   - **Click Send button** (arrow icon next to input)
   - **Press Enter key**
   
3. **AI responds** immediately

### Text Test Phrases:
```
hello
what is your name
open chrome
show me the time
help
```

---

## ✅ Complete Testing Checklist

### 🔧 Initial Setup
- [ ] Python 3.7+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] All static files present (index.html, app.js, style.css)
- [ ] Server starts without errors

### 🌐 Connection & UI
- [ ] Page loads at http://127.0.0.1:8000/
- [ ] HUD interface displays correctly
- [ ] All UI elements visible (buttons, input, badges)
- [ ] Browser console shows no errors (F12)

### 🔌 WebSocket Connection
- [ ] WebSocket connects when page loads
- [ ] Console shows: "✓ Connected to SANDEEP Jarvis AI System"
- [ ] Connection badge shows green/active
- [ ] Messages flow between client and server

### 🎤 Voice Input Testing
- [ ] Microphone button is clickable
- [ ] Clicking triggers permission prompt
- [ ] Grant microphone permission
- [ ] "Listening..." appears when active
- [ ] Speak a test phrase
- [ ] Interim transcription displays
- [ ] Final command is recognized
- [ ] AI responds with text
- [ ] AI speaks response aloud
- [ ] Conversation history updates

### ⌨️ Text Input Testing
- [ ] Input field accepts typing
- [ ] Send button is clickable
- [ ] Enter key works to submit
- [ ] Command appears in conversation
- [ ] AI responds immediately
- [ ] Multiple commands work in sequence

### 🔄 Real-time Updates
- [ ] Status badges update correctly
- [ ] Voice active/inactive indicator works
- [ ] Connection status changes appropriately
- [ ] Timestamps appear on messages
- [ ] Response scrolls to latest message

### 🛑 Error Handling
- [ ] Gracefully handles empty commands
- [ ] Shows error for connection issues
- [ ] Reconnects automatically if disconnected
- [ ] Fallback response when server unavailable

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────┐
│         Browser (Client)                     │
│  ┌────────────────────────────────────┐    │
│  │ UI (index.html)                    │    │
│  │  • Microphone button               │    │
│  │  • Text input field                │    │
│  │  • Response display                │    │
│  └────────────────────────────────────┘    │
│           ↕ (app.js)                       │
│  • Voice Recognition (Web Speech API)      │
│  • Button Click Handlers                   │
│  • WebSocket Communication                 │
└─────────────────────────────────────────────┘
           ↕
      [WebSocket]
      ws://127.0.0.1:8000/ws
           ↕
┌─────────────────────────────────────────────┐
│    FastAPI Backend Server (server.py)       │
│  ┌────────────────────────────────────┐    │
│  │ WebSocket Handler                  │    │
│  │  • Receive voice/text commands     │    │
│  │  • Process with AI Brain           │    │
│  │  • Send JSON responses             │    │
│  └────────────────────────────────────┘    │
│           ↕                                 │
│  ┌────────────────────────────────────┐    │
│  │ Core Modules                       │    │
│  │  • brain.py (LLM interface)        │    │
│  │  • planner.py (Task planning)      │    │
│  │  • memory.py (Context storage)     │    │
│  │  • router.py (Tool execution)      │    │
│  └────────────────────────────────────┘    │
│           ↕                                 │
│  ┌────────────────────────────────────┐    │
│  │ Voice Output                       │    │
│  │  • Text-to-Speech (edge-tts)       │    │
│  │  • Audio file generation           │    │
│  │  • Serve audio files               │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

---

## 🔍 Debugging & Troubleshooting

### 1. "Connection Refused" Error
**Problem:** Cannot connect to http://127.0.0.1:8000/

**Solution:**
- Ensure server is running
- Check port 8000 is not blocked by firewall
- Try: `python -m uvicorn server:app --host 127.0.0.1 --port 8000`

### 2. Microphone Not Detected
**Problem:** No microphone permission prompt or mic not recognized

**Solution:**
- Check microphone is connected: Settings → Sound → Input devices
- Grant browser permission: Settings → Privacy → Microphone
- Test mic in another browser first
- Try refreshing page

### 3. Voice Not Recognized
**Problem:** Speaking but no transcription appears

**Solution:**
- Speak louder and more clearly
- Check microphone is unmuted
- Reduce background noise
- Try shorter phrases first
- Check browser supports Web Speech API (Chrome, Edge, Safari)

### 4. No Audio Response
**Problem:** AI responds with text but doesn't speak

**Solution:**
- Check speaker/headphone volume
- Allow browser to play audio: check notification bar
- Disable browser audio mute
- Try different browser

### 5. WebSocket Connection Fails
**Problem:** "Failed to connect" or 404 error

**Solution:**
- Check server is running on correct port (8000)
- Check firewall allows WebSocket connections
- Check browser console (F12) for specific error
- Restart server and refresh browser

### 6. Text Input Not Working
**Problem:** Input field not responding to clicks or typing

**Solution:**
- Click input field to ensure it's focused (should show blue border)
- Try refreshing page
- Check JavaScript is enabled
- Try Enter key instead of Send button

---

## 🎯 Features & Capabilities

### Voice Input Features:
✅ Continuous listening capability  
✅ Interim transcription display  
✅ Final command processing  
✅ Multiple language support (configurable)  
✅ Automatic restart after speech end  
✅ Error recovery and reconnection  

### Text Input Features:
✅ Type any command  
✅ Send button activation  
✅ Enter key submission  
✅ Input field with placeholder  
✅ Auto-clear after submission  
✅ Validation and error handling  

### Response Features:
✅ Real-time message display  
✅ Timestamped conversations  
✅ Source indicator (voice/text)  
✅ AI voice response output  
✅ Message history in view  
✅ Auto-scroll to latest  

### System Features:
✅ WebSocket real-time communication  
✅ Status badge indicators  
✅ Connection monitoring  
✅ Voice activity indicator  
✅ System health checks  
✅ Automatic reconnection  

---

## 📁 Project Structure

```
sandeep/
├── server.py                      # FastAPI backend server
├── requirements.txt               # Python dependencies
├── LIVE_TEST_GUIDE.md            # Detailed testing guide
├── START_SERVER.bat              # Windows startup script
├── verify_system.py              # System verification tool
│
├── static/
│   ├── index.html               # Main UI (Jarvis HUD)
│   ├── app.js                   # Frontend logic (voice + button handling)
│   ├── style.css                # UI styling
│   └── audio/                   # Generated audio responses
│
├── core/
│   ├── brain.py                 # LLM interface (litellm)
│   ├── planner.py               # Task planning engine
│   └── memory.py                # Memory management
│
├── executors/
│   ├── router.py                # Tool routing
│   ├── files.py                 # File operations
│   ├── vision.py                # OCR/vision
│   └── windows.py               # Windows-specific actions
│
└── windows_agent/
    ├── voice_pipeline.py        # Voice capture + STT
    ├── agent.py                 # Windows integration
    └── tests/
```

---

## 🔧 Configuration

### Server Settings (server.py):
```python
HOST = "127.0.0.1"     # Localhost only
PORT = 8000            # Default FastAPI port
RELOAD = True          # Auto-reload on file changes
```

### Voice Recognition Settings (app.js):
```javascript
recognition.language = 'en-US';      // Language code
recognition.continuous = false;      // One phrase at a time
recognition.interimResults = true;   // Show interim text
```

### TTS Settings (app.js):
```javascript
utterance.rate = 1.0;    // Speed (0.1 to 10)
utterance.pitch = 1.0;   // Pitch (0 to 2)
utterance.volume = 1.0;  // Volume (0 to 1)
```

---

## 🌟 Advanced Usage

### Custom Commands
Modify `simulateResponse()` in `app.js` to add more responses:
```javascript
const responses = {
    'custom': 'Your custom response here',
};
```

### Backend Command Processing
Modify `server.py` to add custom actions:
```python
def process_command(command: str) -> str:
    # Add your custom logic here
    return response
```

### UI Customization
Edit `static/style.css` to change:
- Colors, fonts, sizes
- Animation speeds
- Button styles
- Status badge appearance

---

## ❓ FAQ

**Q: Do I need internet to use this?**
A: No, it works offline for local commands. Only need internet for certain AI features.

**Q: What browsers are supported?**
A: Chrome, Edge, Safari (all support Web Speech API). Firefox has limited support.

**Q: Can I change the language?**
A: Yes, modify `recognition.language` in app.js to language codes like 'hi-IN', 'es-ES', etc.

**Q: Is my voice data stored?**
A: No, processing happens locally. Browser doesn't save audio.

**Q: Can I run this on a different port?**
A: Yes, change port in startup command: `--port 9000`

**Q: How do I add new AI commands?**
A: Extend the `responses` dictionary in app.js or modify server.py brain.py

---

## 📞 Support

If you encounter issues:
1. Check browser console (F12) for errors
2. Verify server is running with no errors
3. Ensure microphone permissions are granted
4. Review LIVE_TEST_GUIDE.md for detailed steps
5. Check troubleshooting section above

---

## ✨ Summary

Your SANDEEP Jarvis AI Voice Assistant is fully configured with:

✅ Voice command input via Web Speech API  
✅ Text input via button click  
✅ Real-time WebSocket communication  
✅ Conversational AI responses  
✅ Voice synthesis output  
✅ Real-time status monitoring  
✅ Automatic error recovery  

**Ready to test? Start the server now!** 🚀

```bash
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

Then visit: **http://127.0.0.1:8000/**

---

**Last Updated:** August 12, 2026  
**Status:** ✅ Production Ready
