import datetime
import threading
import tkinter as tk
from tkinter import scrolledtext
from zoneinfo import ZoneInfo
import requests
import json
import os
import queue
import numpy as np
import sounddevice as sd
import wave
import tempfile
import speech_recognition as sr
import pyttsx3
from duckduckgo_search import DDGS
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ── CONFIG ────────────────────────────────────────────────────────────────────
SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES               = ['https://www.googleapis.com/auth/calendar.readonly']
CALENDAR_ID          = 'sfreeman.1.sf@gmail.com'   # <── your Gmail
YOUR_TIMEZONE        = 'America/New_York'
OLLAMA_URL           = 'http://localhost:11434/api/generate'
OLLAMA_MODEL         = 'llama3.2:3b'
MEMORY_FILE          = 'assistant_memory.json'
MAX_MEMORY_MESSAGES  = 40
WAKE_WORD            = 'hey quantum'            # new wake word!
ASSISTANT_NAME       = 'Quantum'
SAMPLE_RATE          = 16000
RECORD_SECONDS       = 6
# ─────────────────────────────────────────────────────────────────────────────

BG_DARK      = "#0f0f1a"
BG_PANEL     = "#16162a"
BG_INPUT     = "#1e1e35"
ACCENT       = "#7c6af7"
ACCENT2      = "#a78bfa"
USER_COLOR   = "#e2e8f0"
BOT_COLOR    = "#a78bfa"
TIME_COLOR   = "#4a4a6a"
EVENT_COLOR  = "#34d399"
BTN_HOVER    = "#6c5ce7"
TEXT_MAIN    = "#e2e8f0"
TEXT_DIM     = "#6b7280"
MEMORY_COLOR = "#fbbf24"
MIC_ACTIVE   = "#34d399"
MIC_INACTIVE = "#4a4a6a"
SEARCH_COLOR = "#38bdf8"


# ── MEMORY ────────────────────────────────────────────────────────────────────
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_memory(memory):
    trimmed = memory[-MAX_MEMORY_MESSAGES:]
    try:
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(trimmed, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Memory save error: {e}")

def format_memory_for_prompt(memory):
    if not memory:
        return "No previous conversations."
    lines = []
    for entry in memory[-20:]:
        role   = entry.get('role', 'unknown')
        text   = entry.get('text', '')
        date   = entry.get('date', '')
        prefix = "Stacey" if role == 'user' else ASSISTANT_NAME
        lines.append(f"{prefix} ({date}): {text}")
    return "\n".join(lines)


# ── CALENDAR ──────────────────────────────────────────────────────────────────
def get_calendar_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('calendar', 'v3', credentials=creds)

def fetch_upcoming_events(service, max_results=10):
    tz  = ZoneInfo(YOUR_TIMEZONE)
    now = datetime.datetime.now(tz=tz)
    result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=now.isoformat(),
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return result.get('items', [])

def format_events_for_display(events):
    if not events:
        return "No upcoming events found."
    tz = ZoneInfo(YOUR_TIMEZONE)
    lines = []
    for e in events:
        start_raw = e.get('start', {})
        start_str = start_raw.get('dateTime') or start_raw.get('date', 'Unknown')
        if 'T' in start_str:
            try:
                dt = datetime.datetime.fromisoformat(start_str)
                start_str = dt.astimezone(tz).strftime('%a %b %d  %I:%M %p ET')
            except Exception:
                pass
        title   = e.get('summary', 'Untitled event')
        loc     = e.get('location', '')
        loc_str = f"  📍 {loc}" if loc else ""
        lines.append(f"  🗓  {start_str}  —  {title}{loc_str}")
    return "\n".join(lines)


# ── WEB SEARCH ────────────────────────────────────────────────────────────────
def web_search(query, max_results=3):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "No search results found."
        return "\n".join(f"- {r.get('title','')}: {r.get('body','')}" for r in results)
    except Exception as e:
        return f"Search error: {e}"

def needs_search(message):
    keywords = [
        'today', 'current', 'latest', 'news', 'weather', 'price',
        'right now', 'recently', 'this week', 'stock', 'score',
        'what is happening', 'search', 'look up', 'find out'
    ]
    return any(k in message.lower() for k in keywords)


# ── OLLAMA ────────────────────────────────────────────────────────────────────
def ask_ollama(prompt):
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=300)
        resp.raise_for_status()
        return resp.json().get('response', '').strip()
    except requests.exceptions.ConnectionError:
        return "I cannot reach Ollama. Please make sure ollama serve is running."
    except Exception as exc:
        return f"Error: {exc}"


