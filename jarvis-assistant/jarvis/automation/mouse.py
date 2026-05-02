import pyautogui


def handle_mouse(prompt: str) -> str:
    lower = prompt.lower()
    if "double" in lower:
        pyautogui.doubleClick()
        return "Double click."
    if "click" in lower:
        pyautogui.click()
        return "Clicked."
    if "move" in lower:
        pyautogui.moveRel(100, 0, duration=0.2)
        return "Moved mouse."
    if "type" in lower:
        text = prompt.replace("type", "").strip()
        pyautogui.typewrite(text)
        return f"Typed: {text}"
    return ""
