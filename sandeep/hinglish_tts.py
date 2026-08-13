"""
Enhanced Text-to-Speech Engine
Provides natural, human-like voice with Hinglish support
"""

import asyncio
import re
import edge_tts
from pathlib import Path

class HinglishTTSEngine:
    def __init__(self):
        # Use natural-sounding voice
        self.voice = "en-IN-NeerjaNeural"  # Natural Indian English voice
        self.rate = "-10%"  # Slower speech rate
        self.pitch = "+0Hz"  # Natural pitch
        self.audio_dir = Path(__file__).parent / "static" / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
    
    def add_natural_pauses(self, text: str) -> str:
        """
        Add natural pauses (SSML breaks) between sentences for human-like delivery.
        """
        # Add pause after sentences ending with period, exclamation, question
        text = re.sub(r'([.!?])\s+', r'\1<break time="600ms"/>', text)
        
        # Add pause after commas
        text = re.sub(r'([,])\s+', r'\1<break time="300ms"/>', text)
        
        # Add pause before confirmation questions
        text = re.sub(r'(Kya.*\?)', r'<break time="400ms"/>\1', text, flags=re.IGNORECASE)
        
        return text
    
    def add_emphasis(self, text: str) -> str:
        """
        Add natural emphasis and intonation to text.
        """
        # Emphasize key actions
        text = re.sub(r'\b(open|close|send|message|check|delete)\b', 
                     r'<emphasis level="strong">\1</emphasis>', 
                     text, flags=re.IGNORECASE)
        
        # Emphasize confirmations
        text = re.sub(r'\b(Ji|Haan|Bilkul|Okay|Okay Sir)\b', 
                     r'<emphasis level="moderate">\1</emphasis>', 
                     text)
        
        return text
    
    def format_hinglish_speech(self, text: str) -> str:
        """
        Format Hinglish text with SSML for natural delivery.
        """
        # Wrap in SSML
        formatted = f"""<speak>
<voice name="{self.voice}">
<prosody rate="{self.rate}" pitch="{self.pitch}">
{text}
</prosody>
</voice>
</speak>"""
        
        return formatted
    
    async def text_to_speech(self, text: str, filename: str = None) -> str:
        """
        Convert text to speech asynchronously.
        Returns the path to the generated audio file.
        """
        if filename is None:
            import time
            filename = f"response_{int(time.time())}.mp3"
        
        filepath = self.audio_dir / filename
        
        # Add natural pauses and emphasis
        formatted_text = self.add_natural_pauses(text)
        formatted_text = self.add_emphasis(formatted_text)
        
        try:
            # Use edge-tts for high-quality speech
            communicate = edge_tts.Communicate(formatted_text, self.voice, rate=self.rate)
            await communicate.save(str(filepath))
            
            return f"/static/audio/{filename}"
        except Exception as e:
            print(f"TTS Error: {e}")
            return None

# Global TTS engine instance
tts_engine = HinglishTTSEngine()

# Synchronous wrapper for compatibility
def generate_hinglish_speech(text: str, filename: str = None) -> str:
    """
    Synchronous wrapper for text-to-speech generation.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(tts_engine.text_to_speech(text, filename))
        return result
    finally:
        loop.close()
