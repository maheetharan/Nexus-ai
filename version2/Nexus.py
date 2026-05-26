# ╔══════════════════════════════════════════╗
# ║       NEXUS AI - Version 2.0             ║
# ║       Added: Voice Input + Output        ║
# ║       Brain: Groq API                    ║
# ╚══════════════════════════════════════════╝
# pip install groq speechrecognition pyttsx3 pyaudio

import speech_recognition as sr
import pyttsx3
from groq import Groq

# ─────────────────────────────────────────
# ⚙️ SETTINGS
# ─────────────────────────────────────────
GROQ_API_KEY = "your-groq-api-key-here"

# ─────────────────────────────────────────
# 🔊 VOICE OUTPUT
# ─────────────────────────────────────────
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

voices = engine.getProperty('voices')
for voice in voices:
    if any(n in voice.name.lower() for n in ["male","david","mark"]):
        engine.setProperty('voice', voice.id)
        break

def speak(text):
    print(f"🤖 Nexus: {text}")
    engine.say(text)
    engine.runAndWait()

# ─────────────────────────────────────────
# 🎙️ VOICE INPUT
# ─────────────────────────────────────────
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=5)
            return r.recognize_google(audio, language="en-IN").lower()
        except:
            return ""

# ─────────────────────────────────────────
# 🧠 AI BRAIN
# ─────────────────────────────────────────
client = Groq(api_key=GROQ_API_KEY)
conversation_history = []

def ask_nexus(user_input):
    conversation_history.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are Nexus, a smart friendly AI assistant. Keep replies under 2 sentences. Be casual."}
        ] + conversation_history,
        max_tokens=150
    )
    reply = response.choices[0].message.content.strip()
    conversation_history.append({"role": "assistant", "content": reply})
    return reply

# ─────────────────────────────────────────
# 🚀 MAIN LOOP
# ─────────────────────────────────────────
def run():
    speak("Nexus version 2 online. You can speak or type!")
    print("💡 Press Enter to type instead of speaking.\n")

    while True:
        text = listen()
        if not text:
            text = input("⌨️ You: ").strip()
        if not text:
            continue
        if text.lower() in ["exit","bye","goodbye"]:
            speak("Goodbye!")
            break
        reply = ask_nexus(text)
        speak(reply)

if __name__ == "__main__":
    run()