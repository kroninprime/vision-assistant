from PIL import ImageGrab
import pytesseract


def extract_screen_text(tesseract_cmd: str = "") -> str:
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    screenshot = ImageGrab.grab()
    text = pytesseract.image_to_string(screenshot)
    return text.strip()
