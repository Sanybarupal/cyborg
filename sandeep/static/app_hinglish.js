/**
 * SANDEEP Hinglish AI - Enhanced Voice Interaction
 * Features: Wake word detection, context awareness, human-like responses
 */

// ════════════════════════════════════════════════════════════════════════════════
// STATE & CONFIGURATION
// ════════════════════════════════════════════════════════════════════════════════

let ws = null;
let recognition = null;
let isListeningVoice = false;
let isSpeaking = false;
let wakeWordDetected = false;
let conversationContext = {};
let currentMessage = null;

// Wake words to detect
const WAKE_WORDS = ['hi sandeep', 'hey sandeep', 'sandeep', 'hii sandeep'];

// Web Speech API setup
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

// ════════════════════════════════════════════════════════════════════════════════
// WEBSOCKET INITIALIZATION
// ════════════════════════════════════════════════════════════════════════════════

function initWebSocket() {
    try {
        ws = new WebSocket('ws://127.0.0.1:8000/ws');

        ws.onopen = () => {
            console.log('✓ WebSocket Connected');
            updateStatus('Connected', 'success');
            showSystemMessage('System ready. Awaiting wake word...');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleServerResponse(data);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateStatus('Connection Error', 'error');
        };

        ws.onclose = () => {
            updateStatus('Disconnected', 'warning');
            setTimeout(initWebSocket, 3000);
        };
    } catch (error) {
        console.error('WebSocket init error:', error);
    }
}

// ════════════════════════════════════════════════════════════════════════════════
// VOICE RECOGNITION SETUP WITH WAKE WORD DETECTION
// ════════════════════════════════════════════════════════════════════════════════

function initVoiceRecognition() {
    if (!SpeechRecognition) {
        alert('Speech Recognition not supported');
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = true;  // Keep listening continuously
    recognition.interimResults = true;
    recognition.lang = 'en-IN';  // English (India) for Hinglish
    
    // Also support Hindi
    let langToggle = false;

    recognition.onstart = () => {
        console.log('🎤 Voice recognition started');
        isListeningVoice = true;
        updateVoiceIndicator(true);
    };

    recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript.toLowerCase();

            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }

        // Display interim results
        if (interimTranscript) {
            document.getElementById('voice-display').textContent = `Listening: ${interimTranscript}`;
        }

        // Process final transcript
        if (finalTranscript) {
            finalTranscript = finalTranscript.trim();
            document.getElementById('voice-display').textContent = finalTranscript;
            
            // Check for wake word
            if (!wakeWordDetected) {
                if (detectWakeWord(finalTranscript)) {
                    wakeWordDetected = true;
                    respondToWakeWord();
                    return;  // Don't process as command
                }
            } else {
                // Process as command
                handleVoiceCommand(finalTranscript);
                wakeWordDetected = false;  // Reset for next wake word
            }
        }
    };

    recognition.onerror = (event) => {
        console.error('Voice error:', event.error);
    };

    recognition.onend = () => {
        console.log('🎤 Voice recognition ended');
        isListeningVoice = false;
        updateVoiceIndicator(false);
        
        // Restart listening after brief delay
        setTimeout(() => {
            if (recognition) {
                recognition.start();
            }
        }, 500);
    };

    // Start listening
    try {
        recognition.start();
    } catch (e) {
        console.log('Recognition already started');
    }
}

// ════════════════════════════════════════════════════════════════════════════════
// WAKE WORD DETECTION
// ════════════════════════════════════════════════════════════════════════════════

function detectWakeWord(transcript) {
    transcript = transcript.toLowerCase().trim();
    
    for (let wakeWord of WAKE_WORDS) {
        if (transcript.includes(wakeWord)) {
            console.log(`🎤 Wake word detected: "${wakeWord}"`);
            return true;
        }
    }
    
    return false;
}

function respondToWakeWord() {
    console.log('✓ Wake word acknowledged');
    
    // Respond to wake word
    const response = "Ji Sir, main sun raha hoon.";
    
    // Speak acknowledgment
    speakResponse(response);
    
    // Update UI
    showSystemMessage(`WAITING FOR COMMAND... (Say your command)`);
    updateStatus('Listening for Command', 'active');
}

// ════════════════════════════════════════════════════════════════════════════════
// VOICE COMMAND HANDLER
// ════════════════════════════════════════════════════════════════════════════════

function handleVoiceCommand(command) {
    if (!command.trim()) return;

    console.log('🎤 Voice Command:', command);
    showUserMessage(command, 'voice');

    // Send to server for processing
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'voice_command',
            text: command,
            context: conversationContext,
            timestamp: new Date().toISOString()
        }));
    }
}

// ════════════════════════════════════════════════════════════════════════════════
// SERVER RESPONSE HANDLER
// ════════════════════════════════════════════════════════════════════════════════

