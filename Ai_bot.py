#Ai.py
import speech_recognition as sr
import pyttsx3
import pyautogui
import subprocess
import webbrowser
import datetime
import requests
import os
import json
import threading
from googlesearch import search
from groq import Groq

# ─────────────────────────────────────────
# ⚙️ SETTINGS
# ─────────────────────────────────────────
GROQ_API_KEY = "Your_Groq_API_Key_Here"   # 👈 Paste your key from https://console.groq.com
WAKE_WORD = "nexus"
MEMORY_FILE = "nexus_memory.json"

# ─────────────────────────────────────────
# 💾 MEMORY
# ─────────────────────────────────────────
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"user_name": None, "facts": []}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

memory = load_memory()

# ─────────────────────────────────────────
# 🔊 VOICE OUTPUT
# ─────────────────────────────────────────
engine = pyttsx3.init()
engine.setProperty("rate", 170)
engine.setProperty("volume", 1.0)

def speak(text):
    print(f"🤖 Nexus: {text}")
    engine.say(text)
    engine.runAndWait()

# ─────────────────────────────────────────
# 🎙️ VOICE INPUT
# ─────────────────────────────────────────
def listen(timeout=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio = r.listen(source, timeout=timeout)
            return r.recognize_google(audio).lower()
        except:
            return ""

# ─────────────────────────────────────────
# 🧠 AI BRAIN
# ─────────────────────────────────────────
client = Groq(api_key=GROQ_API_KEY)
conversation_history = []

def ask_nexus(user_input):
    conversation_history.append({"role": "user", "content": user_input})

    name_context = f"The user's name is {memory['user_name']}." if memory['user_name'] else ""

    system_prompt = f"""
You are Nexus, a friendly, smart AI assistant.
Keep replies under 2 short sentences.
Be casual and natural.
{name_context}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": system_prompt}] + conversation_history,
        max_tokens=120
    )

    reply = response.choices[0].message.content.strip()
    conversation_history.append({"role": "assistant", "content": reply})

    # Learn name
    if memory["user_name"] is None:
        if "my name is" in user_input:
            name = user_input.split("my name is")[-1].strip().split()[0]
            memory["user_name"] = name.capitalize()
            save_memory(memory)

    return reply

# ─────────────────────────────────────────
# 🌦️ WEATHER
# ─────────────────────────────────────────
def get_weather(city=""):
    try:
        location = city if city else "auto"
        url = f"https://wttr.in/{location}?format=3"
        return requests.get(url, timeout=5).text.strip()
    except:
        return "Couldn't fetch weather."

# ─────────────────────────────────────────
# 🕐 TIME & DATE
# ─────────────────────────────────────────
def get_time():
    return f"It's {datetime.datetime.now().strftime('%I:%M %p')}."

def get_date():
    return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."

# ─────────────────────────────────────────
# 🌐 SEARCH
# ─────────────────────────────────────────
def search_web(query):
    try:
        results = list(search(query, num_results=3))
        return results[0] if results else "No results found."
    except:
        return "Search failed."

# ─────────────────────────────────────────
# 💻 CONTROL COMPUTER
# ─────────────────────────────────────────
def control_computer(command):

    # Open websites
    sites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "github": "https://github.com",
        "gmail": "https://mail.google.com",
    }

    for site, url in sites.items():
        if site in command and "open" in command:
            webbrowser.open(url)
            speak(f"Opening {site}.")
            return True

    # Open apps
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
    }

    for app, exe in apps.items():
        if app in command and "open" in command:
            subprocess.Popen(exe)
            speak(f"Opening {app}.")
            return True

    # Screenshot
    if "screenshot" in command:
        filename = f"screenshot_{datetime.datetime.now().strftime('%H%M%S')}.png"
        pyautogui.screenshot(filename)
        speak("Screenshot saved.")
        return True

    return False

# ─────────────────────────────────────────
# 🧠 COMMAND HANDLER
# ─────────────────────────────────────────
def handle_command(user_input):

    print(f"👤 You: {user_input}")

    if "time" in user_input:
        speak(get_time())

    elif "date" in user_input or "day" in user_input:
        speak(get_date())

    elif "weather" in user_input:
        city = user_input.replace("weather", "").strip()
        speak(get_weather(city))

    elif "search" in user_input:
        query = user_input.replace("search", "").strip()
        result = search_web(query)
        speak(result)

    elif control_computer(user_input):
        pass

    else:
        response = ask_nexus(user_input)
        speak(response)

# ─────────────────────────────────────────
# 🔀 HYBRID MODE
# ─────────────────────────────────────────
def hybrid_mode():

    speak("Hybrid mode activated. You can speak or type anytime.")

    def voice_loop():
        while True:
            user_input = listen()
            if user_input:
                user_input = user_input.replace(WAKE_WORD, "").strip()
                handle_command(user_input)

    def text_loop():
        while True:
            user_input = input("\n⌨️ You: ").lower().strip()
            if user_input in ["exit", "bye", "shutdown"]:
                speak("Goodbye! Shutting down.")
                os._exit(0)
            if user_input:
                handle_command(user_input)

    threading.Thread(target=voice_loop, daemon=True).start()
    threading.Thread(target=text_loop, daemon=True).start()

    while True:
        pass

# ─────────────────────────────────────────
# 🚀 START
# ─────────────────────────────────────────
if __name__ == "__main__":
    hybrid_mode()
