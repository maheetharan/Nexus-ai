# ╔══════════════════════════════════════════════════════════════╗
# ║         NEXUS v6 — Tamil Language Support                    ║
# ║         Understands Tamil, replies in Tamil                  ║
# ╚══════════════════════════════════════════════════════════════╝
# pip install googletrans==4.0.0rc1 gtts pygame

from gtts import gTTS
import pygame
import tempfile
import os
import requests

# ─────────────────────────────────────────
# ⚙️ SETTINGS
# ─────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL      = "qwen2.5:7b"

# Tamil characters range
TAMIL_RANGE = range(0x0B80, 0x0BFF)

# Common Tamil phrases Nexus knows
TAMIL_RESPONSES = {
    "வணக்கம்":           "வணக்கம்! நான் நெக்சஸ். உங்களுக்கு எப்படி உதவலாம்?",
    "vanakkam":          "வணக்கம்! நான் நெக்சஸ். என்ன செய்யட்டும்?",
    "nandri":            "இல்லை இல்லை! இது என் கடமை!",
    "நன்றி":             "இல்லை இல்லை! இது என் கடமை!",
    "en peyar enna":     "உங்கள் பெயர் மஹி! என் பெயர் நெக்சஸ்!",
    "unakku tamil theriyuma": "கொஞ்சம் கொஞ்சம் தெரியும்! நான் கற்றுக்கொண்டே இருக்கிறேன்!",
    "epdi irukeenga":    "நான் நலமாக இருக்கிறேன்! நீங்கள் எப்படி இருக்கிறீர்கள்?",
    "nee yaru":          "நான் நெக்சஸ்! மஹி உருவாக்கிய AI assistant!",
    "enna seyyalam":     "நான் உங்களுக்கு பல விஷயங்களில் உதவ முடியும் — தேடல், கணிதம், கணினி கட்டுப்பாடு!",
    "bye":               "போய் வாருங்கள்! நன்றி!",
    "சரி":               "சரி! என்ன வேண்டும்?",
}

# ─────────────────────────────────────────
# 🔍 DETECT TAMIL
# ─────────────────────────────────────────
def is_tamil(text):
    """Check if text contains Tamil characters."""
    return any(ord(c) in TAMIL_RANGE for c in text)

def is_tamil_romanized(text):
    """Check if text is Tamil written in English letters."""
    tamil_roman_words = [
        "vanakkam", "nandri", "epdi", "irukeenga", "enna",
        "yaru", "theriyuma", "peyar", "seyyalam", "nexus",
        "mahee", "nee", "naan", "ungal", "en peyar",
        "unakku", "theriyuma", "konjam", "pesuvathu"
    ]
    text_lower = text.lower()
    return any(word in text_lower for word in tamil_roman_words)

def needs_tamil_response(text):
    """Check if we should respond in Tamil."""
    return is_tamil(text) or is_tamil_romanized(text)

# ─────────────────────────────────────────
# 🗣️ SPEAK IN TAMIL
# ─────────────────────────────────────────
def speak_tamil(text):
    """Speak text in Tamil using gTTS."""
    print(f"🤖 Nexus (Tamil): {text}")
    try:
        tts = gTTS(text=text, lang='ta', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            tmp = f.name
        tts.save(tmp)
        pygame.mixer.init()
        pygame.mixer.music.load(tmp)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        os.unlink(tmp)
    except Exception as e:
        print(f"⚠️ Tamil TTS error: {e}")

# ─────────────────────────────────────────
# 🧠 ASK NEXUS IN TAMIL
# ─────────────────────────────────────────
def ask_nexus_tamil(user_input, memory=None):
    """Generate Tamil response using Ollama."""
    # Check preset responses first
    ui_lower = user_input.lower().strip()
    for trigger, response in TAMIL_RESPONSES.items():
        if trigger in ui_lower:
            return response

    # Ask Ollama for Tamil response
    name_ctx = f"பயனரின் பெயர் {memory['user_name']}." if memory and memory.get('user_name') else ""

    prompt = f"""நீங்கள் நெக்சஸ் என்ற AI assistant. மஹி என்பவர் உங்களை உருவாக்கினார்.
{name_ctx}
தமிழில் சுருக்கமாக பதில் சொல்லுங்கள் (2-3 வாக்கியங்கள் மட்டுமே).
இயற்கையாக பேசுங்கள்.

பயனர்: {user_input}
நெக்சஸ்:"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=30
        )
        return response.json()["response"].strip()
    except:
        return "மன்னிக்கவும்! இப்போது பதில் சொல்ல முடியவில்லை."

# ─────────────────────────────────────────
# 🌐 TRANSLATE (English → Tamil)
# ─────────────────────────────────────────
def translate_to_tamil(english_text):
    """Translate English response to Tamil."""
    try:
        from googletrans import Translator
        translator = Translator()
        result = translator.translate(english_text, dest='ta')
        return result.text
    except:
        return english_text

# ─────────────────────────────────────────
# 🧩 MAIN HANDLER
# ─────────────────────────────────────────
def handle_tamil(user_input, memory=None):
    """
    Handle Tamil input — returns (response_text, is_tamil)
    If is_tamil=True, use speak_tamil() to speak it.
    """
    if needs_tamil_response(user_input):
        response = ask_nexus_tamil(user_input, memory)
        return response, True
    return None, False