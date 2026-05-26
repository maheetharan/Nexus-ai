import speech_recognition as sr

r = sr.Recognizer()
mics = sr.Microphone.list_microphone_names()

print("Available microphones:")
for i, mic in enumerate(mics):
    print(f"  [{i}] {mic}")

print("\nSpeak something for 5 seconds...")
with sr.Microphone() as source:
    r.energy_threshold = 400        # lower = more sensitive
    r.adjust_for_ambient_noise(source, duration=1)
    print(f"Energy threshold set to: {r.energy_threshold:.0f}")
    print("Listening now — say something!")
    try:
        audio = r.listen(source, timeout=5, phrase_time_limit=5)
        text = r.recognize_google(audio)
        print(f"✅ You said: {text}")
    except sr.WaitTimeoutError:
        print("❌ Timeout — mic heard nothing. Check mic volume in Windows settings.")
    except sr.UnknownValueError:
        print("⚠️ Heard audio but couldn't understand. Speak louder/clearer.")
    except Exception as e:
        print(f"Error: {e}")