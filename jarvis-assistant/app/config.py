import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    openai_api_key: str | None
    model: str
    wakeword: str
    data_dir: Path


def load_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("JARVIS_MODEL", "gpt-4o-mini"),
        wakeword=os.getenv("JARVIS_WAKEWORD", "hey jarvis"),
        data_dir=Path(os.getenv("JARVIS_DATA_DIR", Path.home() / ".jarvis")),
    )
