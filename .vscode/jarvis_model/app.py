import asyncio
import json
from pathlib import Path
import threading
from typing import Set

import pyttsx3
import speech_recognition as sr
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from memory import MemoryStore
from models import CommandRequest, CommandResponse, ListenResponse
from planner import plan_and_execute
from vision import extract_screen_text

app = FastAPI(title="Jarvis MVP")
memory = MemoryStore(settings.memory_db)
voice_engine = pyttsx3.init()
clients: Set[WebSocket] = set()
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


async def broadcast(state: str, message: str = "") -> None:
    payload = json.dumps({"state": state, "message": message})
    dead = []
    for ws in clients:
        try:
            await ws.send_text(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.discard(ws)


def speak(text: str) -> None:
    voice_engine.say(text)
    voice_engine.runAndWait()


def capture_voice_once(timeout: int = 6, phrase_time_limit: int = 8) -> tuple[str, str]:
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        transcript = recognizer.recognize_google(audio)
        return transcript, ""
    except sr.WaitTimeoutError:
        return "", "I did not hear anything. Speak closer to the mic."
    except sr.UnknownValueError:
        return "", "I heard audio but could not understand words."
    except sr.RequestError as exc:
        return "", f"Speech service request failed: {exc}"
    except OSError as exc:
        return "", f"Mic device error: {exc}"
    except Exception as exc:
        return "", f"Unexpected mic error: {exc}"


async def process_command(text: str, include_screen_context: bool = False) -> str:
    await broadcast("thinking", text)
    screen_context = ""
    if include_screen_context:
        await broadcast("acting", "Capturing screen context")
        try:
            screen_context = extract_screen_text(settings.tesseract_cmd)
        except Exception as exc:
            screen_context = f"OCR failed: {exc}"

    await broadcast("acting", "Executing action plan")
    result = plan_and_execute(text, screen_context, memory=memory)
    memory.save_interaction(text, result)
    await broadcast("speaking", result)
    speak(result)
    await broadcast("idle", "")
    return result


@app.get("/")
def home() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/capabilities")
def capabilities() -> dict:
    return {
        "available_now": [
            "Voice/text command UI with speaking responses",
            "Open apps, websites, and common local files",
            "Google search and summarized results",
            "Create portfolio/project/website/game from topic",
            "Screen OCR context (optional)",
            "Memory for interactions and preferences",
            "Local free AI chat with Ollama (or OpenAI key path)",
        ],
        "not_movie_complete_yet": [
            "Always-on wake-word reliability without cloud dependencies",
            "True OS-deep control for all apps with robust permissions",
            "Autonomous long-horizon planning with guaranteed safety",
            "Full screen understanding with GUI element grounding",
            "Human-level reasoning and zero-error execution",
        ],
    }


@app.post("/command", response_model=CommandResponse)
async def command(req: CommandRequest) -> CommandResponse:
    result = await process_command(req.text, req.include_screen_context)
    return CommandResponse(status="ok", response=result)


@app.post("/listen", response_model=ListenResponse)
async def listen() -> ListenResponse:
    await broadcast("listening", "Listening from system microphone...")
    transcript, error = await asyncio.to_thread(capture_voice_once)
    if error:
        await broadcast("idle", error)
        return ListenResponse(status="error", error=error)
    await broadcast("thinking", transcript)
    return ListenResponse(status="ok", transcript=transcript)


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    clients.add(websocket)
    await websocket.send_text(json.dumps({"state": "idle", "message": "connected"}))
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        clients.discard(websocket)


def wake_word_loop() -> None:
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
            heard = recognizer.recognize_google(audio).lower()
            if settings.wake_word in heard:
                with mic as source:
                    command_audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
                text = recognizer.recognize_google(command_audio)
                loop.run_until_complete(broadcast("listening", text))
                loop.run_until_complete(process_command(text, include_screen_context=False))
        except Exception:
            continue


@app.on_event("startup")
def start_background_services() -> None:
    if settings.enable_wake_word:
        thread = threading.Thread(target=wake_word_loop, daemon=True)
        thread.start()
