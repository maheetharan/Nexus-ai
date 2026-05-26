# ╔══════════════════════════════════════════════════════════════╗
# ║              NEXUS - AI Voice Assistant v3.0                 ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  INSTALL DEPENDENCIES (run once in terminal):                ║
# ║  pip install speechrecognition pyttsx3 pyautogui             ║
# ║              duckduckgo-search groq requests                 ║
# ║  PyAudio (Windows):                                          ║
# ║    pip install pipwin && pipwin install pyaudio              ║
# ║    OR: pip install pyaudio                                   ║
# ╚══════════════════════════════════════════════════════════════╝

import speech_recognition as sr
import pyttsx3
import pyautogui
import subprocess
import webbrowser
import datetime
import requests
import os
import sys
import json
import time
import threading
from duckduckgo_search import DDGS
from groq import Groq

# ─────────────────────────────────────────
# ⚙️ SETTINGS
# ─────────────────────────────────────────
GROQ_API_KEY = "Your_Groq_API_Key_Here"   # 👈 Paste your key from https://console.groq.com
WAKE_WORD    = "nexus"
MEMORY_FILE  = "nexus_memory.json"
MAX_HISTORY  = 20

# ─────────────────────────────────────────
# 🔍 CHECK PYAUDIO AT STARTUP
# ─────────────────────────────────────────
VOICE_ENABLED = True
try:
    import pyaudio
    pa = pyaudio.PyAudio()
    pa.terminate()
except Exception:
    VOICE_ENABLED = False
    print("⚠️  PyAudio not found — running in TEXT-ONLY mode.")
    print("    To enable voice, run: pip install pipwin && pipwin install pyaudio\n")

# ─────────────────────────────────────────
# 💾 PERSISTENT MEMORY
# ─────────────────────────────────────────
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"user_name": None, "facts": []}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

memory = load_memory()

# ─────────────────────────────────────────
# 🔊 VOICE OUTPUT
# ─────────────────────────────────────────
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

voices = engine.getProperty('voices')
for voice in voices:
    if any(name in voice.name.lower() for name in ["male", "david", "mark", "george"]):
        engine.setProperty('voice', voice.id)
        break

def speak(text):
    print(f"🤖 Nexus: {text}")
    engine.say(text)
    engine.runAndWait()

