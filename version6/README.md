# 🤖 NEXUS AI - Multi Platform Setup

## 📁 Files
- web_app.py       → Web browser (ChatGPT-like UI)
- telegram_bot.py  → Telegram bot
- templates/       → HTML files for web UI

---

## 🌐 1. WEB APP (ChatGPT-like UI)

### Install:
pip install flask requests

### Run:
1. Start Ollama:   ollama serve
2. Start Nexus:    python web_app.py
3. Open browser:   http://localhost:5000

Features:
✅ ChatGPT-like chat bubbles
✅ Voice input (mic button)
✅ Voice output (speaks replies)
✅ Works on phone browser too!

---

## 💬 2. TELEGRAM BOT

### Install:
pip install python-telegram-bot

### Setup:
1. Open Telegram → search @BotFather
2. Send /newbot → follow steps
3. Copy the token
4. Paste in telegram_bot.py where it says "your-telegram-bot-token"

### Run:
1. Start Ollama:   ollama serve
2. Start bot:      python telegram_bot.py
3. Open Telegram → find your bot → start chatting!

---

## 📱 3. ANDROID APP (WebView)

No coding needed! Steps:
1. Run web_app.py on your PC
2. Find your PC's IP: ipconfig (look for IPv4 address, e.g. 192.168.1.5)
3. On Android: open Chrome → go to http://192.168.1.5:5000
4. Tap menu → "Add to Home Screen"
   → It works like an app! ✅

OR use MIT App Inventor:
1. Go to: appinventor.mit.edu
2. Create new project
3. Add a WebViewer component
4. Set URL to: http://YOUR_PC_IP:5000
5. Build APK → install on phone!

---

## 🔊 VOICE FEATURES
- Web: Uses browser's built-in speech (works on Chrome!)
- Telegram: Text only (voice needs extra setup)
- Android: Uses Chrome's speech recognition

---

## 📝 TRAIN NEXUS
Edit nexus_training.json to add custom responses.
Nexus learns instantly after save + restart!