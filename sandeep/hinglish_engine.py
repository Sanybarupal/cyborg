"""
SANDEEP Hinglish AI Engine
Handles Hinglish language processing, context awareness, and natural conversations
"""

import re
from typing import Dict, List, Tuple, Optional

# Intent mappings for various command variations
INTENT_MAPPINGS = {
    'open_app': {
        'keywords': [
            r'\b(open|kholo|chalao|start|chal|lao|start karo|khul ja|open karo|open kar)\b',
        ],
        'apps': {
            r'\b(whatsapp|whatsapp|watsapp|wa)\b': 'whatsapp',
            r'\b(chrome|cromo|browser|chrome browser)\b': 'chrome',
            r'\b(youtube|yt|youtube.com)\b': 'youtube',
            r'\b(vs code|vscode|vs-code|code editor)\b': 'vscode',
            r'\b(notepad|notepad plus|npp)\b': 'notepad',
            r'\b(gmail|google mail|mail)\b': 'gmail',
            r'\b(excel|spreadsheet)\b': 'excel',
            r'\b(word|microsoft word|document)\b': 'word',
        }
    },
    'close_app': {
        'keywords': [
            r'\b(close|band karo|band kar|close karo|close kar|quit|exit|shut down)\b',
        ],
        'apps': {
            r'\b(whatsapp|whatsapp|watsapp|wa)\b': 'whatsapp',
            r'\b(chrome|browser)\b': 'chrome',
            r'\b(youtube|yt)\b': 'youtube',
            r'\b(vs code|vscode)\b': 'vscode',
            r'\b(notepad)\b': 'notepad',
        }
    },
    'send_message': {
        'keywords': [
            r'\b(message karo|message kar|bhejo|send|msg|msg karo|bolo|kaho)\b',
        ]
    },
    'check_messages': {
        'keywords': [
            r'\b(check karo|check kar|dekhna|dekho|batao|message|msg|new messages|inbox)\b',
        ]
    },
    'greeting': {
        'keywords': [
            r'\b(hello|hi|hey|helo|namaste|namaskar|shukriya|thanks|thankyou)\b',
        ]
    }
}

# Hinglish responses database
HINGLISH_RESPONSES = {
    'greeting_response': [
        "Hello Sir, main online hoon. Bataiye, kya karna hai?",
        "Ji Sir, main sun raha hoon. Command do.",
        "Haan Sir, main ready hoon. Bataiye na.",
    ],
    'app_opening': [
        "Ji Sir, {app} open kar raha hoon.",
        "Okay Sir, {app} ko chalao.",
        "Bilkul Sir, {app} khol raha hoon.",
    ],
    'app_closing': [
        "Ji Sir, {app} close kar raha hoon.",
        "Okay Sir, {app} band kar diya.",
        "Bilkul Sir, {app} band kar raha hoon.",
    ],
    'message_confirmation': [
        "Ji Sir, message hai: '{message}'. Kya send kar doon?",
        "Samajh gaya Sir. Message: '{message}'. Send kar doon?",
        "Theek hai Sir. Iska matlab: '{message}'. Bhej doon?",
    ],
    'confirmation_positive': [
        "Okay Sir, send kar diya.",
        "Ji Sir, bhej diya.",
        "Bilkul Sir, message send ho gaya.",
    ],
    'ask_for_command': [
        "Haan Sir, main sun raha hoon.",
        "Ji Sir, aap bataiye.",
        "Bilkul Sir, command do.",
    ],
    'wake_acknowledged': [
        "Ji Sir, main sun raha hoon.",
        "Haan Sir, sunai de raha hai?",
        "Bilkul Sir, listening...",
    ]
}

class HinglishEngine:
    def __init__(self):
        self.conversation_context = {}
        self.last_contact = None
        self.last_app = None
        self.message_buffer = None
        
    def detect_intent(self, text: str) -> Tuple[str, Dict]:
        """
        Detect intent from user input.
        Returns: (intent_name, extracted_data)
        """
        text = text.lower().strip()
        
        # Check for open app intent
        for keyword_pattern in INTENT_MAPPINGS['open_app']['keywords']:
            if re.search(keyword_pattern, text):
                # Find which app
                for app_pattern, app_name in INTENT_MAPPINGS['open_app']['apps'].items():
                    if re.search(app_pattern, text):
                        self.last_app = app_name
                        return ('open_app', {'app': app_name})
        
        # Check for close app intent
        for keyword_pattern in INTENT_MAPPINGS['close_app']['keywords']:
            if re.search(keyword_pattern, text):
                # Find which app
                for app_pattern, app_name in INTENT_MAPPINGS['close_app']['apps'].items():
                    if re.search(app_pattern, text):
                        self.last_app = app_name
                        return ('close_app', {'app': app_name})
        
        # Check for send message intent
        for keyword_pattern in INTENT_MAPPINGS['send_message']['keywords']:
            if re.search(keyword_pattern, text):
                # Extract contact name if present
                # Simple extraction - would be enhanced with NLP
                contact = self._extract_contact_name(text)
                if contact:
                    self.last_contact = contact
                return ('send_message', {'contact': contact})
        
        # Check for check messages intent
        for keyword_pattern in INTENT_MAPPINGS['check_messages']['keywords']:
            if re.search(keyword_pattern, text):
                return ('check_messages', {})
        
        # Check for greeting
        for keyword_pattern in INTENT_MAPPINGS['greeting']['keywords']:
            if re.search(keyword_pattern, text):
                return ('greeting', {})
        
        # Default to conversation
        return ('conversation', {'text': text})
    
    def _extract_contact_name(self, text: str) -> Optional[str]:
        """
        Extract contact name from text.
        E.g., "Rahul ko message karo" -> "Rahul"
        """
        # Remove common phrases
        text = re.sub(r'\b(ko|ke|ka|message karo|message kar|bhejo|send)\b', '', text, flags=re.IGNORECASE)
        
        # Extract proper nouns (capitalized words)
        words = text.split()
        for word in words:
            if word and word[0].isupper():
                return word.lower()
        
        return None
    
    def get_hinglish_response(self, intent: str, data: Dict = None) -> str:
        """
        Generate appropriate Hinglish response for an intent.
        """
        if data is None:
            data = {}
        
        response_templates = HINGLISH_RESPONSES.get(intent + '_response', [])
        
        if not response_templates:
            # Fallback to generic response
            if intent == 'open_app':
                app_name = data.get('app', 'application')
                return f"Ji Sir, {app_name} khol raha hoon."
            elif intent == 'close_app':
                app_name = data.get('app', 'application')
                return f"Okay Sir, {app_name} band kar raha hoon."
            else:
                return "Ji Sir, samajh gaya."
        
        # Select first template and format with data
        response = response_templates[0]
        try:
            return response.format(**data)
        except KeyError:
            return response
    
    def should_ask_confirmation(self, intent: str) -> bool:
        """
        Determine if we should ask for confirmation before executing.
        """
        # Sensitive operations need confirmation
        sensitive_intents = ['send_message', 'delete_message', 'close_app']
        return intent in sensitive_intents
    
    def maintain_context(self, intent: str, data: Dict):
        """
        Update conversation context based on intent.
        """
        if intent == 'send_message':
            self.conversation_context['pending_message'] = {
                'contact': data.get('contact'),
                'text': data.get('text', '')
            }
        elif intent == 'open_app':
            self.conversation_context['last_opened_app'] = data.get('app')
        elif intent == 'close_app':
            self.conversation_context['last_closed_app'] = data.get('app')

# Initialize global engine
hinglish_engine = HinglishEngine()