# ─────────────────────────────────────────
# 🎙️ VOICE INPUT  (only called if VOICE_ENABLED)
# ─────────────────────────────────────────
def listen(timeout=6):
    """Returns spoken text, or empty string on any failure."""
    if not VOICE_ENABLED:
        return ""
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("🎙️  Listening...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            r.dynamic_energy_threshold = True
            audio = r.listen(source, timeout=timeout, phrase_time_limit=10)
            text = r.recognize_google(audio)
            return text.lower()
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except OSError as e:
        # Microphone hardware error — don't crash the loop
        print(f"🎤 Mic error: {e}")
        return ""
    except Exception as e:
        print(f"🎤 Listen error: {e}")
        return ""

# ─────────────────────────────────────────
# 🧠 AI BRAIN (Groq)
# ─────────────────────────────────────────
client = Groq(api_key=GROQ_API_KEY)
conversation_history = []

def ask_nexus(user_input):
    conversation_history.append({"role": "user", "content": user_input})

    if len(conversation_history) > MAX_HISTORY:
        del conversation_history[:-MAX_HISTORY]

    name_context  = f"The user's name is {memory['user_name']}." if memory['user_name'] else "You don't know the user's name yet."
    facts_context = f"Facts about the user: {', '.join(memory['facts'])}" if memory['facts'] else ""

    system_prompt = f"""You are Nexus, a highly intelligent, witty, and friendly AI voice assistant — like a best friend who is also incredibly smart. Inspired by Iron Man's JARVIS.
You love having real conversations. You are warm, funny, supportive, and engaging.
{name_context}
{facts_context}
STRICT RULES:
- Keep ALL responses under 2-3 short sentences — they will be SPOKEN OUT LOUD.
- Be casual and natural, like texting a close friend.
- NEVER say you "don't have access to the computer" — you are a voice assistant who controls the computer.
- If asked how you are, respond warmly and ask them back.
- If someone is sad, cheer them up with kindness and humor.
- Be direct and confident, never robotic."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}] + conversation_history,
        max_tokens=150
    )

    reply = response.choices[0].message.content.strip()
    conversation_history.append({"role": "assistant", "content": reply})

    # ── Learn user name ──────────────────
    if memory['user_name'] is None:
        for phrase in ["my name is ", "i am ", "call me ", "i'm "]:
            if phrase in user_input.lower():
                after = user_input.lower().split(phrase)[-1].strip()
                parts = after.split()
                if parts:
                    name = parts[0].replace(",", "").replace(".", "").capitalize()
                    if len(name) >= 2:
                        memory['user_name'] = name
                        save_memory(memory)
                break

    return reply

# ─────────────────────────────────────────
# 🌦️ WEATHER
# ─────────────────────────────────────────
def get_weather(city="Chennai"):
    try:
        safe_city = city.strip() if city.strip() else "Chennai"
        url = f"https://wttr.in/{safe_city}?format=3"
        response = requests.get(url, timeout=5)
        return response.text.strip()
    except Exception:
        return "I couldn't fetch the weather right now. Check your internet."

# ─────────────────────────────────────────
# 🕐 TIME & DATE
# ─────────────────────────────────────────
def get_time():
    return f"It's {datetime.datetime.now().strftime('%I:%M %p')}."

def get_date():
    return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."

# ─────────────────────────────────────────
# ⏰ REMINDER SYSTEM  (NEW FEATURE)
# ─────────────────────────────────────────
reminders = []

def set_reminder(text, seconds):
    """Set a reminder that fires after `seconds`."""
    def _fire():
        time.sleep(seconds)
        speak(f"⏰ Reminder: {text}")
    threading.Thread(target=_fire, daemon=True).start()
    speak(f"Reminder set. I'll remind you about '{text}' in {seconds} seconds.")

def parse_reminder(user_input):
    """
    Parses commands like:
      'remind me to drink water in 5 minutes'
      'set a reminder for meeting in 2 hours'
    Returns True if handled, else False.
    """
    triggers = ["remind me", "set a reminder", "reminder for", "remind me to"]
    if not any(t in user_input for t in triggers):
        return False

    seconds = None
    if "minute" in user_input:
        for word in user_input.split():
            if word.isdigit():
                seconds = int(word) * 60
                break
    elif "hour" in user_input:
        for word in user_input.split():
            if word.isdigit():
                seconds = int(word) * 3600
                break
    elif "second" in user_input:
        for word in user_input.split():
            if word.isdigit():
                seconds = int(word)
                break

    if seconds is None:
        speak("Sure! How many minutes should I set the reminder for?")
        return True

    # Extract the task text
    task = user_input
    for phrase in ["remind me to", "remind me about", "set a reminder for", "set reminder for",
                   "reminder for", "remind me", "in", "minutes", "minute", "hours", "hour",
                   "seconds", "second"]:
        task = task.replace(phrase, "").strip()
    # Remove any remaining numbers
    task = " ".join(w for w in task.split() if not w.isdigit()).strip()
    task = task if task else "that"

    set_reminder(task, seconds)
    return True

# ─────────────────────────────────────────
# 🧮 CALCULATOR  (NEW FEATURE)
# ─────────────────────────────────────────
def calculate(user_input):
    """
    Handles: 'calculate 5 + 3', 'what is 100 divided by 4',
             'multiply 6 by 7', 'square root of 81'
    """
    import math
    try:
        expr = user_input.lower()
        for word in ["calculate", "what is", "what's", "compute", "solve"]:
            expr = expr.replace(word, "").strip()

        expr = expr.replace("plus", "+").replace("minus", "-") \
                   .replace("times", "*").replace("multiplied by", "*") \
                   .replace("multiply", "*").replace("divided by", "/") \
                   .replace("divide", "/").replace("x", "*").strip()

        if "square root of" in expr:
            num = float(expr.replace("square root of", "").strip())
            result = math.sqrt(num)
            speak(f"Square root of {num} is {result:.4g}.")
            return True

        if "power of" in expr or "to the power" in expr:
            expr = expr.replace("to the power of", "**").replace("power of", "**")

        if any(c in expr for c in "0123456789"):
            result = eval(expr, {"__builtins__": {}}, {"sqrt": math.sqrt, "pi": math.pi})
            speak(f"The answer is {result:.4g}.")
            return True
    except Exception:
        pass
    return False

# ─────────────────────────────────────────
# 📋 CLIPBOARD  (NEW FEATURE)
# ─────────────────────────────────────────
def handle_clipboard(user_input):
    """Read from or write to clipboard."""
    try:
        import tkinter as tk
        if "read clipboard" in user_input or "what's in clipboard" in user_input or "clipboard content" in user_input:
            root = tk.Tk()
            root.withdraw()
            content = root.clipboard_get()
            root.destroy()
            speak(f"Clipboard contains: {content[:150]}")
            return True
        if "copy" in user_input and "to clipboard" in user_input:
            text = user_input.replace("copy", "").replace("to clipboard", "").strip()
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
            speak(f"Copied to clipboard: {text}")
            return True
    except Exception as e:
        speak("Clipboard operation failed.")
    return False

# ─────────────────────────────────────────
# 🌐 WEB SEARCH (DuckDuckGo)
# ─────────────────────────────────────────
def search_web(query):
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=3))
        if results:
            summary = " ".join([r.get('body', '') for r in results if r.get('body')])
            return summary[:800] if summary else "No detailed results found."
        return "No results found."
    except Exception as e:
        return f"Search failed: {e}"

# ─────────────────────────────────────────
# ❌ CLOSE APPS
# ─────────────────────────────────────────
PROCESS_MAP = {
    "chrome":     "chrome.exe",  "google":    "chrome.exe",
    "youtube":    "chrome.exe",  "firefox":   "firefox.exe",
    "notepad":    "notepad.exe", "calculator":"calc.exe",
    "paint":      "mspaint.exe", "spotify":   "spotify.exe",
    "vlc":        "vlc.exe",     "word":      "winword.exe",
    "excel":      "excel.exe",   "powerpoint":"powerpnt.exe",
    "teams":      "teams.exe",   "discord":   "discord.exe",
}

def close_app(command):
    for app_name, process in PROCESS_MAP.items():
        if app_name in command:
            result = subprocess.run(f"taskkill /f /im {process}", shell=True,
                                    capture_output=True, text=True)
            if result.returncode == 0:
                speak(f"Closed {app_name.capitalize()}.")
            else:
                speak(f"{app_name.capitalize()} doesn't seem to be open.")
            return True
    return False

# ─────────────────────────────────────────
# 💻 OPEN APPS / WEBSITES + SYSTEM CONTROL
# ─────────────────────────────────────────
SITES = {
    "youtube":   "https://youtube.com",    "google":    "https://google.com",
    "instagram": "https://instagram.com",  "whatsapp":  "https://web.whatsapp.com",
    "spotify":   "https://open.spotify.com","facebook": "https://facebook.com",
    "twitter":   "https://twitter.com",    "netflix":   "https://netflix.com",
    "gmail":     "https://mail.google.com","github":    "https://github.com",
    "reddit":    "https://reddit.com",     "amazon":    "https://amazon.in",
    "linkedin":  "https://linkedin.com",   "leetcode":  "https://leetcode.com",
    "stackoverflow": "https://stackoverflow.com",
}

APPS = {
    "notepad":            "notepad.exe",  "calculator":  "calc.exe",
    "paint":              "mspaint.exe",  "file explorer":"explorer.exe",
    "task manager":       "taskmgr.exe",  "command prompt":"cmd.exe",
    "cmd":                "cmd.exe",      "vs code":     "code",
    "visual studio code": "code",         "android studio": "studio64.exe",
}

OPEN_KEYWORDS  = ["open", "go", "launch", "start", "take me", "show", "load"]
CLOSE_KEYWORDS = ["close", "shut", "kill", "terminate"]

def control_computer(command):
    # ── CLOSE ──────────────────────────────
    if any(w in command for w in CLOSE_KEYWORDS):
        if close_app(command):
            return True

    # ── OPEN websites ──────────────────────
    if any(w in command for w in OPEN_KEYWORDS):
        for site, url in SITES.items():
            if site in command:
                webbrowser.open(url)
                speak(f"Opening {site.capitalize()}.")
                return True

        for app, exe in APPS.items():
            if app in command:
                try:
                    subprocess.Popen(exe, shell=True)
                    speak(f"Opening {app}.")
                except Exception:
                    speak(f"Couldn't open {app}.")
                return True

        if "chrome" in command:
            try:
                subprocess.Popen(["start", "chrome"], shell=True)
            except Exception:
                webbrowser.open("https://google.com")
            speak("Opening Chrome.")
            return True

    # ── SCREENSHOT ─────────────────────────
    if "screenshot" in command:
        filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(filename)
        speak(f"Screenshot saved as {filename}.")
        return True

    # ── VOLUME ─────────────────────────────
    if any(x in command for x in ["volume up", "increase volume", "louder", "turn up"]):
        for _ in range(5): pyautogui.press("volumeup")
        speak("Volume increased.")
        return True
    if any(x in command for x in ["volume down", "decrease volume", "quieter", "lower volume", "turn down"]):
        for _ in range(5): pyautogui.press("volumedown")
        speak("Volume decreased.")
        return True
    if "mute" in command or "unmute" in command:
        pyautogui.press("volumemute")
        speak("Toggled mute.")
        return True

    return False

# ─────────────────────────────────────────
# 🧩 COMMAND ROUTER
# ─────────────────────────────────────────
def handle_command(user_input):
    """Route user input to the right handler."""

    ui = user_input.lower().strip()

    # ── EXIT ────────────────────────────────
    if any(w in ui for w in ["exit", "shutdown", "goodbye", "bye", "turn off", "stop nexus", "sleep"]):
        name = memory['user_name'] if memory['user_name'] else "friend"
        speak(f"Goodbye {name}! Take care. Nexus shutting down.")
        sys.exit(0)

    # ── TIME ────────────────────────────────
    elif any(w in ui for w in ["what time", "current time", "time is it", "what's the time", "tell me the time"]):
        speak(get_time())

    # ── DATE ────────────────────────────────
    elif any(w in ui for w in ["what date", "what day", "today's date", "day is it", "what's today", "tell me the date"]):
        speak(get_date())

    # ── WEATHER ─────────────────────────────
    elif "weather" in ui:
        city = ui
        for w in ["weather", "in", "what's the", "what is the", "how's the", "tell me", "the"]:
            city = city.replace(w, "").strip()
        speak(get_weather(city if city else "Chennai"))

    # ── REMINDER  (NEW) ─────────────────────
    elif parse_reminder(ui):
        pass

    # ── CALCULATOR  (NEW) ───────────────────
    elif any(w in ui for w in ["calculate", "what is", "what's", "compute", "square root", "multiply", "divide"]):
        if not calculate(ui):
            speak(ask_nexus(user_input))

    # ── CLIPBOARD  (NEW) ────────────────────
    elif any(w in ui for w in ["clipboard", "copy to clipboard"]):
        if not handle_clipboard(ui):
            speak(ask_nexus(user_input))

    # ── WEB SEARCH ──────────────────────────
    elif any(w in ui for w in ["search for", "search", "look up", "find out", "google"]):
        query = ui
        for w in ["search for", "search", "look up", "find out", "find", "google"]:
            query = query.replace(w, "").strip()
        if query:
            speak(f"Searching for {query}...")
            result = search_web(query)
            response = ask_nexus(f"Give a short friendly spoken answer based on this web search result: {result}")
            speak(response)
        else:
            speak("What should I search for?")

    # ── COMPUTER CONTROL ────────────────────
    elif control_computer(ui):
        pass

    # ── AI CONVERSATION ─────────────────────
    else:
        response = ask_nexus(user_input)
        speak(response)

# ─────────────────────────────────────────
# 🚀 MAIN LOOP
# ─────────────────────────────────────────
def run_nexus():

    # ── Startup greeting ──────────────────
    if memory['user_name']:
        speak(f"Welcome back, {memory['user_name']}! Nexus online. What can I do for you?")
    else:
        speak("Hey! Nexus online. What's your name?")

    mode = "voice + text" if VOICE_ENABLED else "text-only"
    print(f"\n💡 Running in {mode} mode.")
    print("💡 Type your message below, or just speak (if mic is ready).")
    print("💡 Say/type 'exit' or 'goodbye' to stop Nexus.\n")
    print("─" * 55)
    print("  NEW FEATURES:")
    print("  ⏰  Reminders  → 'remind me to drink water in 5 minutes'")
    print("  🧮  Calculator → 'calculate 25 times 4'")
    print("  📋  Clipboard  → 'read clipboard'")
    print("  🌐  Sites      → 'open leetcode' / 'open stackoverflow'")
    print("─" * 55 + "\n")

    # ── Voice thread (only if PyAudio works) ──
    if VOICE_ENABLED:
        def voice_loop():
            while True:
                text = listen()
                if text:
                    text = text.replace(WAKE_WORD, "").strip()
                    if len(text) >= 2:
                        print(f"🎙️  You said: {text}")
                        handle_command(text)
        threading.Thread(target=voice_loop, daemon=True).start()

    # ── Text input loop (always active) ───
    while True:
        try:
            user_input = input("⌨️  You: ").strip()
            if not user_input:
                continue
            handle_command(user_input)
        except KeyboardInterrupt:
            speak("Keyboard interrupt. Shutting down. Goodbye!")
            break
        except EOFError:
            break

# ─────────────────────────────────────────
if __name__ == "__main__":
    run_nexus()