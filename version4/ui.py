# web_app.py - Nexus Web Server
# Run: python web_app.py
# Open: http://localhost:5000

from flask import Flask, render_template, request, jsonify, Response
import requests
import os, json, datetime

app = Flask(__name__)

# ─────────────────────────────────────────
# ⚙️ SETTINGS
# ─────────────────────────────────────────
OLLAMA_URL    = "http://localhost:11434/api/generate"
MODEL         = "llama3.2"
GROQ_API_KEY  = "your-groq-api-key"   # backup only
MEMORY_FILE   = "nexus_memory.json"
TRAINING_FILE = "nexus_training.json"

# ─────────────────────────────────────────
# 💾 MEMORY
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
# 🎓 TRAINING DATA
# ─────────────────────────────────────────
def load_training():
    if os.path.exists(TRAINING_FILE):
        with open(TRAINING_FILE, "r") as f:
            return json.load(f)
    return []

import difflib
def check_training(user_input):
    training = load_training()
    ui = user_input.lower().strip()
    for item in training:
        if item["trigger"].lower() in ui:
            return item["response"]
    triggers = [item["trigger"].lower() for item in training]
    close = difflib.get_close_matches(ui, triggers, n=1, cutoff=0.6)
    if close:
        for item in training:
            if item["trigger"].lower() == close[0]:
                return item["response"]
    return None

# ─────────────────────────────────────────
# 🧠 AI BRAIN
# ─────────────────────────────────────────
conversation_history = []

def ask_nexus(user_input):
    # Check training first
    trained = check_training(user_input)
    if trained:
        return trained

    conversation_history.append({"role": "user", "content": user_input})
    if len(conversation_history) > 20:
        del conversation_history[:-20]

    name_ctx = f"The user's name is {memory['user_name']}." if memory['user_name'] else ""
    history_text = ""
    for msg in conversation_history[-6:]:
        role = "User" if msg["role"] == "user" else "Nexus"
        history_text += f"{role}: {msg['content']}\n"

    prompt = f"""You are Nexus, a highly intelligent, witty, and friendly AI assistant built by Mahee.
Be warm, funny, and engaging. Keep responses 2-4 sentences max.
{name_ctx}

{history_text}User: {user_input}
Nexus:"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=30
        )
        reply = response.json()["response"].strip()
    except:
        reply = ask_groq(user_input)

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

def ask_groq(user_input):
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":"You are Nexus, a smart friendly AI. Keep replies short."}] + conversation_history,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except:
        return "Sorry, I'm having trouble connecting. Please make sure Ollama is running!"

# ─────────────────────────────────────────
# 🌐 ROUTES
# ─────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html",
                           user_name=memory.get("user_name", ""))

@app.route("/chat", methods=["POST"])
def chat():
    data       = request.json
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"response": "Say something!"})
    reply = ask_nexus(user_input)
    return jsonify({
        "response": reply,
        "user_name": memory.get("user_name", ""),
        "time": datetime.datetime.now().strftime("%I:%M %p")
    })

@app.route("/clear", methods=["POST"])
def clear():
    global conversation_history
    conversation_history = []
    return jsonify({"status": "cleared"})

@app.route("/memory", methods=["GET"])
def get_memory():
    return jsonify(memory)

if __name__ == "__main__":
    print("🚀 Nexus Web App starting...")
    print("🌐 Open: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)