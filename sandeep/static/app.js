/**
 * SANDEEP — Jarvis AI Command Center Engine
 * Continuous Voice Recognition, WebSocket Directives, Real Telemetry, Dynamic Waveforms
 */

// ── State ──────────────────────────────────────────────────────────
let ws = null;
let recognition = null;
let isListeningContinuous = true;
let isSpeaking = false;
let wakeWordDetected = false;
let scheduleItems = JSON.parse(localStorage.getItem('sandeep_schedule') || '[]');
let currentAudio = null;
const WAKE_WORDS = ['hey sandeep', 'hay sandeep', 'hi sandeep', 'hii sandeep'];
const WAKE_ACK = 'Ji Sir, main sun raha hoon.';

// ── DOM Elements ───────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
const aiState = $('aiState');
const aiStateSub = $('aiStateSub');
const aiStatusBadge = $('aiStatusBadge');
const voiceWaveform = $('voiceWaveform');
const hudCommandText = $('hudCommandText');
const hudResponseText = $('hudResponseText');
const cmdInput = $('cmdInput');
const sendBtn = $('sendBtn');
const micBtn = $('micBtn');
const taskTracker = $('taskTracker');
const ttTitle = $('ttTitle');
const ttCount = $('ttCount');
const ttFill = $('ttFill');
const ttStep = $('ttStep');

// ── Initialization ─────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initClock();
    initWebSocket();
    initContinuousVoice();
    initScheduleUI();
    setupEvents();
    pollSystemStatus();
});

// ── Clock ──────────────────────────────────────────────────────────
function initClock() {
    const update = () => {
        const now = new Date();
        $('clock').textContent = now.toLocaleTimeString('en-IN', { hour12: true });
    };
    update();
    setInterval(update, 1000);
}

