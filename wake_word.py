# ╔══════════════════════════════════════════════════════════════╗
# ║         NEXUS v6 — Wake Word Module                          ║
# ║         Say "Hey Nexus" to activate hands-free               ║
# ╚══════════════════════════════════════════════════════════════╝
# No extra install needed — uses speech_recognition

import speech_recognition as sr
import threading
import time

# ─────────────────────────────────────────
# ⚙️ SETTINGS
# ─────────────────────────────────────────
WAKE_PHRASES = [
    "hey nexus", "ok nexus", "nexus", "hi nexus",
    "hello nexus", "aye nexus", "a nexus"
]
SLEEP_PHRASES = [
    "nexus sleep", "go to sleep", "nexus stop listening",
    "nexus休息"
]

# State
_is_awake    = False
_wake_callback = None  # Called when wake word heard
_sleep_callback = None # Called when sleep word heard

# ─────────────────────────────────────────
# 🔊 STATE MANAGEMENT
# ─────────────────────────────────────────
def set_awake(val):
    global _is_awake
    _is_awake = val

def is_awake():
    return _is_awake

def on_wake(callback):
    """Register function to call when wake word detected."""
    global _wake_callback
    _wake_callback = callback

def on_sleep(callback):
    """Register function to call when sleep word detected."""
    global _sleep_callback
    _sleep_callback = callback

# ─────────────────────────────────────────
# 🎙️ WAKE WORD LISTENER
# ─────────────────────────────────────────
def _listen_for_wake():
    """
    Continuously listens in background.
    Short timeout = fast response to wake word.
    """
    global _is_awake
    r = sr.Recognizer()
    r.energy_threshold        = 2500
    r.dynamic_energy_threshold = True
    r.pause_threshold          = 0.5

    while True:
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.2)
                audio = r.listen(source, timeout=3, phrase_time_limit=3)

            text = r.recognize_google(audio, language="en-IN").lower()

            # ── Check wake word ──────────────
            if not _is_awake:
                if any(p in text for p in WAKE_PHRASES):
                    _is_awake = True
                    print(f"\n✅ Wake word detected: '{text}'")
                    if _wake_callback:
                        _wake_callback()

            # ── Check sleep word ─────────────
            else:
                if any(p in text for p in SLEEP_PHRASES):
                    _is_awake = False
                    print("\n😴 Going to sleep mode...")
                    if _sleep_callback:
                        _sleep_callback()

        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except Exception as e:
            time.sleep(1)

# ─────────────────────────────────────────
# 🚀 START WAKE WORD LISTENER
# ─────────────────────────────────────────
def start_wake_word_listener():
    """Start wake word detection in background thread."""
    t = threading.Thread(target=_listen_for_wake, daemon=True)
    t.start()
    print("👂 Wake word listener active — say 'Hey Nexus'!")
    return t