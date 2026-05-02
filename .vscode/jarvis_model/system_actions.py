import subprocess
import webbrowser
from urllib.parse import quote_plus
from urllib.request import urlopen
import json
from pathlib import Path
import os
import pyautogui


SAFE_COMMAND_PREFIXES = ("dir", "echo", "whoami", "time", "date")
COMMON_FILE_ROOTS = [
    Path.home() / "Desktop",
    Path.home() / "Downloads",
    Path.home() / "Documents",
    Path.home() / "Pictures",
]


def open_app(app_name: str) -> str:
    app_map = {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "vscode": "Code.exe",
    }
    target = app_map.get(app_name.lower(), app_name).strip()
    try:
        if target.lower().startswith(("open ", "start ")):
            target = target.split(" ", 1)[1]
        if target.startswith("http://") or target.startswith("https://"):
            webbrowser.open(target)
            return f"Opened {target}"
        if "." in target and " " not in target and not target.endswith(".exe"):
            site = target if target.startswith(("http://", "https://")) else f"https://{target}"
            webbrowser.open(site)
            return f"Opened {site}"
        file_match = _find_file_by_name(target)
        if file_match:
            os.startfile(str(file_match))
            return f"Opened file: {file_match}"
        if Path(target).exists():
            os.startfile(str(Path(target)))
            return f"Opened path: {target}"
        subprocess.Popen(target)
        return f"Opened {app_name}"
    except Exception as exc:
        return f"Failed to open {app_name}: {exc}"


def _find_file_by_name(name: str) -> Path | None:
    needle = name.lower().strip()
    if not needle:
        return None
    for root in COMMON_FILE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.name.lower() == needle or needle in path.name.lower():
                return path
    return None


def run_safe_command(command: str) -> str:
    cleaned = command.strip().lower()
    if not cleaned.startswith(SAFE_COMMAND_PREFIXES):
        return "Blocked. Command is not in allowlist."
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True, timeout=10)
        output = (result.stdout or result.stderr or "").strip()
        return output[:1200] if output else "Command executed."
    except Exception as exc:
        return f"Command failed: {exc}"


def close_app(app_name: str) -> str:
    process_map = {
        "chrome": "chrome.exe",
        "notepad": "notepad.exe",
        "calculator": "CalculatorApp.exe",
        "vscode": "Code.exe",
    }
    process = process_map.get(app_name.lower(), app_name)
    command = f'taskkill /IM "{process}" /F'
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True, timeout=10)
        output = (result.stdout or result.stderr or "").strip()
        if result.returncode == 0:
            return f"Closed {app_name}"
        return f"Could not close {app_name}: {output[:300]}"
    except Exception as exc:
        return f"Close failed: {exc}"


def set_volume(value: str) -> str:
    try:
        level = int(value.strip())
    except ValueError:
        return "Volume must be a number between 0 and 100."
    level = max(0, min(level, 100))
    presses = int((100 - level) / 2)
    for _ in range(50):
        pyautogui.press("volumedown")
    for _ in range(max(0, 50 - presses)):
        pyautogui.press("volumeup")
    return f"Set volume near {level}%."


def open_website(url: str) -> str:
    site = url.strip()
    if not site.startswith(("http://", "https://")):
        site = "https://" + site
    webbrowser.open(site)
    return f"Opened website: {site}"


def search_google(query: str) -> str:
    q = quote_plus(query.strip())
    url = f"https://www.google.com/search?q={q}"
    webbrowser.open(url)
    return f"Searching Google for: {query}"


def search_and_summarize(query: str) -> str:
    q = quote_plus(query.strip())
    url = f"https://api.duckduckgo.com/?q={q}&format=json&no_redirect=1&no_html=1"
    try:
        with urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return f"Search failed: {exc}"

    webbrowser.open(f"https://www.google.com/search?q={q}")
    lines = []
    abstract = (data.get("AbstractText") or "").strip()
    if abstract:
        lines.append(f"Top summary: {abstract}")
    related = data.get("RelatedTopics") or []
    for item in related:
        if isinstance(item, dict) and item.get("Text"):
            lines.append(f"- {item['Text']}")
        if len(lines) >= 4:
            break
    if not lines:
        return f"Searched Google for '{query}'. No quick summary found."
    return f"Searched Google for '{query}'.\n" + "\n".join(lines)


def automation_click(x: int, y: int) -> str:
    pyautogui.click(x=x, y=y)
    return f"Clicked at ({x}, {y})"


def automation_type(text: str) -> str:
    pyautogui.typewrite(text, interval=0.02)
    return "Typed text."


def automation_hotkey(*keys: str) -> str:
    pyautogui.hotkey(*keys)
    return f"Pressed hotkey: {' + '.join(keys)}"
