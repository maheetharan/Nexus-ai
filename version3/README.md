# 🤖 Nexus AI Voice Assistant

A smart, voice-controlled AI assistant powered by Groq's LLaMA 3 model. Talk to Nexus naturally — it can answer questions, search the web, open apps, control your system, and remember past conversations.

---

## 🎬 Demo
<img width="1235" height="924" alt="Screenshot 2026-05-23 165221" src="https://github.com/user-attachments/assets/5a82f601-17a5-4a70-96dd-65f8da611cec" />
<img width="1047" height="940" alt="Screenshot 2026-05-23 165240" src="https://github.com/user-attachments/assets/f962208e-7b43-41a5-b94d-5f9860dd706e" />
<img width="1125" height="959" alt="Screenshot 2026-05-23 165256" src="https://github.com/user-attachments/assets/e8513683-b7f0-4fcb-8141-80976cbae2be" />


---

## ✨ Features

- 🎙️ **Voice Input & Output** — speak naturally, get spoken responses
- 🧠 **AI-Powered** — uses Groq API with LLaMA 3.3 70B model
- 🌐 **Web Search** — searches the internet for real-time information
- 💻 **System Control** — opens apps, websites, and controls your PC
- 🧠 **Persistent Memory** — remembers your preferences across sessions
- 🖥️ **Clean UI** — built with a simple Python GUI

---

## 🛠️ Tech Stack

| Technology | Usage |
|------------|-------|
| Python | Core programming language |
| Groq API | LLaMA 3.3 70B AI model |
| SpeechRecognition | Voice input |
| pyttsx3 / gTTS | Voice output |
| Tkinter / CustomTkinter | GUI |
| python-dotenv | Secure API key management |

---

## 📦 Installation

1. Clone the repository
```bash
git clone https://github.com/maheetharan/Nexus-AI-Voice-Assistant.git
cd Nexus-AI-Voice-Assistant
```

2. Install dependencies
```bash
pip install groq speechrecognition pyttsx3 python-dotenv
```

3. Create a `.env` file in the root folder
```
GROQ_API_KEY=your_groq_api_key_here
```

4. Run the assistant
```bash
python main.py
```

---

## 🔑 Getting a Groq API Key

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Generate an API key
4. Paste it in your `.env` file

---

## 📁 Project Structure

```
Nexus-AI-Voice-Assistant/
├── main.py          # Entry point
├── brain.py         # AI logic & Groq API integration
├── ui.py            # GUI interface
├── system_contrl.py # System control functions
├── Ai bot.py        # Core bot logic
├── test_mic.py      # Microphone test utility
├── .env             # API keys (not uploaded)
├── .gitignore
└── README.md
```

---

## ⚠️ Important

Never share your `.env` file or commit it to GitHub. Your API key should always stay private.

---

## 👨‍💻 Author

**Maheetharan**
- GitHub: [@maheetharan](https://github.com/maheetharan)
- LinkedIn: [Your LinkedIn]
- B.Tech AI & Data Science, Kamaraj College of Engineering & Technology

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).
