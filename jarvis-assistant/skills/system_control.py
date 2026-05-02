import os
import subprocess
import psutil  # type: ignore

from app.main import assistant


def system_skill(prompt: str) -> str:
    lower = prompt.lower()
    if "shutdown" in lower or "shut down pc" in lower:
        subprocess.Popen(["shutdown", "/s", "/t", "5"])
        return "Shutting down in 5 seconds."
    if "restart" in lower or "reboot" in lower:
        subprocess.Popen(["shutdown", "/r", "/t", "5"])
        return "Restarting in 5 seconds."
    if "cpu" in lower:
        return f"CPU usage {psutil.cpu_percent()}%"
    if "ram" in lower:
        mem = psutil.virtual_memory()
        return f"Memory used {mem.percent}%"
    return "System control ready. Say shutdown, restart, cpu, or ram."


assistant.register("system", ["shutdown", "restart", "cpu", "ram", "reboot"], system_skill)
