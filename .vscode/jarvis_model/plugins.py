from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

from system_actions import close_app, open_app, open_website, run_safe_command, search_and_summarize, search_google, set_volume


PluginHandler = Callable[[str], str]


@dataclass
class Plugin:
    name: str
    description: str
    handler: PluginHandler


class PluginManager:
    def __init__(self) -> None:
        self.plugins: Dict[str, Plugin] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(
            Plugin(
                name="system.open",
                description="Open desktop application",
                handler=open_app,
            )
        )
        self.register(
            Plugin(
                name="system.close",
                description="Close desktop application",
                handler=close_app,
            )
        )
        self.register(
            Plugin(
                name="system.command",
                description="Run allowlisted shell command",
                handler=run_safe_command,
            )
        )
        self.register(
            Plugin(
                name="system.volume",
                description="Set system volume percent",
                handler=set_volume,
            )
        )
        self.register(
            Plugin(
                name="web.open",
                description="Open website in browser",
                handler=open_website,
            )
        )
        self.register(
            Plugin(
                name="web.search",
                description="Search query on Google",
                handler=search_google,
            )
        )
        self.register(
            Plugin(
                name="web.search_summary",
                description="Search and summarize top result",
                handler=search_and_summarize,
            )
        )

    def register(self, plugin: Plugin) -> None:
        self.plugins[plugin.name] = plugin

    def execute(self, plugin_name: str, payload: str) -> str:
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            return f"Plugin not found: {plugin_name}"
        return plugin.handler(payload)
