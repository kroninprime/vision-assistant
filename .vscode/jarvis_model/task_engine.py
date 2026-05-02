from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Callable, List, Tuple

from plugins import PluginManager


@dataclass
class TaskStep:
    label: str
    execute: Callable[[], str]


class TaskEngine:
    def __init__(self, plugin_manager: PluginManager) -> None:
        self.plugin_manager = plugin_manager

    def build_steps(self, command: str) -> List[TaskStep]:
        text = command.lower().strip()
        steps: List[TaskStep] = []

        if "open " in text and "search " in text:
            app_name = text.split("open ", 1)[1].split(" and ", 1)[0].strip()
            query = text.split("search ", 1)[1].strip()
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            steps.extend(
                [
                    TaskStep(
                        label=f"Open {app_name}",
                        execute=lambda n=app_name: self.plugin_manager.execute("system.open", n),
                    ),
                    TaskStep(
                        label=f"Run search for {query}",
                        execute=lambda u=search_url: self.plugin_manager.execute("system.open", u),
                    ),
                ]
            )

        if "organize downloads" in text:
            steps.extend(self._downloads_organizer_steps())

        return steps

    def execute_steps(self, steps: List[TaskStep]) -> Tuple[List[str], str]:
        logs: List[str] = []
        for idx, step in enumerate(steps, start=1):
            try:
                result = step.execute()
                logs.append(f"{idx}. {step.label} -> {result}")
            except Exception as exc:
                logs.append(f"{idx}. {step.label} -> failed: {exc}")
                return logs, "failed"
        return logs, "completed"

    def _downloads_organizer_steps(self) -> List[TaskStep]:
        downloads = Path.home() / "Downloads"
        known_types = {
            ".pdf": "PDFs",
            ".doc": "Docs",
            ".docx": "Docs",
            ".xlsx": "Sheets",
            ".csv": "Sheets",
            ".jpg": "Images",
            ".jpeg": "Images",
            ".png": "Images",
            ".zip": "Archives",
            ".rar": "Archives",
            ".mp4": "Videos",
        }

        def organize() -> str:
            if not downloads.exists():
                return "Downloads folder not found."
            moved = 0
            for item in downloads.iterdir():
                if item.is_dir():
                    continue
                folder_name = known_types.get(item.suffix.lower(), "Others")
                target = downloads / folder_name
                target.mkdir(exist_ok=True)
                destination = target / item.name
                if destination.exists():
                    continue
                shutil.move(str(item), str(destination))
                moved += 1
            return f"Organized Downloads. Moved {moved} files."

        return [TaskStep(label="Organize Downloads by file type", execute=organize)]
