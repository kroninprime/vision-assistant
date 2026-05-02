from __future__ import annotations


class PhoneBridge:
    def status(self) -> str:
        return "Phone bridge connected."


class SmartHomeBridge:
    def status(self) -> str:
        return "Smart home bridge connected."


class PluginLoader:
    def __init__(self) -> None:
        self.plugins: dict[str, str] = {}

    def register(self, name: str, description: str) -> None:
        self.plugins[name] = description

    def list_plugins(self) -> list[str]:
        return [f"{k}: {v}" for k, v in self.plugins.items()]

