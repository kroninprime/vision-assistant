from __future__ import annotations

import os
from typing import Any

import requests

from jarvis.voice import ASRStream, TTSEngine, VoiceConfig


OPENAI_API_URL = "https://api.openai.com/v1/responses"
MODEL = "gpt-4o-mini"
SYSTEM_STYLE = (
    "You are a voice assistant speaking to a real person. "
    "Be warm, natural, and understanding. "
    "Keep answers clear and concise unless asked for detail. "
    "If the user sounds confused, acknowledge and explain simply."
)


def ask_ai(user_text: str, history: list[dict[str, str]]) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return "Please set OPENAI_API_KEY to enable AI responses."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {
        "model": MODEL,
        "instructions": SYSTEM_STYLE,
        "input": [
            *[
                {"role": item["role"], "content": item["content"]}
                for item in history[-8:]
            ],
            {"role": "user", "content": user_text},
        ],
    }

    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("output", [{}])[0].get("content", [{}])[0].get("text", "I could not generate a response.")
    except Exception as exc:
        return f"AI request failed: {exc}"


def main() -> None:
    config = VoiceConfig(enable_tts=True, microphone_enabled=True, keyboard_fallback=True)
    asr = ASRStream(config)
    tts = TTSEngine(config)

    print(f"[MIC] {asr.microphone_status()}")
    print("Say something. Type 'exit' to quit.")

    history: list[dict[str, str]] = []

    while True:
        spoken_text = asr.listen_once().strip()
        if not spoken_text:
            continue
        print(f"You: {spoken_text}")

        if spoken_text.lower() == "exit":
            tts.speak("Goodbye.")
            break

        answer = ask_ai(spoken_text, history)
        history.append({"role": "user", "content": spoken_text})
        history.append({"role": "assistant", "content": answer})
        tts.speak(answer)


if __name__ == "__main__":
    main()

