/**
 * SANDEEP — Jarvis AI Command Center
 * Enhanced: Voice Commands + Button Click Input
 * Real-time WebSocket Communication
 */

// ════════════════════════════════════════════════════════════════════════════════
// STATE & INITIALIZATION
// ════════════════════════════════════════════════════════════════════════════════

let ws = null;
let recognition = null;
let isListeningVoice = false;
let audioContext = null;
let analyser = null;
let animationId = null;

// Web Speech API Recognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

// ════════════════════════════════════════════════════════════════════════════════
// WEBSOCKET INITIALIZATION
// ════════════════════════════════════════════════════════════════════════════════

function initWebSocket() {
    try {
        ws = new WebSocket('ws://127.0.0.1:8000/ws');

        ws.onopen = () => {
            console.log('✓ Connected to SANDEEP Jarvis AI System');
            updateStatus('Connected', 'success');
            addSystemMessage('Connected to SANDEEP Jarvis AI System. Ready for voice and text commands.');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleServerResponse(data);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateStatus('Connection Error', 'error');
            addSystemMessage('⚠️ Connection error. Trying to reconnect...');
        };

        ws.onclose = () => {
            console.log('WebSocket closed');
            updateStatus('Disconnected', 'warning');
            setTimeout(initWebSocket, 3000);
        };
    } catch (error) {
        console.error('WebSocket initialization error:', error);
    }
}

// ════════════════════════════════════════════════════════════════════════════════
// VOICE RECOGNITION SETUP
// ════════════════════════════════════════════════════════════════════════════════

function initVoiceRecognition() {
    if (!SpeechRecognition) {
        alert('Web Speech API not supported in this browser');
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.language = 'en-US';

    recognition.onstart = () => {
        console.log('Voice recognition started');
        isListeningVoice = true;
        updateVoiceStatus(true);
        addSystemMessage('🎤 Voice recognition started...');
    };

    recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;

            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }

        // Display interim results
        if (interimTranscript) {
            document.getElementById('voice-input-display').textContent = interimTranscript;
        }

        // Process final transcript
        if (finalTranscript) {
            document.getElementById('voice-input-display').textContent = finalTranscript.trim();
            handleVoiceCommand(finalTranscript.trim());
        }
    };

    recognition.onerror = (event) => {
        console.error('Voice recognition error:', event.error);
        addSystemMessage(`⚠️ Voice error: ${event.error}`);
        updateVoiceStatus(false);
    };

    recognition.onend = () => {
        console.log('Voice recognition ended');
        isListeningVoice = false;
        updateVoiceStatus(false);
        document.getElementById('voice-input-display').textContent = '';
    };
}

// ════════════════════════════════════════════════════════════════════════════════
// VOICE INPUT HANDLER
// ════════════════════════════════════════════════════════════════════════════════

function handleVoiceCommand(command) {
    if (!command.trim()) return;

    console.log('🎤 Voice Command:', command);
    addUserMessage(command, 'voice');

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'voice',
            text: command,
            timestamp: new Date().toISOString()
        }));
    } else {
        simulateResponse(command);
    }
}

// ════════════════════════════════════════════════════════════════════════════════
// TEXT INPUT HANDLER (Button Click)
// ════════════════════════════════════════════════════════════════════════════════

function handleTextCommand(text) {
    if (!text.trim()) return;

    console.log('⌨️ Text Command:', text);
    addUserMessage(text, 'text');

    // Clear input field
    const inputField = document.getElementById('command-input');
    if (inputField) inputField.value = '';

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'text',
            text: text,
            timestamp: new Date().toISOString()
        }));
    } else {
        simulateResponse(text);
    }
}

// ════════════════════════════════════════════════════════════════════════════════
// SERVER RESPONSE HANDLER
// ════════════════════════════════════════════════════════════════════════════════

function handleServerResponse(data) {
    console.log('Server Response:', data);

    if (data.type === 'voice_response' || data.type === 'text_response') {
        addAIMessage(data.response);
        if (data.response) {
            speakResponse(data.response);
        }
    } else if (data.type === 'command_executed') {
        addAIMessage(data.response);
    } else if (data.type === 'status') {
        console.log('Status update:', data);
    }
}

// ════════════════════════════════════════════════════════════════════════════════
// SIMULATE RESPONSE (Fallback when server unavailable)
// ════════════════════════════════════════════════════════════════════════════════

function simulateResponse(command) {
    const responses = {
        'hello': 'नमस्ते! I am SANDEEP Jarvis AI. How can I assist you?',
        'hi': 'Hello! Ready to help you.',
        'name': 'I am SANDEEP - Jarvis AI System, your personal voice assistant.',
        'time': `It is currently ${new Date().toLocaleTimeString()}`,
        'date': `Today is ${new Date().toLocaleDateString()}`,
        'help': 'You can give me voice commands or type text commands. Try saying "Hello" or "What time is it".',
    };

    let response = 'Processing your request...';
    const cmd = command.toLowerCase();

    for (let key in responses) {
        if (cmd.includes(key)) {
            response = responses[key];
            break;
        }
    }

    setTimeout(() => {
        addAIMessage(response);
        speakResponse(response);
    }, 500);
}

// ════════════════════════════════════════════════════════════════════════════════
// UI MESSAGE DISPLAY
// ════════════════════════════════════════════════════════════════════════════════

