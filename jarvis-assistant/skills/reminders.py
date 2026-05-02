from datetime import datetime
from typing import List

from app.main import assistant

REMINDERS: List[str] = []


def reminder_skill(prompt: str) -> str:
    lower = prompt.lower()
    if "list" in lower:
        if not REMINDERS:
            return "No reminders yet."
        return "Reminders: " + "; ".join(REMINDERS)
    # add new reminder
    text = prompt.replace("remind me", "", 1).strip()
    if not text:
        return "Tell me what to remind you about."
    REMINDERS.append(f"{datetime.now().strftime('%H:%M')} - {text}")
    return f"Added reminder: {text}"


assistant.register("reminders", ["remind", "reminder", "remember"], reminder_skill)
