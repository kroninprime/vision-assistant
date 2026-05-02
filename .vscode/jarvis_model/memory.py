import sqlite3
from datetime import datetime


class MemoryStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_text TEXT NOT NULL,
                    assistant_text TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )

    def save_interaction(self, user_text: str, assistant_text: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO interactions(timestamp, user_text, assistant_text) VALUES (?, ?, ?)",
                (datetime.utcnow().isoformat(), user_text, assistant_text),
            )

    def recent_context(self, limit: int = 5) -> str:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT user_text, assistant_text FROM interactions ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        rows.reverse()
        return "\n".join([f"User: {u}\nJarvis: {a}" for u, a in rows])

    def set_preference(self, key: str, value: str) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO preferences(key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
                """,
                (key, value),
            )

    def get_preference(self, key: str) -> str | None:
        with self._conn() as conn:
            row = conn.execute("SELECT value FROM preferences WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    def list_preferences(self) -> dict[str, str]:
        with self._conn() as conn:
            rows = conn.execute("SELECT key, value FROM preferences ORDER BY key").fetchall()
        return {k: v for k, v in rows}