// ── Holographic Ambient Particles ──────────────────────────────────
function initParticles() {
    const canvas = $('particleCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let w, h, particles = [];

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    for (let i = 0; i < 45; i++) {
        particles.push({
            x: Math.random() * w,
            y: Math.random() * h,
            r: Math.random() * 1.5 + 0.5,
            dx: (Math.random() - 0.5) * 0.35,
            dy: (Math.random() - 0.5) * 0.35,
            o: Math.random() * 0.35 + 0.1
        });
    }

    function draw() {
        ctx.clearRect(0, 0, w, h);
        particles.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 229, 255, ${p.o})`;
            ctx.fill();
            p.x += p.dx;
            p.y += p.dy;
            if (p.x < 0 || p.x > w) p.dx *= -1;
            if (p.y < 0 || p.y > h) p.dy *= -1;
        });
        requestAnimationFrame(draw);
    }
    draw();
}

// ── WebSocket Connection ───────────────────────────────────────────
function initWebSocket() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    ws = new WebSocket(`${proto}://${location.host}/ws`);

    ws.onopen = () => {
        setBadge('pillAI', true);
        setBadge('pillAgent', true);
        setHUDState('SYSTEM ONLINE // READY', 'Continuous Voice Recognition Active — Speak your command');
    };

    ws.onmessage = (e) => {
        try {
            const data = JSON.parse(e.data);
            handleServerEvent(data);
            
        } catch (err) {
            console.error('[WS Parse Error]:', err);
        }
    };

    ws.onclose = () => {
        setBadge('pillAI', false);
        setBadge('pillAgent', false);
        setHUDState('DISCONNECTED', 'Attempting reconnection...');
        setTimeout(initWebSocket, 3000);
    };

    ws.onerror = (err) => {
        console.error('[WS Error]:', err);
    };
}

function setBadge(id, online) {
    const el = $(id);
    if (el) el.className = `status-badge ${online ? 'online' : 'offline'}`;
}

// ── Server Event Handling ──────────────────────────────────────────
let planTotal = 0, planDone = 0;

function handleServerEvent(d) {
    switch (d.type) {
        case 'greeting':
            hudResponseText.textContent = d.text;
            if (d.audio) playAudioResponse(d.audio);
            break;

        case 'status':
            setHUDState('PROCESSING DIRECTIVE', d.text);
            if (d.command) hudCommandText.textContent = `"${d.command}"`;
            updateDiagnosticFlow('UNDERSTANDING', 'active');
            break;

        case 'error':
            showSystemError(d.message || d.text);
            setHUDState('SYSTEM ERROR', 'Task execution failed');
            addErrorLog({
                module: d.module || 'SYSTEM',
                message: d.message || d.text,
                fix: d.fix || 'Check system status'
            });
            updateDiagnosticFlow('VERIFYING', 'error');
            break;

        case 'action':
            planTotal = d.steps ? d.steps.length : 0;
            planDone = 0;
            if (d.command) hudCommandText.textContent = `"${d.command}"`;
            showTracker(d.text, planTotal);
            setHUDState('EXECUTING DIRECTIVE', `${planTotal} action(s) scheduled`);
            updateDiagnosticFlow('TOOL ROUTER', 'active');
            break;

        case 'executing':
            updateTracker(d.text);
            updateDiagnosticFlow('WINDOWS AGENT', 'active');
            break;

        case 'step_result':
            planDone++;
            // updateTrackerBar(planDone, planTotal); // UI removed
            if (d.success) {
                updateDiagnosticFlow('VERIFYING', 'done');
            } else {
                updateDiagnosticFlow('VERIFYING', 'error');
                addErrorLog({
                    module: 'VERIFICATION',
                    message: d.message || 'Verification failed',
                    fix: d.fix || 'Check if action completed'
                });
            }
            break;

        case 'response':
            hideTracker();
            if (d.command) hudCommandText.textContent = `"${d.command}"`;
            hudResponseText.textContent = d.text;
            setHUDState('TASK COMPLETED', 'All directives executed');
            updateDiagnosticFlow('COMPLETED', 'done');

            if (d.audio) {
                playAudioResponse(d.audio);
            } else {
                setTimeout(() => {
                    setHUDState('SYSTEM ACTIVE // LISTENING', 'Continuous Voice Recognition Active — Speak your command');
                }, 3000);
            }
            fetchSystemStatus();
            break;
            
        case 'health_update':
            updateSystemHealth(d.health);
            break;
    }
}

// ── HUD State Manager ───────────��──────────────────────────────────
function setHUDState(state, sub) {
    aiState.textContent = state;
    aiStateSub.textContent = sub || '';
    
    aiStatusBadge.className = 'hud-status-badge';
    voiceWaveform.classList.remove('listening', 'speaking');

    if (state.includes('LISTENING') || state.includes('READY') || state.includes('ONLINE')) {
        aiStatusBadge.classList.add('listening');
        voiceWaveform.classList.add('listening');
    } else if (state.includes('EXECUTING') || state.includes('PROCESSING')) {
        aiStatusBadge.classList.add('executing');
    } else if (state.includes('SPEAKING')) {
        voiceWaveform.classList.add('speaking');
    }
}

function showTracker(title, total) {
    taskTracker.style.display = 'block';
    ttTitle.textContent = title.toUpperCase();
    ttStep.textContent = 'Initializing execution pipeline...';
    // Initialize flow
    const flow = $('diagFlow');
    if (flow) {
        flow.innerHTML = `
            <span class="diag-step done">LISTENING</span> →
            <span class="diag-step done">COMMAND RECEIVED</span> →
            <span class="diag-step active">UNDERSTANDING</span>
        `;
    }
}

function updateTracker(text) {
    ttStep.textContent = text;
}

function updateDiagnosticFlow(stepName, status) {
    const flow = $('diagFlow');
    if (!flow) return;
    
    // Add new step
    const arrow = `<span style="color:#555"> → </span>`;
    const newStep = `<span class="diag-step ${status}">${stepName}</span>`;
    
    // If it's a completion or error, just append
    if (!flow.innerHTML.includes(stepName)) {
        flow.innerHTML += arrow + newStep;
    } else {
        // Find existing and update class
        flow.innerHTML = flow.innerHTML.replace(
            new RegExp(`<span class="diag-step [^"]*">${stepName}<\/span>`),
            `<span class="diag-step ${status}">${stepName}</span>`
        );
    }
}

function hideTracker() {
    setTimeout(() => {
        taskTracker.style.display = 'none';
    }, 1800);
}

// ── Continuous Voice Recognition Engine ─────────────────────────────
function initContinuousVoice() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
        setBadge('pillVoice', false);
        setBadge('pillMic', false);
        console.warn('Speech Recognition not supported in this browser.');
        return;
    }

    recognition = new SR();
    recognition.lang = 'en-IN';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
        micBtn.classList.add('active');
        setBadge('pillMic', true);
        if (!isSpeaking) {
            setHUDState('SYSTEM ACTIVE // LISTENING', 'Continuous Voice Recognition Active — Speak your command');
        }
    };

    recognition.onresult = (e) => {
        const transcript = e.results[0][0].transcript.trim();
        if (!transcript) return;
        console.log('[v0] Heard:', transcript);
        hudCommandText.textContent = `"${transcript}"`;

        const normalized = transcript.toLowerCase();
        const wakeIndex = WAKE_WORDS.findIndex(word => normalized.includes(word));
        if (!wakeWordDetected) {
            if (wakeIndex < 0) return;
            wakeWordDetected = true;
            const command = transcript.slice(wakeIndex >= 0 ? normalized.indexOf(WAKE_WORDS[wakeIndex]) + WAKE_WORDS[wakeIndex].length : 0).trim();
            speakResponse(WAKE_ACK);
            setHUDState('LISTENING FOR COMMAND', 'Wake word detected — speak your command');
            if (command) sendCmd(command);
            return;
        }
        wakeWordDetected = false;
        sendCmd(transcript);
    };

    recognition.onerror = (e) => {
        console.log('[v0] Speech Error:', e.error);
        if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {
            isListeningContinuous = false;
            wakeWordDetected = false;
            setBadge('pillMic', false);
            setHUDState('MICROPHONE PERMISSION REQUIRED', 'Tap the microphone and allow browser access to continue');
        }
    };

    recognition.onend = () => {
        // Automatically restart if continuous listening is enabled and not speaking
        if (isListeningContinuous && !isSpeaking) {
            setTimeout(() => {
                startVoiceEngine();
            }, 300);
        }
    };

    setBadge('pillVoice', true);
    startVoiceEngine();
}

