"""OCR (Optical Character Recognition) for screen text extraction."""
import logging
from typing import Optional

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

from PIL import Image

logger = logging.getLogger("jarvis.vision.ocr")


class OCRHandler:
    """Extract text from images using OCR."""

    def __init__(self):
        self.available = HAS_TESSERACT
        if not self.available:
            logger.warning("Tesseract not installed. Install: pip install pytesseract")

    def extract_text_from_image(self, image: Image.Image) -> str:
        """Extract text from PIL Image."""
        if not self.available:
            return "OCR not available (install pytesseract)"

        try:
            text = pytesseract.image_to_string(image)
            logger.debug(f"OCR extracted {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}", exc_info=True)
            return ""

    def extract_text_from_file(self, filepath: str) -> str:
        """Extract text from image file."""
        try:
            img = Image.open(filepath)
            return self.extract_text_from_image(img)
        except Exception as e:
            logger.error(f"Failed to open image {filepath}: {e}")
            return ""

    def extract_text_with_confidence(self, image: Image.Image) -> dict:
        """Extract text with confidence scores."""
        if not self.available:
            return {"text": "OCR not available", "confidence": 0.0}

        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            # Calculate average confidence
            confidences = [int(conf) for conf in data["confidence"] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            text = pytesseract.image_to_string(image)

            return {"text": text, "confidence": avg_confidence / 100.0}
        except Exception as e:
            logger.error(f"OCR with confidence failed: {e}")
            return {"text": "", "confidence": 0.0}
