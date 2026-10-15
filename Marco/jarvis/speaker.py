import pyttsx3
from .config import VOICE_RATE, VOICE_INDEX


engine = pyttsx3.init()


def configure():
    voices = engine.getProperty("voices")
    if VOICE_INDEX < len(voices):
        engine.setProperty("voice", voices[VOICE_INDEX].id)
    engine.setProperty("rate", VOICE_RATE)


def speak(text: str):
    print(f"Marco: {text}")
    engine.say(text)
    engine.runAndWait()


configure()