function startVoiceEngine() {
    if (!recognition || isSpeaking) return;
    try {
        recognition.start();
    } catch (e) {
        // Already started or restarting
    }
}

function stopVoiceEngine() {
    if (!recognition) return;
    try {
        recognition.stop();
    } catch (e) {}
}

function speakResponse(text) {
    if (!text || !('speechSynthesis' in window)) return;
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 0.85;
    utterance.volume = 1;
    const voices = speechSynthesis.getVoices();
    const male = voices.find(v => /male|david|mark|guy|ravi|prabhat/i.test(`${v.name} ${v.voiceURI}`)) || voices.find(v => /en-IN|hi-IN/i.test(v.lang));
    if (male) utterance.voice = male;
    utterance.onstart = () => { isSpeaking = true; setHUDState('SPEAKING', 'Voice response in progress'); stopVoiceEngine(); };
    utterance.onend = () => { isSpeaking = false; if (isListeningContinuous) { setHUDState('SYSTEM ACTIVE // LISTENING', 'Continuous Voice Recognition Active — Speak your command'); setTimeout(startVoiceEngine, 400); } };
    speechSynthesis.speak(utterance);
}

function playAudioResponse(url) {
    isSpeaking = true;
    stopVoiceEngine();
    setHUDState('JARVIS SPEAKING', 'Delivering voice feedback');

    if (currentAudio) {
        currentAudio.pause();
    }

    currentAudio = new Audio(url);
    currentAudio.play().catch(e => {
        console.log('[Audio play failed - user interaction needed]:', e);
    });

    currentAudio.onended = () => {
        isSpeaking = false;
        setHUDState('SYSTEM ACTIVE // LISTENING', 'Continuous Voice Recognition Active — Speak your command');
        if (isListeningContinuous) {
            setTimeout(startVoiceEngine, 400);
        }
    };
}

// ── Command Dispatcher ─────────────────────────────────────────────
window.sendCmd = function(text) {
    if (!text || !text.trim()) return;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        hudResponseText.textContent = 'System disconnected. Reconnecting...';
        return;
    }
    
    hudCommandText.textContent = `"${text.trim()}"`;
    setHUDState('PROCESSING DIRECTIVE', 'Dispatching command to task router...');
    ws.send(JSON.stringify({ command: text.trim() }));
    cmdInput.value = '';
    hudCommandText.textContent = '';
    hudResponseText.textContent = '';
}

// ── System Error Display ───────────────────────────────────────────
let errorTimeout = null;
function showSystemError(message) {
    const box = document.getElementById('hudErrorBox');
    const msgEl = document.getElementById('hudErrorMessage');
    if (box && msgEl) {
        msgEl.textContent = message;
        box.style.display = 'block';
        
        // Auto-hide after 8 seconds
        if (errorTimeout) clearTimeout(errorTimeout);
        errorTimeout = setTimeout(() => {
            box.style.display = 'none';
        }, 8000);
    }
}

// ── Voice Recognition (Web Speech API) ──────────────────────────────
function pollSystemStatus() {
    fetchSystemStatus();
    setInterval(fetchSystemStatus, 2500);
}

async function fetchSystemStatus() {
    try {
        const res = await fetch('/api/system-status');
        if (!res.ok) return;
        const d = await res.json();

        // Real Telemetry Meters
        $('cpuVal').textContent = `${d.cpu}%`;
        $('cpuFill').style.width = `${d.cpu}%`;

        $('ramVal').textContent = `${d.ram}%`;
        $('ramFill').style.width = `${d.ram}%`;

        $('diskVal').textContent = `${d.disk}%`;
        $('diskFill').style.width = `${d.disk}%`;

        if (d.battery !== null && d.battery !== undefined) {
            $('battVal').textContent = `${d.battery}%`;
            $('battFill').style.width = `${d.battery}%`;
        } else {
            $('battVal').textContent = 'AC POWER';
            $('battFill').style.width = '100%';
        }

        // Recent Actions List
        const actionsList = $('recentActionsList');
        if (d.recent_actions && d.recent_actions.length > 0) {
            actionsList.innerHTML = d.recent_actions.map(a => `
                <div class="action-entry ${a.success ? '' : 'fail'}">
                    <span class="action-time">${escapeHtml(a.time)}</span>
                    <span class="action-text">${escapeHtml(a.action)}</span>
                </div>
            `).join('');
        }

        // Active Processes
        const appList = $('appList');
        if (d.apps && d.apps.length > 0) {
            appList.innerHTML = d.apps.map(a => `<span class="app-badge-tag">${a}</span>`).join('');
        } else {
            appList.innerHTML = '<span class="tag-empty">No prominent desktop apps</span>';
        }

        if (d.health) {
            updateSystemHealth(d.health);
        }
    } catch (e) {
        console.error('[Telemetry fetch error]:', e);
    }
}

