from __future__ import annotations

import os
import webbrowser
from datetime import datetime

import psutil


class ComputerControl:
    def open_app(self, raw_command: str) -> str:
        cmd = raw_command.lower()
        if "notepad" in cmd:
            os.system("start notepad")
            return "Opening Notepad."
        if "calculator" in cmd:
            os.system("start calc")
            return "Opening Calculator."
        if "browser" in cmd or "chrome" in cmd:
            webbrowser.open("https://www.google.com")
            return "Opening browser."
        app_guess = cmd.replace("open", "").strip().strip('"')
        if app_guess:
            result = os.system(f'start "" "{app_guess}"')
            if result == 0:
                return f"Opening {app_guess}."
        return "I could not open that app yet. Try saying open browser, open notepad, or open calculator."

    def system_status(self) -> str:
        cpu = psutil.cpu_percent(interval=0.2)
        mem = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        battery_txt = f"{battery.percent:.0f}% {'charging' if battery.power_plugged else 'on battery'}" if battery else "unknown"
        return f"CPU at {cpu:.0f} percent, memory at {mem:.0f} percent, battery {battery_txt}."

    def ui_action(self, raw_command: str) -> str:
        try:
            import pyautogui
        except Exception:
            return "UI automation is unavailable. Install pyautogui to enable mouse and keyboard control."

        cmd = raw_command.lower()
        if "move mouse" in cmd:
            pyautogui.moveRel(100, 0, duration=0.2)
            return "Moved mouse."
        if "click" in cmd:
            pyautogui.click()
            return "Clicked current cursor position."
        if "type " in cmd:
            text = raw_command.split("type", 1)[1].strip()
            if text:
                pyautogui.write(text, interval=0.03)
                return "Typed requested text."
        return "UI automation command not recognized."


class InternetAutomation:
    def web_search(self, query: str) -> str:
        query = query.strip() or "latest technology news"
        webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        return f"Searching web for {query}."

    def youtube_search(self, query: str) -> str:
        query = query.strip() or "technology"
        webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
        return f"Searching YouTube for {query}."

    def latest_news(self) -> str:
        webbrowser.open("https://news.google.com/")
        return "Opening latest news."


class LifeManager:
    def __init__(self) -> None:
        self.tasks: list[str] = []
        self.calendar_events: list[str] = ["Physics prep at 6 PM", "Project sync tomorrow 10 AM"]

    def create_reminder(self, text: str) -> str:
        self.tasks.append(f"{datetime.now().isoformat(timespec='minutes')}: {text}")
        return "Reminder saved."

    def summary(self) -> str:
        if not self.tasks:
            return "No pending tasks."
        return f"You have {len(self.tasks)} pending tasks."

    def calendar_summary(self) -> str:
        if not self.calendar_events:
            return "Your calendar is clear."
        return "Upcoming: " + "; ".join(self.calendar_events[:3])

    def email_summary(self) -> str:
        return "Email digest: 2 important, 5 normal, no critical alerts."

