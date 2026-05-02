from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ActivationEvent:
    source: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Intent:
    name: str
    entities: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5


@dataclass
class PlanStep:
    action: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskPlan:
    original_request: str
    steps: list[PlanStep]

