from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


HIGH_RISK_INTENTS = {"install_software", "uninstall_software", "delete_file", "run_shell"}


@dataclass
class AuditLog:
    events: list[str] = field(default_factory=list)

    def record(self, text: str) -> None:
        self.events.append(f"{datetime.now().isoformat(timespec='seconds')} | {text}")


class Permissions:
    def allowed(self, intent_name: str) -> bool:
        return intent_name not in HIGH_RISK_INTENTS


class VoiceAuth:
    def verify(self) -> bool:
        return True


class FaceAuth:
    def verify(self) -> bool:
        return True

