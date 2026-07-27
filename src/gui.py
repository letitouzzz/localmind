"""
LocalMind GUI - Interface graphique Tkinter
"""

import tkinter as tk
from tkinter import messagebox
import warnings
warnings.filterwarnings("ignore")

import threading
import re
import subprocess
import shlex
from datetime import datetime

from .core import ask, route_question
from .web import search_duckduckgo, search_tavily
from .executor import extract_exec_commands, is_plausible_command

# --- PALETTE ---
BG_DARK, BG_PANEL, BG_INPUT = "#0f1117", "#171a23", "#1f2330"
ACCENT, ACCENT_HOVER = "#7c5cff", "#9277ff"
TEXT_MAIN, TEXT_DIM = "#e6e6f0", "#8b8fa3"
USER_COLOR, BOT_COLOR = "#5cc8ff", "#7c5cff"
SYS_COLOR, ERR_COLOR = "#f5a623", "#ff5c5c"
SCROLL_TRACK, SCROLL_THUMB, SCROLL_THUMB_HOVER = "#171a23", "#3a3f55", "#4d5375"


class CustomScrollbar(tk.Canvas):
    def __init__(self, parent, command, width=10):
        super().__init__(parent, width=width, bg=SCROLL_TRACK, highlightthickness=0, bd=0)
        self.command = command
        self.thumb = self.create_rectangle(0, 0, width, 40, fill=SCROLL_THUMB, outline="")
        self.bind("<Button-1>", self._click)
        self.bind("<B1-Motion>", self._drag)
        self.bind("<Enter>", lambda e: self.itemconfig(self.thumb, fill=SCROLL_THUMB_HOVER))
        self.bind("<Leave>", lambda e: self.itemconfig(self.thumb, fill=SCROLL_THUMB))

    def set(self, lo, hi):
        lo, hi = float(lo), float(hi)
        h = self.winfo_height()
        y1, y2 = lo * h, hi * h
        if y2 - y1 < 20:
            y2 = y1 + 20
        self.coords(self.thumb, 1, y1, self.winfo_width() - 1, y2)

    def _click(self, event):
        self.command("moveto", event.y / self.winfo_height())

    def _drag(self, event):
        self._click(event)


class LocalMindGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LocalMind")
        self.root.configure(bg=BG_DARK)
        self.root.minsize(750, 550)

        try:
            self.root.state("zoomed")
        except tk.TclError:
            pass

        # Header
        header = tk.Frame(root, bg=BG_PANEL, height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(header, text="LocalMind", font=("Segoe UI", 16, "bold"),
                 bg=BG_PANEL, fg=TEXT_MAIN, anchor="w").pack(side="left", padx=18)
        self.status = tk.Label(header, text="● prêt", font=("Segoe UI", 9),
                               bg=BG_PANEL, fg="#4ade80", anchor="e")
        self.status.pack(side="right", padx=18)

        # Chat area
        chat_frame = tk.Frame(root, bg=BG_DARK)
        chat_frame.pack(fill="both", expand=True, padx=14, pady=(12, 6))

        self.chat_area = tk.Text(chat_frame, wrap=tk.WORD, state="disabled",
                                 font=("Segoe UI", 10), bg=BG_DARK, fg=TEXT_MAIN,
                                 insertbackground=TEXT_MAIN, borderwidth=0,
                                 highlightthickness=0, padx=12, pady=12)
        self.chat_area.pack(side="left", fill="both", expand=True)

        self.scrollbar = CustomScrollbar(chat_frame, command=self.chat_area.yview)
        self.scrollbar.pack(side="right", fill="y", padx=(4, 0))
        self.chat_area.configure(yscrollcommand=self.scrollbar.set)

        # Tags
        self.chat_area.tag_config("user", foreground=USER_COLOR, font=("Segoe UI", 10, "bold"))
        self.chat_area.tag_config("bot", foreground=BOT_COLOR, font=("Segoe UI", 10, "bold"))
        self.chat_area.tag_config("sys", foreground=SYS_COLOR, font=("Segoe UI", 9, "italic"))
        self.chat_area.tag_config("err", foreground=ERR_COLOR, font=("Segoe UI", 9, "bold"))
        self.chat_area.tag_config("body", foreground=TEXT_MAIN, font=("Segoe UI", 10))
        self.chat_area.tag_config("bold", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
        self.chat_area.tag_config("codeblock", foreground="#a6accd", background="#13151f",
                                  font=("Consolas", 9))
        self.chat_area.tag_config("time", foreground=TEXT_DIM, font=("Segoe UI", 8))

        # Input area
        input_frame = tk.Frame(root, bg=BG_DARK)
        input_frame.pack(fill="x", padx=14, pady=(8, 16))

        self.entry_frame = tk.Frame(input_frame, bg=BG_INPUT,
                                    highlightbackground=ACCENT, highlightthickness=1, bd=0)
        self.entry_frame.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=6)

        self.entry = tk.Entry(self.entry_frame, font=("Segoe UI", 11), bg=BG_INPUT,
                              fg=TEXT_MAIN, insertbackground=TEXT_MAIN,
                              borderwidth=0, highlightthickness=0)
        self.entry.pack(fill="x", expand=True, padx=12, pady=2)
        self.entry.bind("<Return>", lambda e: self.send())

        self.send_btn = tk.Button(
            input_frame, text="Envoyer  ➤", command=self.send,
            font=("Segoe UI", 10, "bold"), bg=ACCENT, fg="white",
            activebackground=ACCENT_HOVER, activeforeground="white",
            bd=0, relief="flat", padx=18, pady=8, cursor="hand2"
        )
        self.send_btn.pack(side="right")

        self.root.after(100, lambda: self.entry.focus_set())
        self.append("LocalMind", "Yo ! Je suis prêt, pose-moi ta question 👇", "bot")

    def timestamp(self):
        return datetime.now().strftime("%H:%M")

    def insert_markdown_text(self, text: str):
        code_blocks = re.split(r'(```[\s\S]*?```)', text)
        for block in code_blocks:
            if block.startswith('```') and block.endswith('```'):
                lines = block[3:-3].split('\n')
                if lines and lines[0].strip().isalpha():
                    code_text = '\n'.join(lines[1:])
                else:
                    code_text = '\n'.join(lines)
                self.chat_area.insert(tk.END, f"\n{code_text.strip()}\n", "codeblock")
            else:
                parts = re.split(r'(\*\*.*?\*\*)', block)
                for part in parts:
                    if part.startswith('**') and part.endswith('**'):
                        self.chat_area.insert(tk.END, part[2:-2], "bold")
                    else:
                        self.chat_area.insert(tk.END, part, "body")

    def append(self, sender: str, text: str, tag: str):
        self.chat_area.configure(state="normal")
        self.chat_area.insert(tk.END, f"{sender}  ", tag)
        self.chat_area.insert(tk.END, f"{self.timestamp()}\n", "time")

        if tag == "bot":
            self.insert_markdown_text(text)
            self.chat_area.insert(tk.END, "\n\n")
        else:
            self.chat_area.insert(tk.END, f"{text}\n\n", "body")

        self.chat_area.configure(state="disabled")
        self.chat_area.see(tk.END)

    def send(self):
        question = self.entry.get().strip()
        if not question:
            return
        self.entry.delete(0, tk.END)
        self.append("Toi", question, "user")
        self.set_busy(True, "● analyse la demande...")
        threading.Thread(target=self.process, args=(question,), daemon=True).start()

    def set_busy(self, busy: bool, text="● prêt"):
        if busy:
            self.send_btn.config(state="disabled", text="⚡ ...", bg="#4a4d5c")
            self.status.config(text=text, fg="#f5a623")
        else:
            self.send_btn.config(state="normal", text="Envoyer  ➤", bg=ACCENT)
            self.status.config(text="● prêt", fg="#4ade80")

    def process(self, question: str):
        try:
            decision = route_question(question)
            tool = decision["tool"]

            web_context = ""
            if tool == "ddg":
                self.root.after(0, lambda: self.status.config(
                    text="● cherche sur DuckDuckGo...", fg="#5cc8ff"))
                web_context = search_duckduckgo(question)
            elif tool == "tavily":
                self.root.after(0, lambda: self.status.config(
                    text="● recherche poussée Tavily AI...", fg="#9277ff"))
                web_context = search_tavily(question)

            self.root.after(0, lambda: self.status.config(
                text=f"● génération ({decision['category']})...", fg="#f5a623"))

            answer = ask(question, web_context)
        except Exception as e:
            answer = f"[Erreur] {e}"

        self.root.after(0, self.handle_response, answer)

    def handle_response(self, answer: str):
        raw_commands = extract_exec_commands(answer)
        display_text = re.sub(
            r"\[EXEC\].*?\[/EXEC\]",
            "→ [commande proposée, confirmation demandée]",
            answer, flags=re.DOTALL
        )
        self.append("LocalMind", display_text, "bot")

        for cmd in raw_commands:
            cmd = cmd.strip()
            if is_plausible_command(cmd):
                self.confirm_and_run(cmd)
            else:
                self.append("Système", f"Commande ignorée : « {cmd} »", "sys")

        self.set_busy(False)

    def confirm_and_run(self, cmd: str):
        confirmed = messagebox.askyesno(
            "Confirmer l'exécution",
            f"LocalMind propose de lancer cette commande :\n\n{cmd}\n\nL'exécuter ?"
        )
        if not confirmed:
            self.append("Système", f"Commande annulée : {cmd}", "sys")
            return

        self.append("Système", f"Exécution de : {cmd}", "sys")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            output = result.stdout or result.stderr or "(pas de sortie)"
            self.append("Résultat", output[:3000], "sys")
        except Exception as e:
            self.append("Erreur", str(e), "err")


def main():
    root = tk.Tk()
    LocalMindGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
