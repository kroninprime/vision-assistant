"""Screen capture and awareness module."""
import logging
from pathlib import Path
from typing import Optional

import mss
from PIL import Image
import io

logger = logging.getLogger("jarvis.vision")


class ScreenReader:
    """Capture and analyze screen content."""

    def __init__(self, save_dir: Optional[Path] = None):
        self.sct = mss.mss()
        self.save_dir = save_dir or Path("./screenshots")
        self.save_dir.mkdir(exist_ok=True)
        self.last_screenshot: Optional[Image.Image] = None

    def capture_screen(self) -> Image.Image:
        """Capture current screen as PIL Image."""
        try:
            screenshot = self.sct.grab(self.sct.monitors[1])  # Primary monitor
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            self.last_screenshot = img
            logger.debug("Screen captured successfully")
            return img
        except Exception as e:
            logger.error(f"Screen capture failed: {e}", exc_info=True)
            raise

    def save_screenshot(self, filename: str = "screenshot.png") -> Path:
        """Save current screenshot to disk."""
        if self.last_screenshot is None:
            self.capture_screen()

        filepath = self.save_dir / filename
        self.last_screenshot.save(filepath)
        logger.info(f"Screenshot saved to {filepath}")
        return filepath

    def get_screen_dimensions(self) -> tuple[int, int]:
        """Get primary monitor dimensions (width, height)."""
        monitor = self.sct.monitors[1]
        return (monitor["width"], monitor["height"])

    def get_screen_description(self) -> str:
        """Get basic screen info."""
        w, h = self.get_screen_dimensions()
        return f"Screen resolution: {w}x{h}"

    def screenshot_to_bytes(self) -> bytes:
        """Convert last screenshot to bytes for transmission."""
        if self.last_screenshot is None:
            self.capture_screen()

        buffer = io.BytesIO()
        self.last_screenshot.save(buffer, format="PNG")
        return buffer.getvalue()
