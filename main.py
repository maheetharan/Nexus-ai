# ╔══════════════════════════════════════════════════════════════╗
# ║              NEXUS - AI Voice Assistant v5.0                 ║
# ║    Better Recognition + Custom Training + Local Ollama       ║
# ╚══════════════════════════════════════════════════════════════╝

import speech_recognition as sr
import pyttsx3
import pyautogui
import subprocess
import webbrowser
import datetime
import requests
import os, sys, json, time, threading, difflib
from code_assistant import handle_code_request, is_code_request
from wake_word        import start_wake_word_listener, is_awake, set_awake
from tamil_support    import handle_tamil, speak_tamil, needs_tamil_response
from live_updates     import handle_live_update, is_update_request
from whatsapp_control import handle_whatsapp, is_whatsapp_request

try:
    from ddgs import DDGS
except:
    from duckduckgo_search import DDGS

# ─────────────────────────────────────────
# ⚙️ SETTINGS
# ─────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"
MODEL        = "llama3.2"
GROQ_API_KEY = "your-groq-api-key"
WAKE_WORD    = "nexus"
MEMORY_FILE  = "nexus_memory.json"
TRAINING_FILE= "nexus_training.json"
MAX_HISTORY  = 20

# ─────────────────────────────────────────
# 🔍 CHECK PYAUDIO
# ─────────────────────────────────────────
VOICE_ENABLED = True
try:
    import pyaudio
    pa = pyaudio.PyAudio(); pa.terminate()
except:
    VOICE_ENABLED = False
    print("⚠️  PyAudio not found — TEXT-ONLY mode.\n")

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
        json.dump(memory, f, indent=2)

memory = load_memory()

# ─────────────────────────────────────────
# 🎓 TRAINING DATA (Custom Q&A)
# ─────────────────────────────────────────
def load_training():
    """Load custom training data from nexus_training.json"""
    if os.path.exists(TRAINING_FILE):
        with open(TRAINING_FILE, "r") as f:
            return json.load(f)
    # ── Create default training file if not exists ──
    default_training = [
        {"trigger": "who created you",        "response": "I was created by Mahee, a brilliant AI student from Tamil Nadu!"},
        {"trigger": "who made you",            "response": "Mahee built me from scratch — pretty impressive, right?"},
        {"trigger": "who are you",             "response": "I'm Nexus, your personal AI assistant built by Mahee!"},
        {"trigger": "what is your name",       "response": "My name is Nexus. Built by Mahee to be the smartest assistant around!"},
        {"trigger": "what can you do",         "response": "I can open apps, search the web, do math, set reminders, check weather, and have real conversations with you!"},
        {"trigger": "your purpose",            "response": "My purpose is to make Mahee's life easier and more productive!"},
        {"trigger": "unakku tamil theriyuma",  "response": "Konjam konjam theriyum! Naan Nexus, Mahee uruthaana AI assistant!"},
        {"trigger": "en peyar enna",           "response": "Unnoda peyar Mahee! Naan maranthudalaam, aana nee maranthudalai!"},
        {"trigger": "how are you",             "response": "I'm running at full power and ready to help you, Mahee!"},
        {"trigger": "good morning",            "response": "Good morning Mahee! Ready to have a productive day?"},
        {"trigger": "good night",              "response": "Good night Mahee! Rest well, I'll be here when you need me!"}
    ]
    with open(TRAINING_FILE, "w") as f:
        json.dump(default_training, f, indent=2)
    print(f"✅ Created {TRAINING_FILE} — you can edit it to train Nexus!")
    return default_training

training_data = load_training()

def check_training(user_input):
    """
    Check if user input matches any trained response.
    Uses fuzzy matching — so 'who built u' matches 'who made you'
    """
    ui = user_input.lower().strip()

    # ── Exact match first ──
    for item in training_data:
        if item["trigger"].lower() in ui:
            return item["response"]

    # ── Fuzzy match (catches similar phrases) ──
    triggers = [item["trigger"].lower() for item in training_data]
    close    = difflib.get_close_matches(ui, triggers, n=1, cutoff=0.6)
    if close:
        for item in training_data:
            if item["trigger"].lower() == close[0]:
                return item["response"]

    return None  # No match found

# ─────────────────────────────────────────
# 🔊 VOICE OUTPUT
# ─────────────────────────────────────────
# ─────────────────────────────────────────
# 🔊 VOICE OUTPUT
# ─────────────────────────────────────────
from gtts import gTTS
import pygame
import tempfile

engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

voices = engine.getProperty('voices')
for voice in voices:
    if any(n in voice.name.lower() for n in ["male","david","mark","george"]):
        engine.setProperty('voice', voice.id)
        break

def speak(text, lang="en"):
    if lang == "ta":
        speak_tamil(text)
        return
    print(f"🤖 Nexus: {text}")
    engine.say(text)
    engine.runAndWait()

# ─────────────────────────────────────────
# 🎙️ VOICE INPUT — Improved Recognition
# ─────────────────────────────────────────

# ── Word corrections (what Google hears → what you meant) ──
WORD_CORRECTIONS = {
    "lead code":        "leetcode",
    "lead cot":         "leetcode",
    "leet cot":         "leetcode",
    "lit code":         "leetcode",
    "light code":       "leetcode",
    "l e e t c":        "leetcode",
    "led code":         "leetcode",
    "guitar":           "github",
    "get hub":          "github",
    "git hub":          "github",
    "you tube":         "youtube",
    "insta gram":       "instagram",
    "whats app":        "whatsapp",
    "what's app":       "whatsapp",
    "stack overflow":   "stackoverflow",
    "stack over flow":  "stackoverflow",
    "linked in":        "linkedin",
    "you tuber":        "youtube",
    "goggle":           "google",
    "goo gal":          "google",
    "g mail":           "gmail",
    "net flicks":       "netflix",
    "net flex":         "netflix",
    "hu r u":           "how are you",
    "hu are u":         "how are you",
    "r u there":        "are you there",
    "wat u doing":      "what are you doing",
    "wat r u":          "what are you",
}

def correct_speech(text):
    """Fix common speech recognition mistakes."""
    corrected = text.lower()
    for wrong, right in WORD_CORRECTIONS.items():
        corrected = corrected.replace(wrong, right)
    return corrected

