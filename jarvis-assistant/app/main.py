import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Any, List

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from jarvis.config import load_settings, Settings
from jarvis import brain
from jarvis.memory import MemoryStore
from jarvis.automation import system as sys_auto
from jarvis.automation import files as file_auto
from jarvis.automation import mouse as mouse_auto
from jarvis.automation import screen as screen_auto
from jarvis.automation import web as web_auto
from jarvis.tasks import planner


logger = logging.getLogger("jarvis")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class Command(BaseModel):
    text: str
    history: List[Dict[str, str]] | None = None


@dataclass
class Skill:
    name: str
    keywords: List[str]
    handler: Callable[[str], str]


class JarvisAssistant:
    """Minimal event loop + skill registry for a Jarvis-style assistant."""

    def __init__(self) -> None:
        self.skills: List[Skill] = []
        self.loop = asyncio.get_event_loop()

    def register(self, name: str, keywords: List[str], handler: Callable[[str], str]) -> None:
        logger.info("Registering skill: %s (%s)", name, ",".join(keywords))
        self.skills.append(Skill(name=name, keywords=keywords, handler=handler))

    def handle(self, prompt: str) -> str:
        """Pick the first skill whose keyword appears in the prompt."""
        p = prompt.lower()
        for skill in self.skills:
            if any(key in p for key in skill.keywords):
                return skill.handler(prompt)
        # automation fallbacks
        for handler in (
            lambda: sys_auto.handle_system(prompt),
            lambda: file_auto.handle_files(prompt, settings.allow_folders),
            lambda: mouse_auto.handle_mouse(prompt),
            lambda: screen_auto.handle_screen(prompt),
            lambda: web_auto.handle_web(prompt),
            lambda: planner.plan_and_execute(prompt),
        ):
            res = handler()
            if res:
                return res
        return ""

    async def background_tick(self) -> None:
        """Placeholder for proactive/background jobs."""
        while True:
            logger.debug("Background tick...")
            await asyncio.sleep(60)  # run every minute; expand with real work


assistant = JarvisAssistant()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
settings: Settings = load_settings()
memory = MemoryStore(settings.data_dir / "jarvis.db")

app = FastAPI(title="Jarvis Assistant", version="0.1.0")

# Serve static UI
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root() -> FileResponse:
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return FileResponse(BASE_DIR / "fallback.html")  # added below


@app.get("/status")
async def status() -> Dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
async def startup() -> None:
    # Import here so skills can register themselves at import time
    try:
        from skills import example_skill  # noqa: F401
        from skills import app_control  # noqa: F401
        from skills import reminders  # noqa: F401
        from skills import weather  # noqa: F401
        from skills import qa  # noqa: F401
        from skills import site_builder  # noqa: F401
        from skills import search  # noqa: F401
        from skills import system_control  # noqa: F401
        from skills import file_manager  # noqa: F401
        from skills import mouse_keyboard  # noqa: F401
        from skills import screen_vision  # noqa: F401
        from skills import web_automation  # noqa: F401
        from skills import memory  # noqa: F401
    except Exception as exc:  # pragma: no cover - best-effort import
        logger.warning("Failed to load skills: %s", exc)

    # launch background loop
    asyncio.create_task(assistant.background_tick())
    logger.info("Jarvis is up and listening.")


@app.post("/command")
async def command(cmd: Command) -> Dict[str, Any]:
    # skill pass
    response = assistant.handle(cmd.text)
    # if no skill matched, ask LLM
    history = cmd.history or []
    if not response:
        response = brain.chat(settings, history, cmd.text)
    # store history
    memory.add_history("user", cmd.text)
    memory.add_history("assistant", response)
    return {"reply": response}
