import io
import mss
import pytesseract
from PIL import Image


def handle_screen(prompt: str) -> str:
    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[0])
        img = Image.frombytes("RGB", shot.size, shot.rgb)
        text = pytesseract.image_to_string(img)
    if text.strip():
        return f"I see: {text[:400]}"
    return "Captured screen but no readable text."
