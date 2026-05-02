from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .models import ActivationEvent


@dataclass
class TriggerFusion:
    arm_window_seconds: int = 10
    wake_threshold: float = 0.7
    _armed_until: datetime | None = None

    def arm_from_clap(self, confidence: float) -> ActivationEvent | None:
        if confidence < 0.6:
            return None
        self._armed_until = datetime.now() + timedelta(seconds=self.arm_window_seconds)
        return ActivationEvent(source="clap", confidence=confidence)

    def activate_from_wake_phrase(self, confidence: float) -> ActivationEvent | None:
        if confidence < self.wake_threshold:
            return None
        now = datetime.now()
        if self._armed_until and now <= self._armed_until:
            return ActivationEvent(source="clap+wake_phrase", confidence=0.95)
        return ActivationEvent(source="wake_phrase", confidence=confidence)


class ClapDetector:
    """Simple clap trigger recognizer with text fallback."""

    def detect(self) -> float:
        return 0.0

    def detect_from_text(self, transcript: str) -> float:
        lowered = transcript.lower().strip()
        if lowered in {"clap", "👏", "double clap"}:
            return 0.95
        if "clap" in lowered:
            return 0.7
        return 0.0


class WakeWordDetector:
    def __init__(self, wake_words: tuple[str, ...] = ("wake up jarvis", "hey jarvis")) -> None:
        self.wake_words = wake_words

    def score(self, transcript: str) -> float:
        normalized = transcript.lower().strip()
        return 0.9 if any(w in normalized for w in self.wake_words) else 0.0


class PresenceGate:
    def is_present(self) -> bool:
        return True

