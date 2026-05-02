from __future__ import annotations

import json
from urllib.request import Request, urlopen

from openai import OpenAI

from config import settings


def _build_prompt(user_text: str, recent_context: str, screen_context: str) -> str:
    return (
        "You are Jarvis, a concise but helpful desktop AI assistant.\n"
        "Give direct answers, clear steps, and practical guidance.\n"
        "If user asks for code/project help, provide structured help.\n\n"
        f"Recent memory:\n{recent_context or '(none)'}\n\n"
        f"Screen OCR context:\n{screen_context or '(none)'}\n\n"
        f"User: {user_text}"
    )


def _ollama_reply(user_text: str, recent_context: str = "", screen_context: str = "") -> str:
    prompt = _build_prompt(user_text, recent_context, screen_context)
    body = json.dumps(
        {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
        }
    ).encode("utf-8")
    req = Request(
        f"{settings.ollama_base_url}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=45) as response:
            payload = json.loads(response.read().decode("utf-8"))
        text = (payload.get("response") or "").strip()
        return text or "Local AI returned an empty response."
    except Exception as exc:
        return f"Ollama request failed: {exc}"


def _openai_reply(user_text: str, recent_context: str = "", screen_context: str = "") -> str:
    client = OpenAI(api_key=settings.openai_api_key)
    system_prompt = (
        "You are Jarvis, a concise but helpful desktop AI assistant. "
        "Give direct answers, clear steps, and practical guidance. "
        "If user asks for code/project help, provide structured help."
    )
    context_block = (
        f"Recent memory:\n{recent_context or '(none)'}\n\n"
        f"Screen OCR context:\n{screen_context or '(none)'}"
    )
    response = client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": context_block},
            {"role": "user", "content": user_text},
        ],
        temperature=0.5,
    )
    text = (response.output_text or "").strip()
    return text or "I could not produce a response. Please try again."


def _basic_local_reply(user_text: str, recent_context: str = "", screen_context: str = "") -> str:
    text = user_text.strip()
    low = text.lower()
    if any(word in low for word in ("what", "why", "how", "explain")):
        return (
            f"Here is a clear explanation for '{text}':\n"
            "- Core idea: break the topic into smaller parts.\n"
            "- Practical step: start with one simple example and test it.\n"
            "- Next step: tell me your exact goal and I will give a targeted action plan."
        )
    if any(word in low for word in ("project", "website", "game", "portfolio")):
        return (
            "I can build this directly. Use one of these commands:\n"
            "- create website about <topic>\n"
            "- build game on <topic>\n"
            "- create project on <topic>\n"
            "- create portfolio about <topic>"
        )
    context_note = "I loaded your recent context." if recent_context else "No prior context loaded."
    screen_note = "Screen context is available." if screen_context else "No screen context."
    return f"I understood: '{text}'. {context_note} {screen_note} Tell me the exact output you want and I will generate it."


def chat_reply(user_text: str, recent_context: str = "", screen_context: str = "") -> str:
    try:
        if settings.openai_api_key:
            return _openai_reply(user_text, recent_context=recent_context, screen_context=screen_context)
        local = _ollama_reply(user_text, recent_context=recent_context, screen_context=screen_context)
        if local.startswith("Ollama request failed:"):
            return _basic_local_reply(user_text, recent_context=recent_context, screen_context=screen_context)
        return local
    except Exception as exc:
        return _basic_local_reply(user_text, recent_context=recent_context, screen_context=screen_context)
