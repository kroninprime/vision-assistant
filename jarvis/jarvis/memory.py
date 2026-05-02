from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class ShortTermMemory:
    window: int = 20
    _events: deque[str] = field(default_factory=deque)

    def add(self, item: str) -> None:
        self._events.append(item)
        while len(self._events) > self.window:
            self._events.popleft()

    def recent(self) -> list[str]:
        return list(self._events)


@dataclass
class LongTermMemory:
    preferences: dict[str, str] = field(default_factory=dict)
    habits: dict[str, int] = field(default_factory=dict)

    def remember_preference(self, key: str, value: str) -> None:
        self.preferences[key] = value

    def track_habit(self, key: str) -> None:
        self.habits[key] = self.habits.get(key, 0) + 1


class VectorStore:
    def __init__(self) -> None:
        self._docs: list[str] = []

    def add(self, text: str) -> None:
        self._docs.append(text)

    def query(self, text: str, limit: int = 3) -> list[str]:
        return [d for d in self._docs if text.lower() in d.lower()][:limit]


class MemoryPolicies:
    def retain(self, text: str) -> bool:
        return len(text.strip()) > 2