def listen(timeout=6):
    if not VOICE_ENABLED:
        return ""
    r = sr.Recognizer()

    # ── Better recognition settings ──
    r.pause_threshold        = 0.8   # Wait longer before stopping
    r.phrase_threshold       = 0.3
    r.non_speaking_duration  = 0.5

    try:
        with sr.Microphone() as source:
            print("🎙️  Listening...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            r.dynamic_energy_threshold = True
            audio = r.listen(source, timeout=timeout, phrase_time_limit=12)

            # ── Try Google first, fallback to Sphinx ──
            try:
                text = r.recognize_google(
                    audio,
                    language="en-IN"  # ✅ Indian English — better for your accent!
                )
                text = correct_speech(text)
                return text.lower()
            except sr.UnknownValueError:
                return ""

    except sr.WaitTimeoutError:
        return ""
    except OSError as e:
        print(f"🎤 Mic error: {e}")
        return ""
    except Exception as e:
        print(f"🎤 Error: {e}")
        return ""

# ─────────────────────────────────────────
# 🧠 AI BRAIN — Ollama
# ─────────────────────────────────────────
conversation_history = []

def ask_nexus(user_input):
    conversation_history.append({"role": "user", "content": user_input})
    if len(conversation_history) > MAX_HISTORY:
        del conversation_history[:-MAX_HISTORY]

    name_ctx = f"The user's name is {memory['user_name']}." if memory['user_name'] else ""

    history_text = ""
    for msg in conversation_history[-6:]:
        role = "User" if msg["role"] == "user" else "Nexus"
        history_text += f"{role}: {msg['content']}\n"

    prompt = f"""You are Nexus, a highly intelligent, witty, and friendly AI voice assistant built by Mahee.
You love having real conversations. Be warm, funny, supportive, and engaging.
{name_ctx}
STRICT RULES:
- Keep ALL responses under 2-3 short sentences — they will be SPOKEN OUT LOUD.
- Be casual and natural, like talking to a close friend.
- Never say you don't have access to the computer.
- Be direct and confident, never robotic.

{history_text}User: {user_input}
Nexus:"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=30
        )
        reply = response.json()["response"].strip()
        print(f"💻 Local AI ({MODEL})")
    except Exception as e:
        print(f"⚠️ Ollama failed ({e}). Trying Groq...")
        reply = ask_groq_fallback(user_input)

    conversation_history.append({"role": "assistant", "content": reply})

    # Learn name
    if memory['user_name'] is None:
        for phrase in ["my name is ","i am ","call me ","i'm "]:
            if phrase in user_input.lower():
                after = user_input.lower().split(phrase)[-1].strip()
                parts = after.split()
                if parts:
                    name = parts[0].replace(",","").replace(".","").capitalize()
                    if len(name) >= 2:
                        memory['user_name'] = name
                        save_memory(memory)
                break

    return reply

# ─────────────────────────────────────────
# 🔄 GROQ FALLBACK
# ─────────────────────────────────────────
def ask_groq_fallback(user_input):
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        name_ctx = f"The user's name is {memory['user_name']}." if memory['user_name'] else ""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":f"You are Nexus, a smart friendly AI built by Mahee. Keep replies short. {name_ctx}"}
            ] + conversation_history,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except:
        return "Sorry, Ollama isn't running! Please open CMD and type: ollama serve"

# ─────────────────────────────────────────
# 🌦️ WEATHER
# ─────────────────────────────────────────
def get_weather(city="Chennai"):
    try:
        url = f"https://wttr.in/{city.strip() or 'Chennai'}?format=3"
        return requests.get(url, timeout=5).text.strip()
    except:
        return "Couldn't fetch weather right now."

# ─────────────────────────────────────────
# 🕐 TIME & DATE
# ─────────────────────────────────────────
def get_time():
    return f"It's {datetime.datetime.now().strftime('%I:%M %p')}."

def get_date():
    return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."

# ─────────────────────────────────────────
# ⏰ REMINDERS
# ─────────────────────────────────────────
def set_reminder(text, seconds):
    def _fire():
        time.sleep(seconds)
        speak(f"Reminder: {text}")
    threading.Thread(target=_fire, daemon=True).start()
    speak(f"Got it! Reminding you about '{text}' in {seconds//60 if seconds>=60 else seconds} {'minutes' if seconds>=60 else 'seconds'}.")

def parse_reminder(user_input):
    if not any(t in user_input for t in ["remind me","set a reminder","reminder for"]):
        return False
    seconds = None
    for word in user_input.split():
        if word.isdigit():
            if "minute" in user_input:   seconds = int(word) * 60
            elif "hour" in user_input:   seconds = int(word) * 3600
            elif "second" in user_input: seconds = int(word)
            break
    if seconds is None:
        speak("How many minutes should I set it for?")
        return True
    task = user_input
    for p in ["remind me to","remind me about","set a reminder for","reminder for","remind me",
              "in","minutes","minute","hours","hour","seconds","second"]:
        task = task.replace(p,"").strip()
    task = " ".join(w for w in task.split() if not w.isdigit()).strip() or "that"
    set_reminder(task, seconds)
    return True

# ─────────────────────────────────────────
# 🧮 CALCULATOR
# ─────────────────────────────────────────
def calculate(user_input):
    import math
    try:
        expr = user_input.lower()
        for word in ["calculate","what is","what's","compute","solve"]:
            expr = expr.replace(word,"").strip()
        expr = (expr.replace("plus","+").replace("minus","-")
                    .replace("times","*").replace("multiplied by","*")
                    .replace("multiply","*").replace("divided by","/")
                    .replace("divide","/").strip())
        if "square root of" in expr:
            num = float(expr.replace("square root of","").strip())
            speak(f"Square root of {num} is {math.sqrt(num):.4g}.")
            return True
        if "power of" in expr:
            expr = expr.replace("to the power of","**").replace("power of","**")
        if any(c in expr for c in "0123456789"):
            result = eval(expr, {"__builtins__":{}}, {"sqrt":math.sqrt,"pi":math.pi})
            speak(f"That's {result:.4g}.")
            return True
    except:
        pass
    return False

# ─────────────────────────────────────────
# 📋 CLIPBOARD
# ─────────────────────────────────────────
def handle_clipboard(user_input):
    try:
        import tkinter as tk
        if any(w in user_input for w in ["read clipboard","what's in clipboard","clipboard content"]):
            root = tk.Tk(); root.withdraw()
            content = root.clipboard_get(); root.destroy()
            speak(f"Clipboard says: {content[:150]}")
            return True
        if "copy" in user_input and "to clipboard" in user_input:
            text = user_input.replace("copy","").replace("to clipboard","").strip()
            root = tk.Tk(); root.withdraw()
            root.clipboard_clear(); root.clipboard_append(text); root.update(); root.destroy()
            speak(f"Copied: {text}")
            return True
    except:
        speak("Clipboard operation failed.")
    return False

# ─────────────────────────────────────────
# 🌐 WEB SEARCH
# ─────────────────────────────────────────
def search_web(query):
    try:
        ddgs    = DDGS()
        results = list(ddgs.text(query, max_results=3))
        if results:
            summary = " ".join([r.get('body','') for r in results if r.get('body')])
            return summary[:800] if summary else "No detailed results found."
        return "No results found."
    except Exception as e:
        return f"Search failed: {e}"

# ─────────────────────────────────────────
# ❌ CLOSE APPS
# ─────────────────────────────────────────
PROCESS_MAP = {
    "chrome":"chrome.exe",       "google":"chrome.exe",
    "youtube":"chrome.exe",      "firefox":"firefox.exe",
    "notepad":"notepad.exe",     "calculator":"calc.exe",
    "paint":"mspaint.exe",       "spotify":"spotify.exe",
    "vlc":"vlc.exe",             "word":"winword.exe",
    "excel":"excel.exe",         "powerpoint":"powerpnt.exe",
    "teams":"teams.exe",         "discord":"discord.exe",
}

def close_app(command):
    for app_name, process in PROCESS_MAP.items():
        if app_name in command:
            result = subprocess.run(f"taskkill /f /im {process}",
                                    shell=True, capture_output=True, text=True)
            speak(f"Closed {app_name.capitalize()}." if result.returncode==0
                  else f"{app_name.capitalize()} isn't open.")
            return True
    return False

# ─────────────────────────────────────────
# 💻 OPEN APPS / WEBSITES
# ─────────────────────────────────────────
SITES = {
    "youtube":"https://youtube.com",       "google":"https://google.com",
    "instagram":"https://instagram.com",   "whatsapp":"https://web.whatsapp.com",
    "spotify":"https://open.spotify.com",  "facebook":"https://facebook.com",
    "twitter":"https://twitter.com",       "netflix":"https://netflix.com",
    "gmail":"https://mail.google.com",     "github":"https://github.com",
    "reddit":"https://reddit.com",         "amazon":"https://amazon.in",
    "linkedin":"https://linkedin.com",     "leetcode":"https://leetcode.com",
    "stackoverflow":"https://stackoverflow.com",
    "chatgpt":"https://chatgpt.com",       "figma":"https://figma.com",
    "google maps":"https://maps.google.com","maps":"https://maps.google.com",
    "google map":"https://maps.google.com",
}

APPS = {
    "notepad":"notepad.exe",         "calculator":"calc.exe",
    "paint":"mspaint.exe",           "file explorer":"explorer.exe",
    "task manager":"taskmgr.exe",    "command prompt":"cmd.exe",
    "cmd":"cmd.exe",                 "vs code":"code",
    "visual studio code":"code",     "android studio":"studio64.exe",
}

OPEN_KEYWORDS  = ["open","go","launch","start","take me","show","load"]
CLOSE_KEYWORDS = ["close","shut","kill","terminate"]

def control_computer(command):
    if any(w in command for w in CLOSE_KEYWORDS):
        if close_app(command): return True

    if any(w in command for w in OPEN_KEYWORDS):
        # Check multi-word sites first (e.g. "google maps" before "google")
        for site in sorted(SITES.keys(), key=len, reverse=True):
            if site in command:
                webbrowser.open(SITES[site])
                speak(f"Opening {site.capitalize()}.")
                return True
        for app, exe in APPS.items():
            if app in command:
                try:
                    subprocess.Popen(exe, shell=True)
                    speak(f"Opening {app}.")
                except:
                    speak(f"Couldn't open {app}.")
                return True
        if "chrome" in command:
            try: subprocess.Popen(["start","chrome"], shell=True)
            except: webbrowser.open("https://google.com")
            speak("Opening Chrome.")
            return True

    if "screenshot" in command:
        filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(filename)
        speak(f"Screenshot saved!")
        return True
    if any(x in command for x in ["volume up","increase volume","louder","turn up"]):
        for _ in range(5): pyautogui.press("volumeup")
        speak("Volume increased."); return True
    if any(x in command for x in ["volume down","decrease volume","quieter","lower volume","turn down"]):
        for _ in range(5): pyautogui.press("volumedown")
        speak("Volume decreased."); return True
    if "mute" in command or "unmute" in command:
        pyautogui.press("volumemute"); speak("Toggled mute."); return True

    return False

# ─────────────────────────────────────────
# 🧩 COMMAND ROUTER
# ─────────────────────────────────────────
def handle_command(user_input):
    ui = user_input.lower().strip()

    # ── Exit ──────────────────────────────
    if any(w in ui for w in ["exit","shutdown","goodbye","bye","stop nexus"]):
        name = memory['user_name'] or "friend"
        speak(f"Goodbye {name}! Take care.")
        import sys; sys.exit(0)

    # ── Tamil Support ─────────────────────
    elif needs_tamil_response(user_input):
        response, is_ta = handle_tamil(user_input, memory)
        if is_ta and response:
            speak_tamil(response)
            return
 
    # ── Wake word state ───────────────────
    elif any(w in ui for w in ["nexus sleep","go to sleep"]):
        set_awake(False)
        speak("Going to sleep. Say Hey Nexus to wake me!")
        return
 
    # ── Training data (custom responses) ──
    trained = check_training(ui)
    if trained:
        speak(trained)
        return

    # ── Time ──────────────────────────────
    elif any(w in ui for w in ["what time","current time","time is it","what's the time"]):
        speak(get_time())

    # ── Date ──────────────────────────────
    elif any(w in ui for w in ["what date","what day","today's date","day is it","what's today"]):
        speak(get_date())

    # ── Weather ───────────────────────────
    elif "weather" in ui:
        city = ui
        for w in ["weather","in","what's the","what is the","how's the","tell me","the"]:
            city = city.replace(w,"").strip()
        speak(get_weather(city or "Chennai"))

    # ── Reminder ──────────────────────────
    elif parse_reminder(ui):
        pass

    # ── Calculator ────────────────────────
    elif any(w in ui for w in ["calculate","compute","square root","multiply","divide"]):
        if not calculate(ui): speak(ask_nexus(user_input))
    elif any(w in ui for w in ["what is","what's"]) and any(c in ui for c in "0123456789"):
        if not calculate(ui): speak(ask_nexus(user_input))

    # ── Clipboard ─────────────────────────
    elif any(w in ui for w in ["clipboard","copy to clipboard"]):
        if not handle_clipboard(ui): speak(ask_nexus(user_input))

    # ── Search ────────────────────────────
    elif any(w in ui for w in ["search for","search","look up","find out"]):
        query = ui
        for w in ["search for","search","look up","find out","find"]:
            query = query.replace(w,"").strip()
        if query:
            speak(f"Searching for {query}...")
            result   = search_web(query)
            response = ask_nexus(f"Give a short friendly spoken answer based on this search: {result}")
            speak(response)
        else:
            speak("What should I search for?")
    elif is_code_request(ui):
        handle_code_request(user_input, speak)
    # ── Computer Control ──────────────────
    elif control_computer(ui):
        pass

    # ── AI Conversation ───────────────────
    else:
        speak(ask_nexus(user_input))

# ─────────────────────────────────────────
# 🚀 MAIN
# ─────────────────────────────────────────
def run_nexus():
    if memory['user_name']:
        speak(f"Welcome back, {memory['user_name']}! Nexus online.")
    else:
        speak("Hey! Nexus online. What's your name?")

    mode = "voice + text" if VOICE_ENABLED else "text-only"
    print(f"\n💡 Running in {mode} mode.")
    print(f"💡 Training file: {TRAINING_FILE} (edit to add custom responses!)")
    print("💡 Say/type 'exit' to stop.\n")
    print("─" * 55)
    print("  ⏰  'remind me to drink water in 5 minutes'")
    print("  🧮  'calculate 25 times 4'")
    print("  📋  'read clipboard'")
    print("  🌐  'open leetcode' / 'open google maps'")
    print("  🎓  Edit nexus_training.json to train Nexus!")
    print("─" * 55 + "\n")

    if VOICE_ENABLED:
        def voice_loop():
            while True:
                text = listen()
                if text:
                    text = text.replace(WAKE_WORD,"").strip()
                    if len(text) >= 2:
                        print(f"🎙️  You said: {text}")
                        handle_command(text)
        threading.Thread(target=voice_loop, daemon=True).start()

    while True:
        try:
            user_input = input("⌨️  You: ").strip()
            if not user_input: continue
            handle_command(user_input)
        except KeyboardInterrupt:
            speak("Shutting down. Goodbye!")
            break
        except EOFError:
            break

if __name__ == "__main__":
    run_nexus()