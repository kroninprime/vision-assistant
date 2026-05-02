"""Continuous wake word detection ("Hey Jarvis")."""
import logging
import threading
from typing import Callable, Optional

import speech_recognition as sr

logger = logging.getLogger("jarvis.wake_word")


class WakeWordListener:
    """
    Listens continuously for wake word "Hey Jarvis".
    Triggers callback when detected.
    """

    def __init__(
        self,
        wake_words: list[str] = None,
        callback: Optional[Callable[[], None]] = None,
        confidence_threshold: float = 0.7,
    ):
        self.wake_words = wake_words or ["hey jarvis", "jarvis"]
        self.callback = callback
        self.confidence_threshold = confidence_threshold
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start listening for wake word in background thread."""
        if self.running:
            logger.warning("Wake word listener already running")
            return

        try:
            self.microphone = sr.Microphone()
        except Exception as exc:
            logger.warning(f"Wake word microphone unavailable: {exc}")
            return

        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        logger.info("Wake word listener started (listening for: %s)", ", ".join(self.wake_words))

    def stop(self) -> None:
        """Stop listening for wake word."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Wake word listener stopped")

    def _listen_loop(self) -> None:
        """Main listening loop - runs in background thread."""
        if self.microphone is None:
            logger.warning("Wake word listener cannot start because microphone is unavailable")
            self.running = False
            return

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

        while self.running:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)

                # Try to recognize speech
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    logger.debug(f"Wake word listener heard: {text}")

                    # Check if wake word detected
                    if any(wake in text for wake in self.wake_words):
                        logger.info("✨ Wake word detected: %s", text)
                        if self.callback:
                            self.callback()

                except sr.UnknownValueError:
                    pass  # Couldn't understand, continue listening
                except sr.RequestError as e:
                    logger.warning(f"Wake word recognition error: {e}")

            except sr.RequestError:
                pass  # Timeout, continue
            except Exception as e:
                logger.error(f"Wake word listener error: {e}", exc_info=True)
                # Don't crash - keep listening

    def is_listening(self) -> bool:
        """Check if listener is active."""
        return self.running