function handleServerResponse(data) {
    console.log('Server Response:', data);

    if (data.type === 'voice_response' || data.type === 'hinglish_response') {
        const response = data.response || data.text;
        
        // Show response
        showAIMessage(response);
        
        // Speak response
        if (response) {
            speakResponse(response);
        }
        
        // Update context
        if (data.context) {
            conversationContext = { ...conversationContext, ...data.context };
        }
        
        // Handle confirmation requests
        if (data.requires_confirmation) {
            currentMessage = data.pending_data;
            showSystemMessage(`(Awaiting confirmation... Say "Haan" or "Nahi")`);
            wakeWordDetected = true;  // Ready for confirmation response
        }
    } else if (data.type === 'command_executed') {
        showAIMessage(data.response);
        speakResponse(data.response);
    }
}

// ════════════════════════════════════════════════════════════════════════════════
// TEXT-TO-SPEECH WITH HUMAN-LIKE VOICE
// ════════════════════════════════════════════════════════════════════════════════

function speakResponse(text) {
    if (!('speechSynthesis' in window)) {
        console.log('Speech synthesis not supported');
        return;
    }

    // Cancel any ongoing speech
    speechSynthesis.cancel();

    try {
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Human-like voice settings
        utterance.rate = 0.85;      // Slower, clearer speech
        utterance.pitch = 1.0;      // Natural pitch
        utterance.volume = 1.0;     // Full volume
        
        // Try to use a natural-sounding voice
        const voices = speechSynthesis.getVoices();
        const indianVoice = voices.find(v => v.lang.includes('hi') || v.lang.includes('en-IN'));
        if (indianVoice) {
            utterance.voice = indianVoice;
        }

        utterance.onstart = () => {
            isSpeaking = true;
            updateStatus('Speaking', 'speaking');
        };

        utterance.onend = () => {
            isSpeaking = false;
            updateStatus('Listening', 'active');
        };

        speechSynthesis.speak(utterance);
    } catch (error) {
        console.error('TTS Error:', error);
    }
}

// ════════════════════════════════════════════════════════════════════════════════
// UI MESSAGE DISPLAY
// ════════════════════════════════════════════════════════════════════════════════

function showUserMessage(text, source = 'voice') {
    const container = document.getElementById('message-container') || document.getElementById('hudResponsePreview');
    if (!container) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message user ${source}`;
    messageDiv.innerHTML = `
        <span class="source">${source === 'voice' ? '🎤 You' : '⌨️ You'}</span>
        <p>${escapeHtml(text)}</p>
    `;

    container.parentElement.appendChild(messageDiv);
    container.parentElement.scrollTop = container.parentElement.scrollHeight;
}

function showAIMessage(text) {
    const container = document.getElementById('message-container') || document.getElementById('hudResponsePreview');
    if (!container) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai';
    messageDiv.innerHTML = `
        <span class="source">🤖 SANDEEP</span>
        <p>${escapeHtml(text)}</p>
    `;

    container.parentElement.appendChild(messageDiv);
    container.parentElement.scrollTop = container.parentElement.scrollHeight;
    
    // Update main response display
    const responseElement = document.getElementById('hudResponseText');
    if (responseElement) {
        responseElement.textContent = text;
    }
}

function showSystemMessage(text) {
    const container = document.getElementById('message-container') || document.getElementById('hudResponsePreview');
    if (!container) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';
    messageDiv.innerHTML = `
        <span class="source">⚙️ System</span>
        <p>${escapeHtml(text)}</p>
    `;

    container.parentElement.appendChild(messageDiv);
    container.parentElement.scrollTop = container.parentElement.scrollHeight;
}

// ════════════════════════════════════════════════════════════════════════════════
// STATUS UPDATES
// ════════════════════════════════════════════════════════════════════════════════

function updateStatus(message, type = 'info') {
    const statusElement = document.getElementById('aiState') || document.getElementById('aiStatusBadge');
    if (statusElement) {
        if (type === 'speaking') {
            statusElement.textContent = '🔊 SPEAKING';
        } else if (type === 'active') {
            statusElement.textContent = '🎤 LISTENING';
        } else {
            statusElement.textContent = message;
        }
        statusElement.className = type;
    }
}

function updateVoiceIndicator(isActive) {
    const indicator = document.getElementById('voice-status') || document.getElementById('pillVoice');
    if (indicator) {
        if (isActive) {
            indicator.classList.add('active');
            indicator.textContent = '🎤 LISTENING';
        } else {
            indicator.classList.remove('active');
            indicator.textContent = '🎤 STANDBY';
        }
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ════════════════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ════════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    console.log('🤖 SANDEEP Hinglish AI - Initializing...');
    
    initWebSocket();
    initVoiceRecognition();
    
    // Load voices for TTS
    if ('speechSynthesis' in window) {
        speechSynthesis.onvoiceschanged = () => {
            console.log('✓ Voices loaded');
        };
    }
    
    showSystemMessage('🎤 Say "Hi Sandeep" to activate...');
    console.log('✓ SANDEEP Ready - Waiting for wake word');
});
