from typing import List, Dict
from jarvis.config import Settings

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None


def chat(settings: Settings, history: List[Dict[str, str]], prompt: str) -> str:
    """LLM call with context memory; falls back if no API key."""
    if OpenAI and settings.openai_api_key:
        client = OpenAI(api_key=settings.openai_api_key)
        messages = [{"role": "system", "content": "You are Jarvis. Be concise, safe, and actionable."}]
        messages += history
        messages.append({"role": "user", "content": prompt})
        try:
            resp = client.chat.completions.create(model=settings.model, messages=messages, max_tokens=200)
            return resp.choices[0].message.content
        except Exception:
            return "Brain offline (OpenAI error)."
    return "Brain offline: set OPENAI_API_KEY to enable full answers."