function addUserMessage(text, source = 'text') {
    const responseContent = document.getElementById('response-content');
    if (!responseContent) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message user ${source}`;
    messageDiv.innerHTML = `
        <span class="source">${source === 'voice' ? '🎤 Voice' : '⌨️ Text'}</span>
        <span class="time">${new Date().toLocaleTimeString()}</span>
        <p>${escapeHtml(text)}</p>
    `;

    responseContent.appendChild(messageDiv);
    responseContent.scrollTop = responseContent.scrollHeight;
}

function addAIMessage(text) {
    const responseContent = document.getElementById('response-content');
    if (!responseContent) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai';
    messageDiv.innerHTML = `
        <span class="source">🤖 SANDEEP</span>
        <span class="time">${new Date().toLocaleTimeString()}</span>
        <p>${escapeHtml(text)}</p>
    `;

    responseContent.appendChild(messageDiv);
    responseContent.scrollTop = responseContent.scrollHeight;
}

function addSystemMessage(text) {
    const responseContent = document.getElementById('response-content');
    if (!responseContent) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';
    messageDiv.innerHTML = `
        <span class="source">⚙️ System</span>
        <span class="time">${new Date().toLocaleTimeString()}</span>
        <p>${escapeHtml(text)}</p>
    `;

    responseContent.appendChild(messageDiv);
    responseContent.scrollTop = responseContent.scrollHeight;
}

// ════════════════════════════════════════════════════════════════════════════════
// TEXT-TO-SPEECH
// ════════════════════════════════════════════════════════════════════════════════

function speakResponse(text) {
    if (!('speechSynthesis' in window)) {
        console.log('Speech synthesis not supported');
        return;
    }

    // Cancel any ongoing speech
    speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () => {
        updateSpeakingStatus(true);
    };

    utterance.onend = () => {
        updateSpeakingStatus(false);
    };

    speechSynthesis.speak(utterance);
}

// ════════════════════════════════════════════════════════════════════════════════
// STATUS UPDATES
// ════════════════════════════════════════════════════════════════════════════════

function updateStatus(message, type = 'info') {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        statusElement.textContent = message;
        statusElement.className = `badge ${type}`;
    }
}

function updateVoiceStatus(isActive) {
    const voiceStatus = document.getElementById('voice-status');
    if (voiceStatus) {
        if (isActive) {
            voiceStatus.textContent = '🎤 Voice: Active';
            voiceStatus.classList.add('active');
        } else {
            voiceStatus.textContent = '🎤 Voice: Inactive';
            voiceStatus.classList.remove('active');
        }
    }
}

function updateSpeakingStatus(isSpeaking) {
    const systemStatus = document.getElementById('system-status');
    if (systemStatus) {
        if (isSpeaking) {
            systemStatus.textContent = '🔊 Speaking';
            systemStatus.classList.add('speaking');
        } else {
            systemStatus.textContent = '⚡ Ready';
            systemStatus.classList.remove('speaking');
        }
    }
}

// ════════════════════════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ════════════════════════════════════════════════════════════════════════════════

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ════════════════════════════════════════════════════════════════════════════════
// EVENT LISTENERS - DOM READY
// ════════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    console.log('🤖 SANDEEP Jarvis AI System - Initializing...');

    // Initialize systems
    initWebSocket();
    initVoiceRecognition();

    // Voice Button Control
    const voiceBtn = document.getElementById('voice-btn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', () => {
            if (isListeningVoice) {
                recognition.stop();
            } else {
                if (recognition) {
                    recognition.start();
                }
            }
        });
    }

    // Text Input & Send Button
    const commandInput = document.getElementById('command-input');
    const sendBtn = document.getElementById('send-btn');

    if (sendBtn) {
        sendBtn.addEventListener('click', () => {
            const text = commandInput.value.trim();
            if (text) {
                handleTextCommand(text);
            }
        });
    }

    if (commandInput) {
        commandInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const text = commandInput.value.trim();
                if (text) {
                    handleTextCommand(text);
                }
            }
        });
    }

    // Quick Command Buttons
    const quickBtns = document.querySelectorAll('.quick-btn');
    quickBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const command = btn.getAttribute('data-command');
            handleTextCommand(command);
        });
    });

    // Particle animation background
    initParticles();

    console.log('✓ SANDEEP Jarvis AI System Ready');
});

// ════════════════════════════════════════════════════════════════════════════════
// PARTICLE ANIMATION (Optional Visual Effect)
// ════════════════════════════════════════════════════════════════════════════════

function initParticles() {
    const canvas = document.getElementById('particleCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = [];

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 2;
            this.vy = (Math.random() - 0.5) * 2;
            this.size = Math.random() * 1 + 0.5;
            this.opacity = Math.random() * 0.5 + 0.2;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0) this.x = canvas.width;
            if (this.x > canvas.width) this.x = 0;
            if (this.y < 0) this.y = canvas.height;
            if (this.y > canvas.height) this.y = 0;
        }

        draw() {
            ctx.fillStyle = `rgba(0, 255, 150, ${this.opacity})`;
            ctx.fillRect(this.x, this.y, this.size, this.size);
        }
    }

    for (let i = 0; i < 50; i++) {
        particles.push(new Particle());
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => {
            p.update();
            p.draw();
        });
        requestAnimationFrame(animate);
    }

    animate();

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}
