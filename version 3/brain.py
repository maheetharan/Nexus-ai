#brain.py
from groq import Groq
import requests

# ─────────────────────────────────────────
# ⚙️ SETTINGS
# ─────────────────────────────────────────
GROQ_API_KEY = "Your_Groq_API_Key_Here"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

client = Groq(api_key=GROQ_API_KEY)
conversation_history = []

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
# 🤖 LOCAL AI (Ollama - Offline)
# ─────────────────────────────────────────
def ask_local_ai(user_input, memory=None):
    try:
        name_context = f"The user's name is {memory['user_name']}." if memory and memory.get('user_name') else ""
        
        # Build conversation context from history
        history_text = ""
        for msg in conversation_history[-6:]:  # Last 3 exchanges
            role = "User" if msg["role"] == "user" else "Nexus"
            history_text += f"{role}: {msg['content']}\n"

        prompt = f"""You are Nexus, a friendly, smart AI assistant.
Keep replies under 2 short sentences. Be casual and natural.
{name_context}

{history_text}User: {user_input}
Nexus:"""

        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=30)

        return response.json()["response"].strip()
    except Exception as e:
        return f"Local AI error: {str(e)}"

# ─────────────────────────────────────────
# ☁️ GROQ AI (Online)
# ─────────────────────────────────────────
def ask_groq_ai(user_input, memory=None):
    name_context = f"The user's name is {memory['user_name']}." if memory and memory.get('user_name') else ""

    system_prompt = f"""You are Nexus, a futuristic Jarvis-style AI assistant.
Keep responses short and intelligent.
{name_context}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt}
        ] + conversation_history,
        max_tokens=150
    )

    return response.choices[0].message.content.strip()

# ─────────────────────────────────────────
# 🧠 MAIN ASK FUNCTION (Auto Switch)
# ─────────────────────────────────────────
def ask_nexus(user_input, memory=None):
    conversation_history.append({"role": "user", "content": user_input})

    if is_internet_available():
        print("🌐 Using Groq AI (Online)")
        try:
            reply = ask_groq_ai(user_input, memory)
        except Exception as e:
            print(f"⚠️ Groq failed: {e}. Switching to local AI...")
            reply = ask_local_ai(user_input, memory)
    else:
        print("📴 No internet. Using Local Mistral AI (Offline)")
        reply = ask_local_ai(user_input, memory)

    conversation_history.append({"role": "assistant", "content": reply})

    # Learn name
    if memory and memory.get("user_name") is None:
        if "my name is" in user_input:
            name = user_input.split("my name is")[-1].strip().split()[0]
            memory["user_name"] = name.capitalize()

    return reply