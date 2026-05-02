"""
Clap-to-wake voice loop for the Jarvis assistant.

How it works:
1) Listens to mic audio; a loud spike (clap) wakes the assistant.
2) Records speech, sends text to the local FastAPI `/command` endpoint.
3) Speaks the reply via pyttsx3.
4) If the user says "shut down", the loop exits.

Dependencies (in requirements.txt): sounddevice, numpy, speechrecognition, pyttsx3, requests.
"""

import queue
import sys
import threading
import time
from typing import Optional

import numpy as np
import requests
import sounddevice as sd
import speech_recognition as sr
import pyttsx3
import keyboard  # for push-to-talk fallback

API_URL = "http://127.0.0.1:8000/command"
SAMPLE_RATE = 16_000
BLOCK_SECONDS = 0.3           # chunk size for clap detection
CLAP_ENERGY_MULTIPLIER = 5.0   # lower threshold so claps trigger more easily
ROLLING_WINDOW = 20            # blocks to average for baseline

r = sr.Recognizer()
t_tts = pyttsx3.init()


def speak(text: str) -> None:
    t_tts.say(text)
    t_tts.runAndWait()


class ClapDetector:
    """Simple energy-based clap detector."""

    def __init__(self) -> None:
        self.recent_energy: queue.SimpleQueue[float] = queue.SimpleQueue()
        self.energy_list: list[float] = []

    def heard_clap(self, samples: np.ndarray) -> bool:
        energy = float(np.sqrt(np.mean(samples**2)) + 1e-9)
        self.energy_list.append(energy)
        if len(self.energy_list) > ROLLING_WINDOW:
            self.energy_list.pop(0)
        baseline = np.mean(self.energy_list) if self.energy_list else energy
        return energy > baseline * CLAP_ENERGY_MULTIPLIER and energy > 0.05


def listen_for_command(detector: ClapDetector) -> Optional[str]:
    """Blocks until a clap or hotkey (Right Ctrl) is heard, then records speech and returns text."""
    with sd.InputStream(channels=1, samplerate=SAMPLE_RATE, blocksize=int(SAMPLE_RATE * BLOCK_SECONDS)) as stream:
        while True:
            frames, _ = stream.read(stream.blocksize)
            samples = frames.flatten().astype(np.float32)
            triggered = detector.heard_clap(samples) or keyboard.is_pressed("right ctrl")
            if triggered:
                speak("Welcome back, boss. What can I do?")
                # record up to 8 seconds of speech
                duration = 8
                recorded = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32")
                sd.wait()
                audio_bytes = (recorded.flatten() * 32767).astype(np.int16).tobytes()
                audio = sr.AudioData(audio_bytes, SAMPLE_RATE, 2)
                try:
                    text = r.recognize_google(audio)
                    return text
                except Exception:
                    speak("Sorry, I didn't catch that.")
                    return None


def main() -> None:
    detector = ClapDetector()
    speak("Jarvis voice loop armed. Clap to wake me.")
    while True:
        command = listen_for_command(detector)
        if not command:
            continue
        lower = command.lower()
        if "shut down" in lower or "shutdown" in lower or "shut off" in lower:
            speak("Shutting down. Goodbye.")
            break
        try:
            resp = requests.post(API_URL, json={"text": command}, timeout=10)
            resp.raise_for_status()
            reply = resp.json().get("reply", "No reply.")
        except Exception:
            reply = "I could not reach my server."
        speak(reply)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
