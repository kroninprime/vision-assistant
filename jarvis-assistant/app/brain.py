"""
Thin brain wrapper: routes to OpenAI if API key present; otherwise echoes guidance.
"""

from typing import List, Dict
from app.config import Settings

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None


def chat(settings: Settings, history: List[Dict[str, str]], prompt: str) -> str:
    if OpenAI and settings.openai_api_key:
        client = OpenAI(api_key=settings.openai_api_key)
        messages = history + [
            {"role": "system", "content": "You are Jarvis. Be concise, actionable, and safe on the user's PC."},
            {"role": "user", "content": prompt},
        ]
        try:
            resp = client.chat.completions.create(model=settings.model, messages=messages, max_tokens=256)
            return resp.choices[0].message.content
        except Exception:
            return "Brain offline (OpenAI error)."
    return "Brain offline: set OPENAI_API_KEY to enable rich answers."
