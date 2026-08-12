# SANDEEP - Jarvis AI Voice Assistant
## Complete Live Test Guide

### 🚀 Quick Start (3 Steps)

#### **Step 1: Install Dependencies**
```bash
cd c:\Users\boysa\cyborg\sandeep
pip install -r requirements.txt
```

#### **Step 2: Start the Server**
```bash
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```
Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

#### **Step 3: Open in Browser**
Visit: **http://127.0.0.1:8000/**

---

### 🎤 Testing Voice Commands

**Prerequisites:**
- Microphone connected and working
- Browser permission to access microphone (grant when prompted)
- JavaScript enabled

**How to Use:**
1. Click the **🎤 Microphone Button** in top-right area
2. Speak your command clearly
3. Wait for response (AI will speak back + show text)

**Test Commands to Try:**
```
"hello"
"what is your name"
"what time is it"
"help"
"how are you"
```

---

### ⌨️ Testing Text Commands (Button Click)

**How to Use:**
1. Type your command in the input field
2. Either:
   - Click the **Send Button** (arrow icon)
   - Press **Enter** key
3. See response appear immediately

**Test Commands to Try:**
```
hello
Who are you?
What is the current time?
Can you help me?
```

---

### 📊 Live Testing Checklist

- [ ] **Server starts without errors**
- [ ] **Page loads at http://127.0.0.1:8000/**
- [ ] **WebSocket connects** (check browser console for ✓ message)
- [ ] **Voice button is clickable**
- [ ] **Microphone permission prompt appears**
- [ ] **Voice recognition starts when button clicked**
- [ ] **Interim transcription appears**
- [ ] **Final transcription processed**
- [ ] **AI response displayed and spoken**
- [ ] **Text input field accepts typing**
- [ ] **Send button triggers command**
- [ ] **Enter key triggers command**
- [ ] **Response appears in conversation area**
- [ ] **Status badges update correctly**

---

### 🔍 Browser Developer Tools

To debug, press **F12** and check:

1. **Console Tab:**
   - Look for ✓ connection messages
   - Check for any JavaScript errors (red)
   
2. **Network Tab:**
   - Filter by "WS" to see WebSocket
   - Should show "http://127.0.0.1:8000/ws" with status "101"
   
3. **Application Tab → localStorage:**
   - View stored schedule data

---

### 🛠️ Troubleshooting

**"Connection refused" error:**
- Make sure server is running: `python -m uvicorn server:app --host 127.0.0.1 --port 8000`

**Microphone not working:**
- Check browser has microphone permission
- Try: Settings → Privacy and security → Microphone
- Test in another tab first

**Voice not being recognized:**
- Speak clearly and louder
- Check microphone is unmuted
- Try shorter phrases first

**No audio response:**
- Check speaker/headphone volume
- Allow browser to play audio
- Check for browser audio notification

**Text input not responding:**
- Make sure field is focused (blue border)
- Try pressing Enter instead of click
- Refresh page and try again

---

### 📱 Features Implemented

✅ **Voice Input:**
- Web Speech API (continuous listening)
- Real-time interim transcription
- Auto-stop on final result
- Fallback message handling

✅ **Text Input:**
- Input field with placeholder
- Send button click
- Enter key support
- Quick command buttons

✅ **Response Display:**
- Timestamped messages
- Source indicator (🎤 Voice / ⌨️ Text)
- AI responses marked with 🤖
- Auto-scroll to latest message
- System messages for debugging

✅ **Real-time Updates:**
- WebSocket communication
- Status badges (Connection, Voice, System)
- Live message streaming

✅ **Visual Effects:**
- Particle animation background
- Glowing status indicators
- Responsive HUD design

---

### 🎯 Command Examples

**Information Commands:**
- "What time is it?"
- "What's today's date?"
- "What is your name?"
- "Who are you?"

**Greeting Commands:**
- "Hello"
- "Hi"
- "Greetings"

**Help Commands:**
- "Help"
- "What can you do?"
- "Tell me about yourself"

---

### 📝 Server-Side Features

The backend (server.py) provides:
- **Task Planning:** Breaks complex commands into steps
- **Tool Routing:** Executes file operations, system commands, etc.
- **Memory Management:** Persistent conversation history
- **Health Monitoring:** System status reporting
- **TTS Generation:** Creates audio responses
- **Error Handling:** Graceful error recovery

---

### 🔧 Configuration Files

- **requirements.txt** - Python dependencies
- **static/index.html** - UI markup
- **static/app.js** - Frontend logic
- **static/style.css** - Styling
- **server.py** - Backend FastAPI server
- **core/brain.py** - LLM interface
- **core/planner.py** - Task planning
- **executors/router.py** - Command execution

---

### ✅ Everything is Ready!

Your SANDEEP Jarvis AI System is fully configured with:
1. ✅ Voice command input (Web Speech API)
2. ✅ Button click text command input (Send button)
3. ✅ Real-time WebSocket communication
4. ✅ Conversational AI responses
5. ✅ Text-to-speech output
6. ✅ Status monitoring and visual feedback
7. ✅ Error handling and fallback modes

**Start the server and test it live now!** 🚀
