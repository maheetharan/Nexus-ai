# ╔══════════════════════════════════════════════════════════════╗
# ║         NEXUS v6 — WhatsApp Control Module                   ║
# ║         Send messages, schedule messages via voice           ║
# ╚══════════════════════════════════════════════════════════════╝
# pip install pywhatkit pyautogui

import pywhatkit as kit
import datetime
import time
import re

# ─────────────────────────────────────────
# 📒 CONTACTS (Add your contacts here)
# ─────────────────────────────────────────
CONTACTS = {
    # Add your contacts here
    # "name": "+91XXXXXXXXXX",
    "amma":   "+91XXXXXXXXXX",   # 👈 Replace with real numbers
    "appa":   "+91XXXXXXXXXX",
    "friend": "+91XXXXXXXXXX",
    "ramkumar": "+91XXXXXXXXXX",
}

# ─────────────────────────────────────────
# 🔍 DETECT WHATSAPP REQUESTS
# ─────────────────────────────────────────
WHATSAPP_TRIGGERS = [
    "send whatsapp", "whatsapp message", "send message to",
    "message to", "text to", "send a message",
    "whatsapp to", "send whatsapp to"
]

def is_whatsapp_request(user_input):
    ui = user_input.lower()
    return any(t in ui for t in WHATSAPP_TRIGGERS)

# ─────────────────────────────────────────
# 📱 EXTRACT CONTACT & MESSAGE
# ─────────────────────────────────────────
def extract_contact(user_input):
    """Try to find contact name in the command."""
    ui = user_input.lower()
    for name, number in CONTACTS.items():
        if name.lower() in ui:
            return name, number
    return None, None

def extract_message(user_input):
    """Extract the message content."""
    ui = user_input.lower()
    # Try to extract message after "saying" or "that"
    for keyword in [" saying ", " that ", " message ", " tell them "]:
        if keyword in ui:
            return ui.split(keyword, 1)[1].strip()
    return None

# ─────────────────────────────────────────
# 📤 SEND WHATSAPP MESSAGE
# ─────────────────────────────────────────
def send_whatsapp(phone_number, message, wait_seconds=15):
    """
    Send WhatsApp message using pywhatkit.
    Opens WhatsApp Web and sends automatically.
    """
    try:
        now      = datetime.datetime.now()
        hour     = now.hour
        minute   = now.minute + 2  # Send 2 minutes from now

        if minute >= 60:
            hour   += 1
            minute -= 60

        kit.sendwhatmsg(
            phone_no  = phone_number,
            message   = message,
            time_hour = hour,
            time_min  = minute,
            wait_time = wait_seconds,
            tab_close = True,
            close_time = 3
        )
        return True, f"Message sent to {phone_number} successfully!"

    except Exception as e:
        return False, f"Failed to send: {str(e)}"

# ─────────────────────────────────────────
# 🧩 MAIN HANDLER
# ─────────────────────────────────────────
def handle_whatsapp(user_input, speak_func):
    """Handle WhatsApp voice commands."""
    if not is_whatsapp_request(user_input):
        return False

    # Find contact
    contact_name, phone = extract_contact(user_input)

    if not contact_name:
        speak_func("Who do you want to message? Tell me the name.")
        name_input = input("⌨️ Contact name: ").strip().lower()
        contact_name = name_input
        phone = CONTACTS.get(name_input)

        if not phone:
            speak_func(f"I don't have {name_input}'s number saved. Add it to my contacts list.")
            print(f"\n📝 Add this to whatsapp_control.py CONTACTS:")
            print(f'   "{name_input}": "+91XXXXXXXXXX",')
            return True

    # Get message
    message = extract_message(user_input)
    if not message:
        speak_func(f"What should I tell {contact_name}?")
        message = input("⌨️ Message: ").strip()

    if not message:
        speak_func("No message to send!")
        return True

    # Confirm
    speak_func(f"Sending '{message}' to {contact_name}. Opening WhatsApp now!")
    print(f"\n📱 Sending WhatsApp to {contact_name} ({phone})")
    print(f"📝 Message: {message}")
    print("⏳ WhatsApp Web will open in a moment...\n")

    success, result = send_whatsapp(phone, message)

    if success:
        speak_func(f"Message sent to {contact_name} successfully!")
    else:
        speak_func(f"Couldn't send the message. Check if WhatsApp Web is working.")
        print(f"❌ Error: {result}")

    return True

# ─────────────────────────────────────────
# ➕ ADD CONTACT
# ─────────────────────────────────────────
def add_contact(name, phone):
    """Add a new contact."""
    CONTACTS[name.lower()] = phone
    return f"Added {name} with number {phone}!"