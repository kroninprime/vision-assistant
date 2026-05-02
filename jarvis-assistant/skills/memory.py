from collections import deque
from typing import Deque

from app.main import assistant

MEMORY: Deque[str] = deque(maxlen=20)


def remember(prompt: str) -> str:
    lower = prompt.lower()
    if lower.startswith("remember"):
        item = prompt[len("remember"):].strip()
        MEMORY.append(item)
        return f"Got it, I will remember: {item}"
    if "what do you remember" in lower or "recall" in lower:
        if not MEMORY:
            return "I have no memories yet."
        return "I remember: " + "; ".join(MEMORY)
    return "Say 'remember <thing>' or 'what do you remember'."


assistant.register("memory", ["remember", "recall", "memory"], remember)
