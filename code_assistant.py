# ╔══════════════════════════════════════════════════════════════╗
# ║         NEXUS v6 - Code Assistant Module                     ║
# ║  Writes, saves, runs Python code and speaks the result       ║
# ╚══════════════════════════════════════════════════════════════╝
# Add this file to your Nexus AI folder
# Then add this line in main.py imports:
#   from code_assistant import handle_code_request, is_code_request

import requests
import subprocess
import os
import sys
import re
import tempfile
import datetime

# ─────────────────────────────────────────
# ⚙️ SETTINGS
# ─────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"
CODER_MODEL  = "qwen2.5-coder:7b"   # Best coding model
FALLBACK_MODEL = "qwen2.5:7b"       # Fallback if coder not installed
CODES_FOLDER = "nexus_codes"        # Folder to save generated code

# Create codes folder if not exists
os.makedirs(CODES_FOLDER, exist_ok=True)

# ─────────────────────────────────────────
# 🔍 DETECT CODE REQUESTS
# ─────────────────────────────────────────
CODE_TRIGGERS = [
    "write a code", "write code", "create a code", "make a code",
    "write a program", "create a program", "make a program",
    "write a script", "create a script",
    "code for", "program for", "script for",
    "write python", "create python", "make python",
    "can you code", "can you program",
    "run this code", "execute this code", "run the code",
    "run code", "execute code",
    "fix this code", "fix my code", "debug this", "debug my code",
    "what does this code do", "explain this code",
    "write a function", "create a function",
    "write a class", "create a class",
]

def is_code_request(user_input):
    """Check if the user is asking for code help."""
    ui = user_input.lower().strip()
    return any(trigger in ui for trigger in CODE_TRIGGERS)

# ─────────────────────────────────────────
# 🧠 GENERATE CODE using Ollama
# ─────────────────────────────────────────
def generate_code(prompt, model=CODER_MODEL):
    """Ask Ollama to write Python code."""

    system = """You are an expert Python programmer.
When asked to write code:
1. Write clean, working Python code
2. Add helpful comments
3. Wrap ALL code inside ```python ... ``` blocks
4. After the code, give a ONE sentence explanation
5. Keep it simple and practical"""

    full_prompt = f"""{system}

User request: {prompt}

Write the Python code now:"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": full_prompt, "stream": False},
            timeout=60
        )
        return response.json()["response"].strip()
    except Exception as e:
        # Try fallback model
        if model != FALLBACK_MODEL:
            print(f"⚠️ {model} failed, trying {FALLBACK_MODEL}...")
            return generate_code(prompt, FALLBACK_MODEL)
        return f"Error generating code: {e}"

# ─────────────────────────────────────────
# 🔍 EXTRACT CODE from AI response
# ─────────────────────────────────────────
def extract_code(ai_response):
    """Pull out just the Python code from AI response."""

    # Try ```python ... ``` block first
    pattern = r"```python\s*(.*?)\s*```"
    matches = re.findall(pattern, ai_response, re.DOTALL)
    if matches:
        return matches[0].strip()

    # Try ``` ... ``` block
    pattern2 = r"```\s*(.*?)\s*```"
    matches2 = re.findall(pattern2, ai_response, re.DOTALL)
    if matches2:
        return matches2[0].strip()

    # If no code block found, return the whole response
    return ai_response.strip()

# ─────────────────────────────────────────
# 💾 SAVE CODE to file
# ─────────────────────────────────────────
def save_code(code, filename=None):
    """Save code to a .py file."""
    if not filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nexus_code_{timestamp}.py"

    filepath = os.path.join(CODES_FOLDER, filename)
    with open(filepath, "w") as f:
        f.write(code)

    return filepath

# ─────────────────────────────────────────
# ▶️ RUN CODE safely
# ─────────────────────────────────────────
def run_code(filepath, timeout=15):
    """
    Run a Python file safely.
    Returns (success, output, error)
    """
    try:
        result = subprocess.run(
            [sys.executable, filepath],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout.strip()
        error  = result.stderr.strip()

        if result.returncode == 0:
            return True, output, None
        else:
            return False, output, error

    except subprocess.TimeoutExpired:
        return False, "", "Code took too long to run (over 15 seconds)."
    except Exception as e:
        return False, "", str(e)

# ─────────────────────────────────────────
# 🔧 FIX CODE using AI
# ─────────────────────────────────────────
def fix_code(code, error_message, model=CODER_MODEL):
    """Ask AI to fix broken code."""
    prompt = f"""Fix this Python code that has an error:

CODE:
```python
{code}
```

ERROR:
{error_message}

Write the FIXED code only:"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60
        )
        return response.json()["response"].strip()
    except:
        return None

