# ╔══════════════════════════════════════════╗
# ║       NEXUS AI - Version 1.0             ║
# ║       Basic Chatbot (Text Only)          ║
# ║       Brain: Groq API                    ║
# ╚══════════════════════════════════════════╝
# pip install groq

from groq import Groq

# ─────────────────────────────────────────
# ⚙️ SETTINGS
# ─────────────────────────────────────────
GROQ_API_KEY = "your-groq-api-key-here"  # https://console.groq.com

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
            {"role": "system", "content": "You are Nexus, a smart friendly AI assistant. Keep replies short and casual."}
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
    print("🤖 Nexus v1.0 Online!")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "bye", "quit"]:
            print("Nexus: Goodbye!")
            break
        reply = ask_nexus(user_input)
        print(f"Nexus: {reply}\n")

if __name__ == "__main__":
    run()