// ── System Health & Error Logs ──────────────────────────────────────
function updateSystemHealth(healthData) {
    // healthData: { mic: 'online', ai: 'warning', agent: 'error', ... }
    const map = {
        'online': 'h-green',
        'warning': 'h-yellow',
        'error': 'h-red',
        'offline': 'h-gray'
    };
    for (let key in healthData) {
        const el = $(`h_${key}`);
        if (el) {
            el.className = `h-dot ${map[healthData[key]] || 'h-gray'}`;
        }
    }
}

function addErrorLog(err) {
    const container = $('errorLogsContainer');
    if (!container) return;
    
    const time = new Date().toLocaleTimeString('en-IN', { hour12: true });
    const logCard = document.createElement('div');
    logCard.className = 'error-log-card';
    logCard.innerHTML = `
        <div class="error-log-header">
            <span class="error-log-module">${escapeHtml(err.module)}</span>
            <span class="error-log-time">${escapeHtml(time)}</span>
        </div>
        <div class="error-log-msg">${escapeHtml(err.message)}</div>
        <div class="error-log-fix">FIX: ${escapeHtml(err.fix)}</div>
    `;
    
    // Remove "No errors" placeholder if exists
    const empty = container.querySelector('.sched-empty');
    if (empty) container.removeChild(empty);
    
    container.prepend(logCard);
}

// ── Schedule / Directives ──────────────────────────────────────────
function initScheduleUI() {
    renderSchedule();
    $('schedAddBtn').addEventListener('click', addScheduleItem);
    $('schedInput').addEventListener('keydown', e => {
        if (e.key === 'Enter') addScheduleItem();
    });
}

function addScheduleItem() {
    const inp = $('schedInput');
    const text = inp.value.trim();
    if (!text) return;
    scheduleItems.push({ text, done: false, id: Date.now() });
    saveSchedule();
    renderSchedule();
    inp.value = '';
}

function renderSchedule() {
    const list = $('scheduleList');
    if (scheduleItems.length === 0) {
        list.innerHTML = '<div class="sched-empty">No active directives</div>';
        return;
    }
    list.innerHTML = scheduleItems.map((item, i) => `
        <div class="sched-item">
            <div class="sched-check ${item.done ? 'done' : ''}" onclick="toggleSched(${i})">${item.done ? '&#10003;' : ''}</div>
            <span class="sched-text" style="${item.done ? 'text-decoration:line-through;opacity:.5' : ''}">${escapeHtml(item.text)}</span>
            <span class="sched-del" onclick="delSched(${i})">&#10005;</span>
        </div>
    `).join('');
}

window.toggleSched = (i) => {
    scheduleItems[i].done = !scheduleItems[i].done;
    saveSchedule();
    renderSchedule();
};

window.delSched = (i) => {
    scheduleItems.splice(i, 1);
    saveSchedule();
    renderSchedule();
};

function saveSchedule() {
    localStorage.setItem('sandeep_schedule', JSON.stringify(scheduleItems));
}

// ── UI Events ──────────────────────────────────────────────────────
function setupEvents() {
    sendBtn.addEventListener('click', () => sendCmd(cmdInput.value));
    cmdInput.addEventListener('keydown', e => {
        if (e.key === 'Enter') sendCmd(cmdInput.value);
    });

    micBtn.addEventListener('click', () => {
        if (isListeningContinuous) {
            isListeningContinuous = false;
            stopVoiceEngine();
            micBtn.classList.remove('active');
            setHUDState('MIC MUTED', 'Click mic button to resume continuous listening');
        } else {
            isListeningContinuous = true;
            micBtn.classList.add('active');
            startVoiceEngine();
            setHUDState('SYSTEM ACTIVE // LISTENING', 'Continuous Voice Recognition Active — Speak your command');
        }
    });

    // Auto-unlock audio playback on first page interaction if required by browser
    document.addEventListener('click', () => {
        if (isListeningContinuous && !recognition) {
            initContinuousVoice();
        }
    }, { once: true });
}
