from __future__ import annotations

import subprocess
import time
import webbrowser
from pathlib import Path
from urllib.request import urlopen

import pyttsx3
from pynput import keyboard


HOST = "127.0.0.1"
PORT = 8000
BASE_URL = f"http://{HOST}:{PORT}"
DOUBLE_TAP_SECONDS = 0.45

ROOT = Path(__file__).parent
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
OLLAMA_CMD = "ollama"

last_ctrl_tap = 0.0
voice = pyttsx3.init()


def _is_server_up() -> bool:
    try:
        with urlopen(f"{BASE_URL}/", timeout=1.2):
            return True
    except Exception:
        return False


def _start_jarvis_server() -> None:
    if _is_server_up():
        return
    python_bin = str(VENV_PYTHON if VENV_PYTHON.exists() else "python")
    subprocess.Popen(
        [python_bin, "-m", "uvicorn", "app:app", "--host", HOST, "--port", str(PORT)],
        cwd=str(ROOT),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    for _ in range(20):
        if _is_server_up():
            return
        time.sleep(0.4)


def _start_ollama_if_possible() -> None:
    try:
        subprocess.Popen(
            [OLLAMA_CMD, "serve"],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    except Exception:
        pass


def _wake_jarvis() -> None:
    _start_ollama_if_possible()
    _start_jarvis_server()
    webbrowser.open(BASE_URL)
    try:
        voice.say("Yes boss, Jarvis online.")
        voice.runAndWait()
    except Exception:
        pass


def on_press(key: keyboard.Key | keyboard.KeyCode) -> None:
    global last_ctrl_tap
    if key not in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        return
    now = time.time()
    if now - last_ctrl_tap <= DOUBLE_TAP_SECONDS:
        _wake_jarvis()
        last_ctrl_tap = 0.0
    else:
        last_ctrl_tap = now


def main() -> None:
    print("Jarvis daemon running. Double-tap Ctrl to wake Jarvis.")
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()


if __name__ == "__main__":
    main()
