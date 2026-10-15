from jarvis.listener import listen, adjust_for_ambient_noise
from jarvis.brain import think
from jarvis.speaker import speak
from jarvis.config import JARVIS_NAME, VISION_SCAN_MARKER
from jarvis.memory import get_client
from jarvis.commands.vision import full_scan


def verify_supabase():
    try:
        db = get_client()
        db.table("conversations").select("id").limit(1).execute()
        print("[OK] Connected to Supabase")
        return True
    except Exception as e:
        print(f"[WARN] Supabase connection failed: {e}")
        print("      Marco will run without memory. Check your .env credentials.")
        return False


def main():
    print("=" * 50)
    print(f"  {JARVIS_NAME} - AI Voice Assistant")
    print("  Say 'exit' or 'quit' to stop")
    print("=" * 50)

    supabase_ok = verify_supabase()

    adjust_for_ambient_noise()

    speak(f"Good day, sir. {JARVIS_NAME} is online and ready.")

    while True:
        text = listen()
        if text is None:
            continue

        lower = text.lower().strip()
        if lower in ("exit", "quit", "stop", "shutdown"):
            speak("Shutting down. Goodbye, sir.")
            break

        if any(greet in lower for greet in ("hello", "hi", "hey")):
            speak(f"Hello, sir. How may I assist you today?")
            continue

        reply = think(text)

        if reply.strip() == VISION_SCAN_MARKER:
            speak("Activating visual scan, sir.")
            description, detections = full_scan()
            labels = [d["label"] for d in detections]
            if labels:
                speak(f"I can see {', '.join(set(labels))}.")
            speak(description)
        else:
            speak(reply)


if __name__ == "__main__":
    main()
