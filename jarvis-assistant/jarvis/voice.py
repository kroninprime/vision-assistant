"""
Voice pipeline stubs:
- wake word (not implemented)
- STT via speech_recognition (Google) as fallback
- TTS via pyttsx3
"""

import speech_recognition as sr
import pyttsx3

tts_engine = pyttsx3.init()
r = sr.Recognizer()


def speak(text: str) -> None:
    tts_engine.say(text)
    tts_engine.runAndWait()


def transcribe_once(timeout: int = 5, phrase_time_limit: int = 8) -> str:
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.3)
        audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    return r.recognize_google(audio)
