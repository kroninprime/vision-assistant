import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    openai_api_key: str | None
    model: str
    wakeword: str
    data_dir: Path
    allow_folders: list[str]
    default_browser: str


def load_settings() -> Settings:
    data_dir = Path(os.getenv("JARVIS_DATA_DIR", Path.home() / ".jarvis"))
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("JARVIS_MODEL", "gpt-4o-mini"),
        wakeword=os.getenv("JARVIS_WAKEWORD", "hey jarvis"),
        data_dir=data_dir,
        allow_folders=os.getenv("JARVIS_ALLOW_FOLDERS", str(Path.home() / "Desktop")).split(";"),
        default_browser=os.getenv("JARVIS_BROWSER", "chrome"),
    )
