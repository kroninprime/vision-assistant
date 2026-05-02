from __future__ import annotations

import json
from urllib.parse import quote
from urllib.request import urlopen


def answer_doubt(question: str) -> str:
    query = quote(question)
    url = f"https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1&no_html=1"
    try:
        with urlopen(url, timeout=7) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return f"I could not fetch web knowledge right now: {exc}"

    abstract = (data.get("AbstractText") or "").strip()
    if abstract:
        source = data.get("AbstractSource") or "web source"
        return f"{abstract}\n\nSource: {source}"

    related = data.get("RelatedTopics") or []
    for item in related[:4]:
        if isinstance(item, dict) and item.get("Text"):
            return f"Here is what I found: {item['Text']}"

    return "I could not find a direct answer. Ask more specifically, like: 'explain black holes in simple terms'."
