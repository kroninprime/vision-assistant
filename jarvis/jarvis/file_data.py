from __future__ import annotations

from pathlib import Path


class FileDataManager:
    def search_files(self, root: str, query: str) -> str:
        base = Path(root)
        if not base.exists():
            return "Search root does not exist."
        matches = [str(p) for p in base.rglob("*") if query.lower() in p.name.lower()][:10]
        if not matches:
            return f"No files found for {query}."
        return "Found: " + "; ".join(matches)

    def create_folder(self, path: str) -> str:
        Path(path).mkdir(parents=True, exist_ok=True)
        return f"Created folder {path}."

