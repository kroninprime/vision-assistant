import subprocess
from pathlib import Path
from typing import List

from app.main import assistant

# Allow-listed apps (keep safe)
APP_MAP = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "vs code": r"C:\Users\PERI\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "spotify": r"C:\Users\PERI\AppData\Roaming\Spotify\Spotify.exe",
    "notepad": "notepad.exe",
    "explorer": "explorer.exe",
}

SAFE_FOLDERS: List[str] = [r"C:\Users\PERI\Desktop"]


def open_app(prompt: str) -> str:
    lower = prompt.lower()
    for name, path in APP_MAP.items():
        if name in lower:
            subprocess.Popen(path if isinstance(path, list) else [path], shell=False)
            return f"Opening {name}."
    return "App not in allow-list. Add it to APP_MAP."


def open_website(prompt: str) -> str:
    import webbrowser
    lower = prompt.lower()
    parts = lower.split()
    url = None
    if "open" in parts:
        idx = parts.index("open")
        if idx + 1 < len(parts):
            url = parts[idx + 1]
    if not url:
        return "Say 'open <site>' like 'open youtube.com'"
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opening {url}."


def volume_control(prompt: str) -> str:
    # Send media keys via PowerShell
    key = None
    if "mute" in prompt.lower():
        key = 173  # VK_VOLUME_MUTE
    elif "up" in prompt.lower() or "increase" in prompt.lower():
        key = 175  # VK_VOLUME_UP
    elif "down" in prompt.lower() or "decrease" in prompt.lower():
        key = 174  # VK_VOLUME_DOWN
    if key:
        subprocess.run(
            ["powershell", "-Command", f"(New-Object -ComObject WScript.Shell).SendKeys([char]{key})"],
            capture_output=True,
        )
        return "Volume adjusted."
    return "Say mute, volume up, or volume down."


assistant.register("open app", ["open", "launch", "start"], open_app)
assistant.register("website", ["open website", "open site", "youtube", "gmail", "google"], open_website)
assistant.register("volume", ["volume", "mute", "louder", "softer"], volume_control)
