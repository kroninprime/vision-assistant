from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .core import JarvisCore


BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_PATH = BASE_DIR / "chat_history.json"
TEMPLATE_PATH = BASE_DIR / "web" / "index.html"

app = FastAPI(title="Jarvis Web")
jarvis = JarvisCore()


class MessageIn(BaseModel):
    message: str


class ListenResult(BaseModel):
    transcript: str


class ToggleIn(BaseModel):
    enabled: bool


class TriggerIn(BaseModel):
    source: str


def load_history() -> list[dict[str, str]]:
    if HISTORY_PATH.exists():
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    return []


def save_history(history: list[dict[str, str]]) -> None:
    HISTORY_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return TEMPLATE_PATH.read_text(encoding="utf-8")


@app.get("/api/history")
def get_history() -> list[dict[str, str]]:
    return load_history()


@app.post("/api/message")
def send_message(payload: MessageIn) -> dict[str, str]:
    user_text = payload.message.strip()
    bot_text = jarvis.handle_text(user_text)
    history = load_history()
    stamp = datetime.now().isoformat(timespec="seconds")
    history.append({"role": "user", "text": user_text, "time": stamp})
    history.append({"role": "jarvis", "text": bot_text, "time": stamp})
    save_history(history)
    return {"reply": bot_text}


@app.get("/api/mic-status")
def mic_status() -> dict[str, str]:
    return {"status": jarvis.asr.microphone_status()}


@app.post("/api/listen")
def listen_once() -> ListenResult:
    transcript = jarvis.capture_from_system_mic()
    return ListenResult(transcript=transcript)


@app.get("/api/features")
def features() -> dict[str, dict[str, str]]:
    return jarvis.feature_matrix()


@app.post("/api/wake")
def wake(payload: TriggerIn) -> dict[str, str]:
    return {"reply": jarvis.trigger_wake(payload.source)}


@app.post("/api/continuous-listening")
def set_continuous_listening(payload: ToggleIn) -> dict[str, str]:
    return {"reply": jarvis.toggle_continuous_listen(payload.enabled)}


@app.post("/api/history/clear")
def clear_history() -> dict[str, str]:
    save_history([])
    return {"status": "ok"}


app.mount("/static", StaticFiles(directory=str(BASE_DIR / "web")), name="static")

