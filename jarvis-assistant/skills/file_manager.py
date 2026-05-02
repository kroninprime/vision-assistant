import shutil
from pathlib import Path

from app.main import assistant

SAFE_ROOT = Path(r"C:\Users\PERI\Desktop")  # adjust as needed


def file_skill(prompt: str) -> str:
    lower = prompt.lower()
    parts = lower.split()
    try:
        if "list" in parts:
            files = [p.name for p in SAFE_ROOT.iterdir()]
            return "Files: " + ", ".join(files[:30])
        if "create" in parts:
            name = parts[-1]
            target = SAFE_ROOT / name
            target.touch()
            return f"Created {target}"
        if "delete" in parts:
            name = parts[-1]
            target = SAFE_ROOT / name
            if target.is_file():
                target.unlink()
                return f"Deleted {target}"
        if "move" in parts:
            src = SAFE_ROOT / parts[-2]
            dst = SAFE_ROOT / parts[-1]
            shutil.move(str(src), str(dst))
            return f"Moved {src} to {dst}"
    except Exception as exc:
        return f"File action failed: {exc}"
    return "Say list/create/delete/move <name> within Desktop."


assistant.register("files", ["file", "files", "folder", "delete", "create", "move"], file_skill)
