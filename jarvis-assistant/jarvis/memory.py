import sqlite3
from pathlib import Path
from typing import List, Tuple


class MemoryStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, text TEXT)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, role TEXT, content TEXT)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS actions (id INTEGER PRIMARY KEY, action TEXT, input TEXT, output TEXT, created_at TEXT)"
            )

    def add_memory(self, text: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO memories(text) VALUES (?)", (text,))

    def list_memories(self, limit: int = 20) -> List[str]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT text FROM memories ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [r[0] for r in rows]

    def add_history(self, role: str, content: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO history(role, content) VALUES (?,?)",
                (role, content),
            )

    def get_history(self, limit: int = 10) -> List[Tuple[str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT role, content FROM history ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return rows[::-1]

    def store_action(self, action: str, input: str, output: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO actions(action, input, output, created_at) VALUES (?, ?, ?, datetime('now'))",
                (action, input, output),
            )

    def get_actions(self, limit: int = 20) -> List[Tuple[str, str, str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT action, input, output, created_at FROM actions ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return rows
