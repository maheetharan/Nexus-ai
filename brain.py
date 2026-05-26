# brain.py - Nexus AI Brain (Uses Ollama - No API Key Needed!)
import requests
import os
import json

# ─────────────────────────────────────────
# ⚙️ SETTINGS
# ─────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"     # ✅ Your local model (no API key!)
MEMORY_FILE  = "nexus_memory.json"

# ─────────────────────────────────────────
# 💾 MEMORY (Remembers your name)
# ─────────────────────────────────────────
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"user_name": None, "facts": []}

def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)

memory = load_memory()

# ─────────────────────────────────────────
# 🌐 CHECK INTERNET
# ─────────────────────────────────────────
def is_internet_available():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False

# ─────────────────────────────────────────
# 🧠 CONVERSATION HISTORY
# ─────────────────────────────────────────
conversation_history = []

# ─────────────────────────────────────────
# 🤖 ASK NEXUS (Uses your local Ollama)
# ─────────────────────────────────────────
def ask_nexus(user_input):
    # Add user message to history
    conversation_history.append({"role": "user", "content": user_input})

    # Personal context
    name_ctx = f"The user's name is {memory['user_name']}." if memory['user_name'] else ""

    # Build conversation history as text
    history_text = ""
    for msg in conversation_history[-6:]:   # Last 3 exchanges
        role = "User" if msg["role"] == "user" else "Nexus"
        history_text += f"{role}: {msg['content']}\n"

    # Build the prompt
    prompt = f"""You are Nexus, a smart, witty, and friendly AI assistant — like a best friend who is very intelligent.
Keep ALL replies under 2-3 short sentences since they will be spoken out loud.
Be casual and natural. Never sound robotic.
{name_ctx}

{history_text}User: {user_input}
Nexus:"""

    # ── Try Ollama (Local - No internet needed) ──
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        reply = response.json()["response"].strip()
        print(f"💻 Using Local AI ({MODEL})")

    except Exception as e:
        # ── Fallback to Groq if Ollama fails ──
        print(f"⚠️ Ollama failed: {e}")
        print("🌐 Falling back to Groq API...")
        reply = ask_groq_fallback(user_input)

    # Save to history
    conversation_history.append({"role": "assistant", "content": reply})

    # ── Learn user's name automatically ──
    if memory["user_name"] is None:
        for phrase in ["my name is ", "i am ", "call me ", "i'm "]:
            if phrase in user_input.lower():
                after = user_input.lower().split(phrase)[-1].strip()
                name  = after.split()[0].replace(",", "").replace(".", "").capitalize()
                if len(name) >= 2:
                    memory["user_name"] = name
                    save_memory(memory)
                    break

    return reply

# ─────────────────────────────────────────
# 🔄 GROQ FALLBACK (Only if Ollama fails)
# ─────────────────────────────────────────
GROQ_API_KEY = "your-groq-api-key-here"   # Optional backup

def ask_groq_fallback(user_input):
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        name_ctx = f"The user's name is {memory['user_name']}." if memory['user_name'] else ""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are Nexus, a smart friendly AI assistant. Keep replies short (2-3 sentences). Be casual. {name_ctx}"},
            ] + conversation_history,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except:
        return "Sorry, I'm having trouble thinking right now. Please make sure Ollama is running!"