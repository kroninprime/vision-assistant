import pyautogui
from app.main import assistant


def mouse_skill(prompt: str) -> str:
    lower = prompt.lower()
    if "click" in lower:
        pyautogui.click()
        return "Clicked."
    if "double" in lower:
        pyautogui.doubleClick()
        return "Double click."
    if "move" in lower:
        pyautogui.moveRel(100, 0, duration=0.2)
        return "Moved mouse."
    if "type" in lower:
        text = prompt.replace("type", "").strip()
        pyautogui.typewrite(text)
        return f"Typed: {text}"
    return "Say click, double click, move, or type <text>."


assistant.register("mouse", ["click", "double", "move mouse", "type"], mouse_skill)
