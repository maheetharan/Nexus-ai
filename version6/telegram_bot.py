# telegram_bot.py - Nexus on Telegram
# pip install python-telegram-bot
# Get token from @BotFather on Telegram

import requests
import json, os, difflib

TOKEN       = "your-telegram-bot-token"  # 👈 Get from @BotFather
OLLAMA_URL  = "http://localhost:11434/api/generate"
MODEL       = "llama3.2"
MEMORY_FILE = "nexus_memory.json"
TRAINING_FILE = "nexus_training.json"

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ── Memory ──
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE) as f: return json.load(f)
    return {"user_name": None, "facts": []}

memory = load_memory()

# ── Training ──
def check_training(text):
    if not os.path.exists(TRAINING_FILE): return None
    with open(TRAINING_FILE) as f: data = json.load(f)
    for item in data:
        if item["trigger"].lower() in text.lower(): return item["response"]
    return None

# ── AI ──
conversation_history = []

def ask_nexus(user_input):
    trained = check_training(user_input)
    if trained: return trained

    conversation_history.append({"role":"user","content":user_input})
    name_ctx = f"The user's name is {memory['user_name']}." if memory['user_name'] else ""
    history_text = "\n".join([
        f"{'User' if m['role']=='user' else 'Nexus'}: {m['content']}"
        for m in conversation_history[-6:]
    ])
    prompt = f"""You are Nexus, a smart friendly AI assistant built by Mahee.
Keep replies under 3 sentences. Be casual and natural.
{name_ctx}
{history_text}
User: {user_input}
Nexus:"""
    try:
        r = requests.post(OLLAMA_URL,
            json={"model":MODEL,"prompt":prompt,"stream":False}, timeout=30)
        reply = r.json()["response"].strip()
    except:
        reply = "Sorry, I can't connect to my brain right now!"
    conversation_history.append({"role":"assistant","content":reply})
    return reply

# ── Handlers ──
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"Hey {name}! 👋 I'm *Nexus*, your AI assistant built by Mahee.\n"
        f"Just type anything to talk to me! 🤖",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await ctx.bot.send_chat_action(update.effective_chat.id, "typing")
    reply = ask_nexus(user_input)
    await update.message.reply_text(reply)

async def clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    global conversation_history
    conversation_history = []
    await update.message.reply_text("🗑️ Chat cleared!")

# ── Run Bot ──
if __name__ == "__main__":
    print("🤖 Nexus Telegram Bot starting...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot is running! Open Telegram and talk to your bot.")
    app.run_polling()