from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class VoiceConfig:
    enable_tts: bool = False
    continuous_listen: bool = True
    microphone_enabled: bool = False
    keyboard_fallback: bool = False
    sample_rate: int = 16000
    vosk_model_path: str = "models/vosk-model-small-en-us-0.15"
    listen_timeout_seconds: int = 8


class ASRStream:
    """Microphone-first ASR via sounddevice + Vosk (no PyAudio)."""

    def __init__(self, config: VoiceConfig) -> None:
        self.config = config
        self._vosk_model: Optional[object] = None
        self._mic_error: str | None = None
        if self.config.microphone_enabled:
            try:
                from vosk import Model

                model_path = Path(self.config.vosk_model_path)
                if not model_path.exists():
                    self._mic_error = (
                        "Vosk model not found. Download and extract model to "
                        f"{model_path.as_posix()}."
                    )
                else:
                    self._vosk_model = Model(str(model_path))
            except Exception as exc:
                self._vosk_model = None
                self._mic_error = f"Microphone backend unavailable: {exc}"

    def listen_once(self) -> str:
        if self._vosk_model is not None:
            text = self._listen_from_microphone()
            if text:
                return text
        if self.config.keyboard_fallback:
            return input("You: ").strip()
        time.sleep(0.2)
        return ""

    def _listen_from_microphone(self) -> str:
        import sounddevice as sd
        from vosk import KaldiRecognizer

        recognizer = KaldiRecognizer(self._vosk_model, self.config.sample_rate)
        start_time = time.time()
        with sd.RawInputStream(
            samplerate=self.config.sample_rate,
            blocksize=8000,
            dtype="int16",
            channels=1,
        ) as stream:
            while True:
                if time.time() - start_time > self.config.listen_timeout_seconds:
                    return ""
                data, _ = stream.read(4000)
                if recognizer.AcceptWaveform(bytes(data)):
                    raw_result = recognizer.Result()
                    text = json.loads(raw_result).get("text", "").strip()
                    if text:
                        return text

    def microphone_ready(self) -> bool:
        return self._vosk_model is not None

    def microphone_status(self) -> str:
        if self.microphone_ready():
            return "Microphone listening is enabled."
        if self.config.microphone_enabled:
            return self._mic_error or "Microphone requested but unavailable."
        return "Microphone is disabled in config; using keyboard input."


class VAD:
    def is_speech(self, text: str) -> bool:
        return bool(text and text.strip())


class BargeIn:
    INTERRUPT_PHRASES = {"stop", "cancel", "jarvis stop"}

    def interrupted(self, text: str) -> bool:
        return text.lower().strip() in self.INTERRUPT_PHRASES


class TTSEngine:
    def __init__(self, config: VoiceConfig) -> None:
        self.config = config
        self._engine = None
        if self.config.enable_tts:
            try:
                import pyttsx3

                self._engine = pyttsx3.init()
            except Exception:
                self._engine = None

    def speak(self, text: str) -> None:
        print(f"Jarvis: {text}")
        if self._engine is not None:
            self._engine.say(text)
            self._engine.runAndWait()


class ProsodyController:
    def style(self, text: str, mood: str = "calm") -> str:
        if mood == "formal":
            return f"{text}"
        if mood == "urgent":
            return f"Alert: {text}"
        return text

