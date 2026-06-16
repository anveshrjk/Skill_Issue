"""
client/text_to_speech.py — Text-to-Speech Module

Converts text into spoken audio using pyttsx3 (fully offline).

Why pyttsx3?
  - Works completely offline (no internet needed)
  - Uses native OS speech engines:
      • Windows → SAPI5
      • macOS   → NSSpeechSynthesizer
      • Linux   → espeak
  - Simple API, no external services
  - Reliable for short responses (which is our use-case)
"""

import pyttsx3
import threading


# ──────────────────────────────────────────────
# Engine Setup
# ──────────────────────────────────────────────

# Lock to prevent simultaneous speech (pyttsx3 is not thread-safe)
_tts_lock = threading.Lock()


def _create_engine() -> pyttsx3.Engine:
    """
    Create and configure a fresh TTS engine instance.

    We create a new engine per call because pyttsx3 can behave
    unpredictably when reused across threads. A fresh engine per
    call is cheap and eliminates subtle bugs.

    Configuration:
        - Rate: 160 words/min (slightly slower than default for clarity)
        - Volume: Full (1.0)
    """
    engine = pyttsx3.init()
    engine.setProperty("rate", 160)    # Speaking speed (default ~200)
    engine.setProperty("volume", 1.0)  # Max volume
    return engine


# ──────────────────────────────────────────────
# Core TTS Function
# ──────────────────────────────────────────────

def speak(text: str) -> None:
    """
    Speak the given text aloud through the system speakers.

    This function is thread-safe — concurrent calls will queue up
    thanks to the lock. Each call creates a fresh engine to avoid
    cross-thread issues with pyttsx3.

    Args:
        text: The string to speak. Empty strings are silently ignored.

    Flow:
        1. Acquire lock (ensures only one speech at a time)
        2. Create a fresh pyttsx3 engine
        3. Queue the text for speaking
        4. Block until speech completes (runAndWait)
        5. Release lock
    """
    if not text or not text.strip():
        return

    with _tts_lock:
        try:
            engine = _create_engine()
            print(f"[TTS] Speaking: {text[:60]}...")
            engine.say(text)
            engine.runAndWait()
            # NOTE: Do NOT call engine.stop() after runAndWait()
            # on Windows — it causes the engine to hang or silently
            # fail on subsequent calls. This is a known pyttsx3 bug.
            del engine  # Clean up the engine instance
            print("[TTS] Done speaking.")
        except Exception as e:
            print(f"[TTS] Error during speech: {e}")