# ── AUDIO ─────────────────────────────────────────────────────────────────────
def record_audio(seconds=RECORD_SECONDS, samplerate=SAMPLE_RATE):
    recording = sd.rec(int(seconds * samplerate),
                       samplerate=samplerate,
                       channels=1, dtype='int16')
    sd.wait()
    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    with wave.open(tmp.name, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(recording.tobytes())
    return tmp.name

def transcribe_audio(wav_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except Exception:
        return None
    finally:
        try:
            os.unlink(wav_path)
        except Exception:
            pass


class AssistantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"✨ {ASSISTANT_NAME} — Stacey's AI Assistant")
        self.geometry("860x720")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self.minsize(600, 500)

        self.events          = []
        self.events_txt      = "Loading calendar…"
        self.service         = None
        self.memory          = load_memory()
        self.session_history = []
        self.tts_muted       = False
        self.wake_word_on    = False
        self.mic_active      = False
        self.tts_busy        = False          # prevents overlapping speech
        self.speech_queue    = queue.Queue()
        self.tts_engine      = None

        self._init_tts()
        self._build_ui()
        self._load_calendar()
        self.after(300, self._process_speech_queue)

    # ── TTS ───────────────────────────────────────────────────────────────────
    def _init_tts(self):
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 170)
            self.tts_engine.setProperty('volume', 0.9)
            voices = self.tts_engine.getProperty('voices')
            for v in voices:
                if 'zira' in v.name.lower() or 'female' in v.name.lower():
                    self.tts_engine.setProperty('voice', v.id)
                    break
        except Exception as e:
            print(f"TTS init error: {e}")

    def _speak(self, text):
        """Speak text — waits for any current speech to finish first."""
        if self.tts_muted or not self.tts_engine:
            return
        clean = ''.join(c for c in text if c.isascii() or c == ' ')
        threading.Thread(target=self._tts_thread, args=(clean,), daemon=True).start()

    def _tts_thread(self, text):
        # Wait if already speaking
        while self.tts_busy:
            import time; time.sleep(0.1)
        self.tts_busy = True
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS error: {e}")
        finally:
            self.tts_busy = False

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=ACCENT, height=56)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text=f"✨  {ASSISTANT_NAME}",
                 bg=ACCENT, fg="white",
                 font=("Georgia", 16, "bold")).pack(side=tk.LEFT, padx=18, pady=12)

        tk.Label(header, text="Stacey's AI Assistant",
                 bg=ACCENT, fg="#d4c5ff",
                 font=("Georgia", 11)).pack(side=tk.LEFT, padx=(0, 12), pady=12)

        self.status_lbl = tk.Label(header, text="● connecting…",
                                   bg=ACCENT, fg="#d4c5ff",
                                   font=("Consolas", 9))
        self.status_lbl.pack(side=tk.RIGHT, padx=18)

        self.mem_lbl = tk.Label(header, text=f"🧠 {len(self.memory)} memories",
                                bg=ACCENT, fg=MEMORY_COLOR,
                                font=("Consolas", 9))
        self.mem_lbl.pack(side=tk.RIGHT, padx=12)

        # Sidebar
        sidebar = tk.Frame(self, bg=BG_PANEL, width=230)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="UPCOMING EVENTS",
                 bg=BG_PANEL, fg=ACCENT2,
                 font=("Consolas", 8, "bold")).pack(anchor="w", padx=14, pady=(14, 4))

        self.cal_text = tk.Text(sidebar, bg=BG_PANEL, fg=EVENT_COLOR,
                                font=("Consolas", 9), wrap=tk.WORD,
                                relief=tk.FLAT, bd=0,
                                state=tk.DISABLED, cursor="arrow")
        self.cal_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

        tk.Button(sidebar, text="⟳  Refresh Calendar",
                  bg=BG_INPUT, fg=ACCENT2, font=("Consolas", 9),
                  relief=tk.FLAT, cursor="hand2",
                  activebackground=BTN_HOVER, activeforeground="white",
                  command=self._load_calendar).pack(fill=tk.X, padx=8, pady=(0, 4))

        tk.Button(sidebar, text="🧠  View Memory Log",
                  bg=BG_INPUT, fg=MEMORY_COLOR, font=("Consolas", 9),
                  relief=tk.FLAT, cursor="hand2",
                  activebackground=BTN_HOVER, activeforeground="white",
                  command=self._show_memory_window).pack(fill=tk.X, padx=8, pady=(0, 4))

        tk.Button(sidebar, text="🗑  Clear Memory",
                  bg=BG_INPUT, fg="#f87171", font=("Consolas", 9),
                  relief=tk.FLAT, cursor="hand2",
                  activebackground="#7f1d1d", activeforeground="white",
                  command=self._clear_memory).pack(fill=tk.X, padx=8, pady=(0, 12))

        tk.Button(sidebar, text="✍️  Proofread Text",
                  bg=BG_INPUT, fg="#c084fc", font=("Consolas", 9),
                  relief=tk.FLAT, cursor="hand2",
                  activebackground=BTN_HOVER, activeforeground="white",
                  command=self._show_proofread_window).pack(fill=tk.X, padx=8, pady=(0, 12))

        tk.Label(sidebar, text="VOICE CONTROLS",
                 bg=BG_PANEL, fg=ACCENT2,
                 font=("Consolas", 8, "bold")).pack(anchor="w", padx=14, pady=(8, 4))

        self.mute_btn = tk.Button(sidebar, text="🔊  Voice On",
                  bg=BG_INPUT, fg=MIC_ACTIVE, font=("Consolas", 9),
                  relief=tk.FLAT, cursor="hand2",
                  activebackground=BTN_HOVER, activeforeground="white",
                  command=self._toggle_mute)
        self.mute_btn.pack(fill=tk.X, padx=8, pady=(0, 4))

        self.wake_btn = tk.Button(sidebar,
                  text=f"👂  Say '{WAKE_WORD}': Off",
                  bg=BG_INPUT, fg=MIC_INACTIVE, font=("Consolas", 9),
                  relief=tk.FLAT, cursor="hand2",
                  activebackground=BTN_HOVER, activeforeground="white",
                  command=self._toggle_wake_word)
        self.wake_btn.pack(fill=tk.X, padx=8, pady=(0, 12))

        # Chat area
        chat_frame = tk.Frame(self, bg=BG_DARK)
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, bg=BG_DARK, fg=TEXT_MAIN,
            font=("Consolas", 10), wrap=tk.WORD,
            relief=tk.FLAT, bd=0, state=tk.DISABLED,
            padx=12, pady=12, selectbackground=ACCENT)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 0))

        self.chat_display.tag_config("user",      foreground=USER_COLOR,   font=("Consolas", 10, "bold"))
        self.chat_display.tag_config("assistant", foreground=BOT_COLOR,    font=("Consolas", 10))
        self.chat_display.tag_config("timestamp", foreground=TIME_COLOR,   font=("Consolas", 8))
        self.chat_display.tag_config("system",    foreground=TEXT_DIM,     font=("Consolas", 9, "italic"))
        self.chat_display.tag_config("thinking",  foreground=ACCENT,       font=("Consolas", 9, "italic"))
        self.chat_display.tag_config("memory",    foreground=MEMORY_COLOR, font=("Consolas", 9, "italic"))
        self.chat_display.tag_config("search",    foreground=SEARCH_COLOR, font=("Consolas", 9, "italic"))
        self.chat_display.tag_config("voice",     foreground=MIC_ACTIVE,   font=("Consolas", 9, "italic"))

        # Input row
        input_frame = tk.Frame(chat_frame, bg=BG_INPUT, pady=8)
        input_frame.pack(fill=tk.X, padx=4, pady=6)

        self.mic_btn = tk.Button(input_frame, text="🎤",
                  bg=BG_INPUT, fg=MIC_INACTIVE,
                  font=("Consolas", 14), relief=tk.FLAT,
                  cursor="hand2", command=self._push_to_talk)
        self.mic_btn.pack(side=tk.LEFT, padx=(8, 4))

        self.input_box = tk.Text(input_frame, bg=BG_INPUT, fg=TEXT_MAIN,
                                 font=("Consolas", 11), height=2,
                                 relief=tk.FLAT, bd=0,
                                 insertbackground=ACCENT2, wrap=tk.WORD)
        self.input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 6), pady=4)
        self.input_box.bind("<Return>",       self._on_enter)
        self.input_box.bind("<Shift-Return>", lambda e: None)

        tk.Button(input_frame, text="Send  ➤",
                  bg=ACCENT, fg="white",
                  font=("Consolas", 10, "bold"),
                  relief=tk.FLAT, padx=14, cursor="hand2",
                  activebackground=BTN_HOVER, activeforeground="white",
                  command=self._send_message).pack(side=tk.RIGHT, padx=(0, 10))

        tk.Label(chat_frame,
                 text=f"Enter to send  •  Shift+Enter for newline  •  🎤 mic or say '{WAKE_WORD}'",
                 bg=BG_DARK, fg=TIME_COLOR,
                 font=("Consolas", 8)).pack(anchor="e", padx=8)

    # ── VOICE ─────────────────────────────────────────────────────────────────
    def _toggle_mute(self):
        self.tts_muted = not self.tts_muted
        if self.tts_muted:
            self.mute_btn.config(text="🔇  Voice Off", fg=MIC_INACTIVE)
            self._append_chat("🔇  Voice muted.\n", "system")
        else:
            self.mute_btn.config(text="🔊  Voice On", fg=MIC_ACTIVE)
            self._append_chat("🔊  Voice unmuted.\n", "system")

    def _toggle_wake_word(self):
        self.wake_word_on = not self.wake_word_on
        if self.wake_word_on:
            self.wake_btn.config(text=f"👂  Say '{WAKE_WORD}': On", fg=MIC_ACTIVE)
            self._append_chat(f"👂  Listening for '{WAKE_WORD}'…\n", "voice")
            threading.Thread(target=self._wake_word_loop, daemon=True).start()
        else:
            self.wake_btn.config(text=f"👂  Say '{WAKE_WORD}': Off", fg=MIC_INACTIVE)
            self._append_chat("👂  Wake word disabled.\n", "system")

    def _push_to_talk(self):
        if self.mic_active:
            return
        self.mic_active = True
        self.mic_btn.config(fg=MIC_ACTIVE)
        self._append_chat(f"🎤  Recording {RECORD_SECONDS} seconds… speak now!\n", "voice")
        threading.Thread(target=self._record_and_transcribe, daemon=True).start()

    def _record_and_transcribe(self):
        try:
            wav_path = record_audio()
            text = transcribe_audio(wav_path)
            if text:
                self.speech_queue.put(text)
            else:
                self.after(0, lambda: self._append_chat(
                    "🎤  Could not understand — please try again.\n", "system"))
        except Exception as e:
            self.after(0, lambda: self._append_chat(f"🎤  Error: {e}\n", "system"))
        finally:
            self.mic_active = False
            self.after(0, lambda: self.mic_btn.config(fg=MIC_INACTIVE))

    def _wake_word_loop(self):
        while self.wake_word_on:
            try:
                wav_path = record_audio(seconds=4)
                text = transcribe_audio(wav_path)
                if text and WAKE_WORD in text.lower():
                    self.after(0, lambda: self._append_chat(
                        f"👂  '{WAKE_WORD}' heard! Recording your message…\n", "voice"))
                    self._record_and_transcribe()
            except Exception:
                continue

    def _process_speech_queue(self):
        try:
            while True:
                text = self.speech_queue.get_nowait()
                self._append_chat(f"🎤  You said: {text}\n", "voice")
                self.input_box.delete("1.0", tk.END)
                self.input_box.insert("1.0", text)
                self._send_message()
        except queue.Empty:
            pass
        self.after(300, self._process_speech_queue)

    # ── CALENDAR ──────────────────────────────────────────────────────────────
    def _load_calendar(self):
        self._set_cal_text("Loading…")
        self._set_status("● connecting…", "#d4c5ff")
        threading.Thread(target=self._calendar_thread, daemon=True).start()

    def _calendar_thread(self):
        try:
            self.service    = get_calendar_service()
            self.events     = fetch_upcoming_events(self.service)
            self.events_txt = format_events_for_display(self.events)
            self.after(0, lambda: self._set_cal_text(self.events_txt))
            self.after(0, lambda: self._set_status("● calendar connected", "#86efac"))
            self.after(0, self._show_welcome)
        except Exception as exc:
            msg = f"Calendar error:\n{exc}"
            self.after(0, lambda: self._set_cal_text(msg))
            self.after(0, lambda: self._set_status("● calendar error", "#fca5a5"))

    def _show_welcome(self):
        tz      = ZoneInfo(YOUR_TIMEZONE)
        now_str = datetime.datetime.now(tz=tz).strftime('%A, %B %d  %I:%M %p ET')
        self._append_chat(f"📅  {now_str}\n", "timestamp")
        if self.memory:
            last      = self.memory[-1]
            last_date = last.get('date', 'previously')
            self._append_chat(
                f"🧠  I remember our last conversation from {last_date}. "
                f"I have {len(self.memory)} memories stored.\n", "memory")
        self._append_chat(
            f"Hi Stacey! 👋  I'm {ASSISTANT_NAME}, your personal AI assistant.\n"
            f"I'm connected to your Google Calendar and ready to help.\n"
            f"Type, click 🎤, or say '{WAKE_WORD}' to talk to me!\n",
            "assistant")
        self._speak(
            f"Hi Stacey! I'm {ASSISTANT_NAME}, your personal AI assistant. "
            f"I'm connected to your Google Calendar and ready to help!")

    # ── CHAT ──────────────────────────────────────────────────────────────────
    def _on_enter(self, event):
        if not event.state & 0x1:
            self._send_message()
            return "break"

    def _send_message(self):
        msg = self.input_box.get("1.0", tk.END).strip()
        if not msg:
            return
        self.input_box.delete("1.0", tk.END)

        tz       = ZoneInfo(YOUR_TIMEZONE)
        now      = datetime.datetime.now(tz=tz)
        ts       = now.strftime('%I:%M %p')
        date_str = now.strftime('%Y-%m-%d %I:%M %p ET')

        self._append_chat(f"\n[{ts}] You\n", "timestamp")
        self._append_chat(f"{msg}\n", "user")
        self._append_chat(f"{ASSISTANT_NAME} is thinking…\n", "thinking")

        self.memory.append({"role": "user", "text": msg, "date": date_str})
        self.session_history.append(f"Stacey: {msg}")
        threading.Thread(target=self._ollama_thread, args=(msg,), daemon=True).start()

    def _ollama_thread(self, user_msg):
        tz      = ZoneInfo(YOUR_TIMEZONE)
        now_str = datetime.datetime.now(tz=tz).strftime('%A, %B %d %Y  %I:%M %p ET')

        search_context = ""
        if needs_search(user_msg):
            self.after(0, lambda: self._append_chat("🌐  Searching the web…\n", "search"))
            results = web_search(user_msg)
            search_context = f"\nWEB SEARCH RESULTS:\n{results}\n"

        memory_context = format_memory_for_prompt(self.memory[:-1])
        system_ctx = (
            f"Your name is {ASSISTANT_NAME}. You are Stacey's personal AI assistant. "
            f"If anyone asks your name, you are {ASSISTANT_NAME}, not Ollama or Allama. "
            f"Current date/time: {now_str}.\n\n"
            f"Stacey's upcoming calendar events (Eastern Time):\n{self.events_txt}\n\n"
            f"MEMORY OF PAST CONVERSATIONS:\n{memory_context}\n"
            f"{search_context}\n"
            f"CURRENT SESSION:\n" + "\n".join(self.session_history) +
            "\n\nBe concise, warm, and friendly. Always refer to yourself as Quantum."
        )

        reply = ask_ollama(f"{system_ctx}\n\nAssistant:")

        date_str = datetime.datetime.now(tz=tz).strftime('%Y-%m-%d %I:%M %p ET')
        self.memory.append({"role": "assistant", "text": reply, "date": date_str})
        self.session_history.append(f"{ASSISTANT_NAME}: {reply}")
        save_memory(self.memory)

        self.after(0, self._update_memory_label)
        self.after(0, lambda: self._replace_thinking(reply))
        # Speak the reply — queued so it never overlaps
        self._speak(reply)

    def _replace_thinking(self, reply):
        self.chat_display.config(state=tk.NORMAL)
        content       = self.chat_display.get("1.0", tk.END)
        thinking_line = f"{ASSISTANT_NAME} is thinking…\n"
        idx = content.rfind(thinking_line)
        if idx != -1:
            self.chat_display.delete(f"1.0 + {idx} chars",
                                     f"1.0 + {idx + len(thinking_line)} chars")
        self.chat_display.config(state=tk.DISABLED)

        tz = ZoneInfo(YOUR_TIMEZONE)
        ts = datetime.datetime.now(tz=tz).strftime('%I:%M %p')
        self._append_chat(f"\n[{ts}] {ASSISTANT_NAME}\n", "timestamp")
        self._append_chat(f"{reply}\n", "assistant")

    # ── MEMORY UI ─────────────────────────────────────────────────────────────
    def _update_memory_label(self):
        self.mem_lbl.config(text=f"🧠 {len(self.memory)} memories")

    def _show_proofread_window(self):
        """Open a dedicated proofreading window."""
        win = tk.Toplevel(self)
        win.title("✍️  Quantum Proofreader")
        win.geometry("700x600")
        win.configure(bg=BG_DARK)

        tk.Label(win, text="✍️  Quantum Proofreader",
                 bg=BG_DARK, fg="#c084fc",
                 font=("Georgia", 14, "bold")).pack(pady=(14, 2))
        tk.Label(win, text="Paste your text below and Quantum will fix grammar, tone, and clarity.",
                 bg=BG_DARK, fg=TEXT_DIM,
                 font=("Consolas", 9)).pack(pady=(0, 10))

        # Style selector
        style_frame = tk.Frame(win, bg=BG_DARK)
        style_frame.pack(fill=tk.X, padx=16, pady=(0, 8))
        tk.Label(style_frame, text="Tone:",
                 bg=BG_DARK, fg=TEXT_MAIN,
                 font=("Consolas", 9)).pack(side=tk.LEFT, padx=(0, 8))

        style_var = tk.StringVar(value="Professional")
        for style in ["Professional", "Casual", "Academic", "Concise"]:
            tk.Radiobutton(style_frame, text=style,
                          variable=style_var, value=style,
                          bg=BG_DARK, fg=ACCENT2,
                          selectcolor=BG_PANEL,
                          activebackground=BG_DARK,
                          font=("Consolas", 9)).pack(side=tk.LEFT, padx=6)

        # Input area
        tk.Label(win, text="YOUR TEXT:",
                 bg=BG_DARK, fg=TEXT_DIM,
                 font=("Consolas", 8, "bold")).pack(anchor="w", padx=16)
        input_txt = tk.Text(win, bg=BG_PANEL, fg=TEXT_MAIN,
                           font=("Consolas", 10), height=8,
                           relief=tk.FLAT, padx=10, pady=8,
                           insertbackground=ACCENT2, wrap=tk.WORD)
        input_txt.pack(fill=tk.X, padx=16, pady=(4, 8))

        # Proofread button
        status_lbl = tk.Label(win, text="",
                              bg=BG_DARK, fg=ACCENT,
                              font=("Consolas", 9, "italic"))
        status_lbl.pack()

        # Output area
        tk.Label(win, text="QUANTUM'S CORRECTION:",
                 bg=BG_DARK, fg=TEXT_DIM,
                 font=("Consolas", 8, "bold")).pack(anchor="w", padx=16)
        output_txt = tk.Text(win, bg=BG_PANEL, fg="#c084fc",
                            font=("Consolas", 10), height=8,
                            relief=tk.FLAT, padx=10, pady=8,
                            wrap=tk.WORD, state=tk.DISABLED)
        output_txt.pack(fill=tk.X, padx=16, pady=(4, 8))

        def do_proofread():
            text = input_txt.get("1.0", tk.END).strip()
            if not text:
                status_lbl.config(text="Please paste some text first!")
                return
            status_lbl.config(text="Quantum is proofreading…")
            win.update()

            def run():
                tone = style_var.get()
                prompt = (
                    f"You are Quantum, Stacey's AI assistant. "
                    f"Please proofread and correct the following text. "
                    f"Fix all grammar, spelling, and punctuation errors. "
                    f"Make the tone {tone.lower()}. "
                    f"Keep Stacey's original meaning and voice. "
                    f"Return ONLY the corrected text, nothing else.\n\n"
                    f"TEXT TO PROOFREAD:\n{text}"
                )
                result = ask_ollama(prompt)
                win.after(0, lambda: show_result(result))

            def show_result(result):
                output_txt.config(state=tk.NORMAL)
                output_txt.delete("1.0", tk.END)
                output_txt.insert(tk.END, result)
                output_txt.config(state=tk.DISABLED)
                status_lbl.config(text="Done! Copy the corrected text above.")
                self._speak("I've finished proofreading your text!")

            threading.Thread(target=run, daemon=True).start()

        def copy_result():
            result = output_txt.get("1.0", tk.END).strip()
            if result:
                win.clipboard_clear()
                win.clipboard_append(result)
                status_lbl.config(text="Copied to clipboard!")

        btn_frame = tk.Frame(win, bg=BG_DARK)
        btn_frame.pack(pady=4)

        tk.Button(btn_frame, text="✍️  Proofread",
                  bg=ACCENT, fg="white",
                  font=("Consolas", 10, "bold"),
                  relief=tk.FLAT, padx=16, cursor="hand2",
                  activebackground=BTN_HOVER,
                  command=do_proofread).pack(side=tk.LEFT, padx=8)

        tk.Button(btn_frame, text="📋  Copy Result",
                  bg=BG_INPUT, fg=ACCENT2,
                  font=("Consolas", 10),
                  relief=tk.FLAT, padx=16, cursor="hand2",
                  activebackground=BTN_HOVER,
                  command=copy_result).pack(side=tk.LEFT, padx=8)

        tk.Button(btn_frame, text="🗑  Clear",
                  bg=BG_INPUT, fg=TEXT_DIM,
                  font=("Consolas", 10),
                  relief=tk.FLAT, padx=16, cursor="hand2",
                  activebackground=BTN_HOVER,
                  command=lambda: [
                      input_txt.delete("1.0", tk.END),
                      output_txt.config(state=tk.NORMAL),
                      output_txt.delete("1.0", tk.END),
                      output_txt.config(state=tk.DISABLED),
                      status_lbl.config(text="")
                  ]).pack(side=tk.LEFT, padx=8)

    def _show_memory_window(self):
        win = tk.Toplevel(self)
        win.title("🧠 Memory Log")
        win.geometry("600x500")
        win.configure(bg=BG_DARK)
        tk.Label(win, text="Conversation Memory Log",
                 bg=BG_DARK, fg=MEMORY_COLOR,
                 font=("Georgia", 13, "bold")).pack(pady=(12, 4))
        tk.Label(win, text=f"{len(self.memory)} memories stored in {MEMORY_FILE}",
                 bg=BG_DARK, fg=TEXT_DIM,
                 font=("Consolas", 9)).pack(pady=(0, 8))
        txt = scrolledtext.ScrolledText(win, bg=BG_PANEL, fg=TEXT_MAIN,
                                        font=("Consolas", 9), wrap=tk.WORD,
                                        relief=tk.FLAT, padx=10, pady=10)
        txt.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        if not self.memory:
            txt.insert(tk.END, "No memories yet. Start chatting!")
        else:
            for entry in self.memory:
                role = "🧑 Stacey" if entry['role'] == 'user' else f"🤖 {ASSISTANT_NAME}"
                txt.insert(tk.END,
                    f"[{entry.get('date','')}] {role}\n{entry.get('text','')}\n\n")
        txt.config(state=tk.DISABLED)

    def _clear_memory(self):
        win = tk.Toplevel(self)
        win.title("Clear Memory?")
        win.geometry("340x160")
        win.configure(bg=BG_DARK)
        win.resizable(False, False)
        tk.Label(win, text="⚠️  Clear all memory?",
                 bg=BG_DARK, fg="#f87171",
                 font=("Georgia", 12, "bold")).pack(pady=(18, 6))
        tk.Label(win, text="This cannot be undone.",
                 bg=BG_DARK, fg=TEXT_DIM,
                 font=("Consolas", 9)).pack()
        btn_frame = tk.Frame(win, bg=BG_DARK)
        btn_frame.pack(pady=18)
        def confirm():
            self.memory = []
            save_memory(self.memory)
            self._update_memory_label()
            self._append_chat("🗑  Memory cleared.\n", "system")
            win.destroy()
        tk.Button(btn_frame, text="Yes, clear it",
                  bg="#7f1d1d", fg="white", font=("Consolas", 10),
                  relief=tk.FLAT, padx=12, cursor="hand2",
                  command=confirm).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Cancel",
                  bg=BG_INPUT, fg=TEXT_MAIN, font=("Consolas", 10),
                  relief=tk.FLAT, padx=12, cursor="hand2",
                  command=win.destroy).pack(side=tk.LEFT, padx=8)

    # ── HELPERS ───────────────────────────────────────────────────────────────
    def _append_chat(self, text, tag="assistant"):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, text, tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def _set_cal_text(self, text):
        self.cal_text.config(state=tk.NORMAL)
        self.cal_text.delete("1.0", tk.END)
        self.cal_text.insert(tk.END, text)
        self.cal_text.config(state=tk.DISABLED)

    def _set_status(self, text, color):
        self.status_lbl.config(text=text, fg=color)


if __name__ == '__main__':
    app = AssistantApp()
    app.mainloop()