import shutil
from pathlib import Path
from typing import List


def handle_files(prompt: str, allow_folders: List[str]) -> str:
    lower = prompt.lower()
    tokens = lower.split()
    root = Path(allow_folders[0])
    try:
        if "list" in tokens:
            files = [p.name for p in root.iterdir()]
            return "Files: " + ", ".join(files[:30])
        if "create" in tokens:
            name = tokens[-1]
            target = root / name
            target.touch()
            return f"Created {target}"
        if "delete" in tokens:
            name = tokens[-1]
            target = root / name
            if target.exists():
                target.unlink()
                return f"Deleted {target}"
        if "move" in tokens:
            src = root / tokens[-2]
            dst = root / tokens[-1]
            shutil.move(str(src), str(dst))
            return f"Moved {src} to {dst}"
    except Exception as exc:
        return f"File action failed: {exc}"
    return ""