# ─────────────────────────────────────────
# 📖 EXPLAIN CODE using AI
# ─────────────────────────────────────────
def explain_code(code, model=FALLBACK_MODEL):
    """Ask AI to explain what code does in simple words."""
    prompt = f"""Explain what this Python code does in 2-3 simple sentences.
Speak like you're explaining to a friend, not writing documentation.

CODE:
```python
{code}
```

Simple explanation:"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30
        )
        return response.json()["response"].strip()
    except:
        return "I couldn't explain the code right now."

# ─────────────────────────────────────────
# 🧩 MAIN HANDLER
# ─────────────────────────────────────────
def handle_code_request(user_input, speak_func, print_func=print):
    """
    Main function to handle all code-related requests.
    speak_func = your Nexus speak() function
    """
    ui = user_input.lower().strip()

    # ── EXPLAIN code ──────────────────────
    if any(w in ui for w in ["explain this code", "what does this code do",
                              "what does this do", "explain the code"]):
        speak_func("Paste your code and I'll explain it!")
        print_func("\n📋 Paste your code below (type END on a new line when done):")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        code = "\n".join(lines)
        if code.strip():
            speak_func("Let me read through your code...")
            explanation = explain_code(code)
            speak_func(explanation)
        return

    # ── FIX / DEBUG code ──────────────────
    if any(w in ui for w in ["fix this code", "fix my code",
                              "debug this", "debug my code"]):
        speak_func("Paste your broken code and I'll fix it!")
        print_func("\n📋 Paste your code (type END when done):")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        code = "\n".join(lines)

        print_func("❌ What's the error message? (press Enter if none):")
        error = input().strip()

        if code.strip():
            speak_func("Looking at your code now...")
            fixed_response = fix_code(code, error or "Unknown error")
            fixed_code = extract_code(fixed_response)

            print_func("\n" + "─"*50)
            print_func("✅ FIXED CODE:")
            print_func("─"*50)
            print_func(fixed_code)
            print_func("─"*50)

            filepath = save_code(fixed_code)
            speak_func(f"I found and fixed the issue! The corrected code is saved. Want me to run it?")

            answer = input("⌨️ Run the fixed code? (yes/no): ").strip().lower()
            if answer in ["yes", "y", "yeah", "yep", "sure"]:
                _run_and_report(fixed_code, filepath, speak_func, print_func)
        return

    # ── RUN existing code ─────────────────
    if any(w in ui for w in ["run this code", "execute this code",
                              "run the code", "run code", "execute code"]):
        speak_func("Paste the code you want me to run!")
        print_func("\n📋 Paste your code (type END when done):")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        code = "\n".join(lines)
        if code.strip():
            filepath = save_code(code)
            _run_and_report(code, filepath, speak_func, print_func)
        return

    # ── WRITE + RUN new code ──────────────
    speak_func("Sure! Let me write that code for you...")
    print_func(f"\n🧠 Generating code for: {user_input}")
    print_func("⏳ Please wait...\n")

    # Generate
    ai_response = generate_code(user_input)
    code = extract_code(ai_response)

    # Show code
    print_func("─"*50)
    print_func("✅ GENERATED CODE:")
    print_func("─"*50)
    print_func(code)
    print_func("─"*50)

    # Save
    filepath = save_code(code)
    print_func(f"\n💾 Saved to: {filepath}")

    speak_func("I've written the code! Want me to run it now?")

    answer = input("⌨️ Run it? (yes/no): ").strip().lower()
    if answer in ["yes", "y", "yeah", "yep", "sure", "run it", "go"]:
        _run_and_report(code, filepath, speak_func, print_func)
    else:
        speak_func(f"Code is saved at {filepath}. You can run it anytime!")

# ─────────────────────────────────────────
# 🏃 RUN & REPORT helper
# ─────────────────────────────────────────
def _run_and_report(code, filepath, speak_func, print_func):
    """Run code and speak the result."""
    speak_func("Running the code now...")
    print_func("\n▶️ Running...\n")

    success, output, error = run_code(filepath)

    if success:
        print_func("─"*50)
        print_func("✅ OUTPUT:")
        print_func("─"*50)
        print_func(output if output else "(No output)")
        print_func("─"*50)

        if output:
            # Speak a short version of output
            short_output = output[:200] if len(output) > 200 else output
            speak_func(f"Code ran successfully! Output is: {short_output}")
        else:
            speak_func("Code ran successfully with no output!")

    else:
        print_func("─"*50)
        print_func("❌ ERROR:")
        print_func("─"*50)
        print_func(error)
        print_func("─"*50)

        speak_func("The code has an error. Let me try to fix it automatically!")
        print_func("\n🔧 Auto-fixing...\n")

        fixed_response = fix_code(code, error)
        if fixed_response:
            fixed_code = extract_code(fixed_response)
            fixed_path = save_code(fixed_code, "fixed_" + os.path.basename(filepath))

            print_func("─"*50)
            print_func("🔧 FIXED CODE:")
            print_func("─"*50)
            print_func(fixed_code)
            print_func("─"*50)

            speak_func("I fixed the error! Running the fixed version now...")
            success2, output2, error2 = run_code(fixed_path)

            if success2:
                short = output2[:200] if len(output2) > 200 else output2
                speak_func(f"Fixed and working! Output: {short}" if output2
                           else "Fixed and running successfully!")
                print_func(f"\n✅ OUTPUT:\n{output2}")
            else:
                speak_func("Still having trouble. The error is shown on screen.")
                print_func(f"\n❌ ERROR:\n{error2}")
        else:
            speak_func("Couldn't fix it automatically. Check the error on screen.")


# ─────────────────────────────────────────
# 🧪 TEST (run standalone)
# ─────────────────────────────────────────
if __name__ == "__main__":
    def test_speak(text):
        print(f"🤖 Nexus: {text}")

    print("🧪 Testing Code Assistant...")
    handle_code_request(
        "write a python code that prints fibonacci sequence first 10 numbers",
        speak_func=test_speak
    )