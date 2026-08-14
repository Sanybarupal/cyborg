"""
SANDEEP TTS — Generates speech audio using edge-tts (online) with pyttsx3 offline fallback.
The web frontend plays the audio file via the browser.
"""
import asyncio
import os
import uuid

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Primary voice (Microsoft Neural) — Indian English male
VOICE_ONLINE = "en-IN-PrabhatNeural"


async def generate_speech(text: str) -> str:
    """Generate speech audio file and return the filename.
    
    Tries edge-tts first (requires internet). Falls back to pyttsx3 (offline).
    Returns empty string if both fail.
    """
    if not text or not text.strip():
        return ""

    filename = f"speech_{uuid.uuid4().hex[:8]}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    # ── Primary: edge-tts (online, high quality) ─────────────────────
    if EDGE_TTS_AVAILABLE:
        try:
            communicate = edge_tts.Communicate(text, VOICE_ONLINE)
            await communicate.save(filepath)
            if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
                return filename
        except Exception as e:
            print(f"[TTS edge-tts failed]: {e} — trying offline fallback...")

    # ── Fallback: pyttsx3 (offline, saves as WAV, served as-is) ──────
    if PYTTSX3_AVAILABLE:
        try:
            wav_filename = filename.replace(".mp3", ".wav")
            wav_filepath = os.path.join(AUDIO_DIR, wav_filename)
            # pyttsx3 must run in a thread (it's synchronous)
            result = await asyncio.to_thread(_pyttsx3_save, text, wav_filepath)
            if result and os.path.exists(wav_filepath) and os.path.getsize(wav_filepath) > 100:
                print(f"[TTS] Offline pyttsx3 used: {wav_filename}")
                return wav_filename
        except Exception as e:
            print(f"[TTS pyttsx3 failed]: {e}")

    print("[TTS] Both TTS engines failed — response will be text-only.")
    return ""


def _pyttsx3_save(text: str, filepath: str) -> bool:
    """Synchronous pyttsx3 save to file (runs in thread pool)."""
    try:
        engine = pyttsx3.init()
        # Prefer a male fallback voice; never select voices explicitly marked female.
        voices = engine.getProperty("voices")
        for voice in voices:
            name = (voice.name or '').lower()
            if 'female' not in name and any(token in name for token in ('male', 'david', 'mark', 'ravi', 'prabhat')):
                engine.setProperty("voice", voice.id)
                break
        engine.setProperty("rate", 165)   # Speed (words per minute)
        engine.setProperty("volume", 0.9)  # Volume 0.0 to 1.0
        engine.save_to_file(text, filepath)
        engine.runAndWait()
        return True
    except Exception as e:
        print(f"[pyttsx3 save error]: {e}")
        return False


def speak_sync(text: str) -> str:
    """Synchronous wrapper for generate_speech."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, generate_speech(text))
                return future.result()
        else:
            return asyncio.run(generate_speech(text))
    except RuntimeError:
        return asyncio.run(generate_speech(text))
