import datetime
import requests
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ── CONFIG ────────────────────────────────────────────────────────────────────
SERVICE_ACCOUNT_FILE = 'service_account.json'   # your file, in the same folder
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# IMPORTANT: paste the Google account email you want to read the calendar FOR.
# A service account cannot see your calendar unless you either:
#   (a) share your calendar with the service account email, OR
#   (b) enable domain-wide delegation (G Suite / Workspace only)
# See the note at the bottom of this file.
CALENDAR_OWNER_EMAIL = 'sfreeman.1.sf@gmail.com'   # <-- change this

# Ollama settings — adjust model name to whatever you have pulled locally
OLLAMA_URL  = 'http://localhost:11434/api/generate'
OLLAMA_MODEL = 'llama3'   # e.g. 'mistral', 'phi3', 'gemma', etc.
# ─────────────────────────────────────────────────────────────────────────────


def get_calendar_service():
    """Authenticate with the service account and return a Calendar API client."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        # Remove the next line if you are NOT using domain-wide delegation
        # subject=CALENDAR_OWNER_EMAIL,
    )
    return build('calendar', 'v3', credentials=creds)


def fetch_upcoming_events(service, max_results=10):
    """Return the next N events from the primary calendar."""
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    result = service.events().list(
        calendarId='sfreeman.1.sf@gmail.com',
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return result.get('items', [])


def format_events_for_prompt(events):
    """Turn the event list into a readable text block for the LLM."""
    if not events:
        return "No upcoming events found."
    lines = []
    for e in events:
        start_raw = e.get('start', {})
        start = start_raw.get('dateTime') or start_raw.get('date', 'Unknown time')
        title = e.get('summary', 'Untitled event')
        location = e.get('location', '')
        loc_str = f" @ {location}" if location else ""
        lines.append(f"  • {start}  —  {title}{loc_str}")
    return "\n".join(lines)


def ask_ollama(prompt, model=OLLAMA_MODEL):
    """Send a prompt to the local Ollama model and return the response text."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json().get('response', '').strip()
    except requests.exceptions.ConnectionError:
        return ("❌  Could not connect to Ollama. "
                "Make sure it is running: open a terminal and run  `ollama serve`")
    except Exception as exc:
        return f"❌  Ollama error: {exc}"


def chat_loop(events_text):
    """Simple interactive loop — ask your assistant anything about your calendar."""
    system_context = (
        "You are a helpful personal assistant. "
        "The user's upcoming Google Calendar events are listed below.\n\n"
        f"UPCOMING EVENTS:\n{events_text}\n\n"
        "Answer the user's questions about their schedule, suggest preparation tips, "
        "flag conflicts, or help them plan their day. Be concise and friendly."
    )

    print("\n🤖  Your Ollama calendar assistant is ready!  (type 'quit' to exit)\n")
    print("──── Upcoming events loaded ────")
    print(events_text)
    print("────────────────────────────────\n")

    history = []  # keep a simple conversation history

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ('quit', 'exit', 'q'):
            print("Goodbye! 👋")
            break

        history.append(f"User: {user_input}")
        conversation_so_far = "\n".join(history)

        full_prompt = (
            f"{system_context}\n\n"
            f"Conversation so far:\n{conversation_so_far}\n\n"
            "Assistant:"
        )

        print("Assistant: ", end="", flush=True)
        reply = ask_ollama(full_prompt)
        print(reply)
        history.append(f"Assistant: {reply}")
        print()


def main():
    print("🔑  Connecting to Google Calendar …")
    try:
        service = get_calendar_service()
        events = fetch_upcoming_events(service, max_results=10)
        events_text = format_events_for_prompt(events)
    except Exception as exc:
        print(f"\n❌  Google Calendar error: {exc}")
        print(
            "\n── TROUBLESHOOTING ──────────────────────────────────────────────\n"
            "Service accounts cannot access a personal Gmail calendar by default.\n"
            "You need to do ONE of the following:\n\n"
            "  Option A (simplest for personal Gmail):\n"
            "    1. Open Google Calendar → Settings → your calendar → 'Share with\n"
            "       specific people'\n"
            "    2. Add the service account email (ends in @...iam.gserviceaccount.com)\n"
            "    3. Give it 'See all event details' permission\n"
            "    4. Change  calendarId='primary'  to  calendarId='your.email@gmail.com'\n"
            "       in fetch_upcoming_events()\n\n"
            "  Option B (Google Workspace / G Suite only):\n"
            "    Enable domain-wide delegation in Google Admin, then uncomment the\n"
            "    subject=CALENDAR_OWNER_EMAIL  line in get_calendar_service().\n"
            "─────────────────────────────────────────────────────────────────"
        )
        return

    chat_loop(events_text)


if __name__ == '__main__':
    main()