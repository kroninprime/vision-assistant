import io
import base64
import mss
import pytesseract
from PIL import Image

from app.main import assistant


def screen_describe(prompt: str) -> str:
    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[0])
        img = Image.frombytes("RGB", shot.size, shot.rgb)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        text = pytesseract.image_to_string(img)
    if not text.strip():
        return "I captured the screen but could not read text."
    return f"I see on screen: {text[:400]}"


assistant.register("screen", ["what is on my screen", "screen", "describe screen", "screenshot"], screen_describe)
