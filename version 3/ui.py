# ui.py - Uses built-in tkinter only (no customtkinter needed)
import tkinter as tk
from tkinter import scrolledtext
import threading
from brain import ask_nexus

class NexusUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NEXUS - Jarvis AI")
        self.root.geometry("900x680")
        self.root.configure(bg="#0d1117")
        self.root.resizable(False, False)

        self.pulse_radius = 80
        self.pulse_direction = 1

        self.build_ui()
        self.animate_core()

    def build_ui(self):

        # ── Title ──────────────────────────────
        title = tk.Label(
            self.root,
            text="⬡  N E X U S",
            font=("Consolas", 28, "bold"),
            fg="#00f2ff",
            bg="#0d1117"
        )
        title.pack(pady=(20, 0))

        subtitle = tk.Label(
            self.root,
            text="NEURAL EXECUTIVE UNIT",
            font=("Consolas", 9),
            fg="#005f6b",
            bg="#0d1117",
            letter_spacing=4
        )
        subtitle.pack()

        # ── Animated Canvas ────────────────────
        self.canvas = tk.Canvas(
            self.root,
            width=220,
            height=220,
            bg="#0d1117",
            highlightthickness=0
        )
        self.canvas.pack(pady=(5, 0))

        # ── Status ─────────────────────────────
        self.status_label = tk.Label(
            self.root,
            text="● IDLE",
            font=("Consolas", 11),
            fg="#00f2ff",
            bg="#0d1117"
        )
        self.status_label.pack(pady=(0, 5))

        # ── Chat Box ───────────────────────────
        chat_frame = tk.Frame(self.root, bg="#0d1117")
        chat_frame.pack(padx=30, pady=5, fill="both")

        self.chat_box = scrolledtext.ScrolledText(
            chat_frame,
            width=90,
            height=10,
            bg="#161b22",
            fg="#c9d1d9",
            font=("Consolas", 10),
            relief="flat",
            bd=0,
            wrap="word",
            state="disabled"
        )
        self.chat_box.pack(fill="both")
        self.chat_box.configure(insertbackground="#00f2ff")

        # Color tags
        self.chat_box.tag_config("nexus",  foreground="#00f2ff", font=("Consolas", 10, "bold"))
        self.chat_box.tag_config("user",   foreground="#58a6ff", font=("Consolas", 10, "bold"))
        self.chat_box.tag_config("system", foreground="#3a3f47", font=("Consolas", 9, "italic"))
        self.chat_box.tag_config("msg",    foreground="#c9d1d9", font=("Consolas", 10))

        self.add_message("Nexus", "Systems online. How can I help you today?", "nexus")

        # ── Input Row ──────────────────────────
        input_frame = tk.Frame(self.root, bg="#0d1117")
        input_frame.pack(padx=30, pady=10, fill="x")

        self.user_input = tk.Entry(
            input_frame,
            bg="#161b22",
            fg="#c9d1d9",
            insertbackground="#00f2ff",
            font=("Consolas", 12),
            relief="flat",
            bd=8
        )
        self.user_input.pack(side="left", fill="x", expand=True, ipady=8)
        self.user_input.bind("<Return>", lambda e: self.handle_send())

        send_btn = tk.Button(
            input_frame,
            text="  SEND  ",
            bg="#00f2ff",
            fg="#0d1117",
            font=("Consolas", 11, "bold"),
            relief="flat",
            cursor="hand2",
            activebackground="#00c8d4",
            activeforeground="#0d1117",
            command=self.handle_send
        )
        send_btn.pack(side="left", padx=(8, 0), ipady=8)

        # ── Footer ─────────────────────────────
        footer = tk.Label(
            self.root,
            text="NEXUS AI  •  Voice + Text  •  Powered by Groq",
            font=("Consolas", 8),
            fg="#21262d",
            bg="#0d1117"
        )
        footer.pack(pady=(0, 8))

    # ── Pulsing Circle Animation ───────────────
    def animate_core(self):
        self.canvas.delete("all")
        cx, cy = 110, 110

        # Outer glow rings
        for i in range(3):
            r = self.pulse_radius + i * 14
            alpha_color = ["#003a40", "#004d55", "#006070"][i]
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=alpha_color, width=1
            )

        # Main ring
        r = self.pulse_radius
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline="#00f2ff", width=2
        )

        # Inner core
        self.canvas.create_oval(
            cx - 18, cy - 18, cx + 18, cy + 18,
            fill="#003a40", outline="#00f2ff", width=2
        )

        # Center dot
        self.canvas.create_oval(
            cx - 5, cy - 5, cx + 5, cy + 5,
            fill="#00f2ff", outline=""
        )

        # Cross lines
        self.canvas.create_line(cx - r, cy, cx + r, cy, fill="#003a40", width=1)
        self.canvas.create_line(cx, cy - r, cx, cy + r, fill="#003a40", width=1)

        self.pulse_radius += self.pulse_direction * 1.5
        if self.pulse_radius >= 95 or self.pulse_radius <= 70:
            self.pulse_direction *= -1

        self.root.after(35, self.animate_core)

    # ── Handle Send ───────────────────────────
    def handle_send(self):
        message = self.user_input.get().strip()
        if not message:
            return

        self.add_message("You", message, "user")
        self.user_input.delete(0, "end")
        threading.Thread(target=self.get_ai_response, args=(message,), daemon=True).start()

    def get_ai_response(self, message):
        self.update_status("● THINKING...", "#f0c040")
        reply = ask_nexus(message)
        self.add_message("Nexus", reply, "nexus")
        self.update_status("● IDLE", "#00f2ff")

    # ── Helpers ───────────────────────────────
    def update_status(self, text, color="#00f2ff"):
        self.status_label.configure(text=text, fg=color)

    def add_message(self, sender, message, tag="msg"):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"\n{sender}:  ", tag)
        self.chat_box.insert("end", f"{message}\n", "msg")
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def run(self):
        self.root.mainloop()