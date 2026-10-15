import speech_recognition as sr


recognizer = sr.Recognizer()
microphone = sr.Microphone()


def adjust_for_ambient_noise():
    with microphone as source:
        print("Calibrating microphone for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Calibration complete.")


def listen(timeout: int = 7, phrase_limit: int = 10) -> str | None:
    print("Listening...")
    try:
        with microphone as source:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
    except sr.WaitTimeoutError:
        return None

    print("Recognizing speech...")
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition error: {e}")
        return None
