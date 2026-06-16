"""
client/listener.py — Wake Word Listener Module

Continuously listens to the microphone in short chunks, checking
each chunk for the trigger phrase. Once detected, it switches to
"query capture" mode and returns the user's actual question.

Design Decisions:
  - Uses short listening windows (2–3 seconds) for wake word detection
    rather than heavyweight keyword-spotting models like Porcupine.
    This is simpler, dependency-light, and accurate enough for a
    personal assistant.
  - The trigger phrase is configurable (default: "hello hello").
  - After wake word detection, we use a longer listening window
    to capture the full query.
"""

import speech_recognition as sr


# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

TRIGGER_PHRASE = "hello hello"  # The wake word / activation phrase

# Listening parameters
WAKE_TIMEOUT = 2         # Seconds to wait for speech in each wake cycle
WAKE_PHRASE_LIMIT = 4    # Max seconds of speech per wake cycle
QUERY_TIMEOUT = 5        # Seconds to wait for query speech to start
QUERY_PHRASE_LIMIT = 10  # Max seconds to record the query


# ──────────────────────────────────────────────
# Recognizer (shared instance)
# ──────────────────────────────────────────────

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True


# ──────────────────────────────────────────────
# Wake Word Detection
# ──────────────────────────────────────────────

def listen_for_wake_word() -> bool:
    """
    Listen for one short chunk of audio and check if it contains
    the trigger phrase.

    This function is designed to be called in a loop. Each call:
      1. Opens the mic for a brief window
      2. Tries to recognize any speech
      3. Checks if the trigger phrase appears in the text

    Returns:
        True  — if the trigger phrase was detected
        False — if nothing was heard, or the phrase wasn't in the audio

    Why short windows?
      - Keeps CPU usage low (mic isn't held open forever)
      - Gives quick response time (checks every ~2 seconds)
      - Simple and reliable
    """
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(
                source,
                timeout=WAKE_TIMEOUT,
                phrase_time_limit=WAKE_PHRASE_LIMIT,
            )

        # Recognize the short audio chunk
        text = recognizer.recognize_google(audio).lower().strip()
        print(f"[Listener] Heard: '{text}'")

        # Check if trigger phrase is present anywhere in the text
        if TRIGGER_PHRASE in text:
            return True
        return False

    except sr.WaitTimeoutError:
        # Silence — no one spoke. This is normal during idle.
        return False
    except sr.UnknownValueError:
        # Heard something but couldn't make it out
        return False
    except sr.RequestError as e:
        print(f"[Listener] Recognition service error: {e}")
        return False
    except Exception as e:
        print(f"[Listener] Unexpected error: {e}")
        return False


# ──────────────────────────────────────────────
# Query Capture
# ──────────────────────────────────────────────

def capture_query() -> str | None:
    """
    After the wake word is detected, listen for the user's
    actual question with a longer recording window.

    Returns:
        str  — The recognized query text
        None — If nothing was understood

    This gives the user up to QUERY_TIMEOUT seconds to start
    speaking, and records up to QUERY_PHRASE_LIMIT seconds
    of continuous speech.
    """
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("[Listener] Listening for your question...")

            audio = recognizer.listen(
                source,
                timeout=QUERY_TIMEOUT,
                phrase_time_limit=QUERY_PHRASE_LIMIT,
            )

        text = recognizer.recognize_google(audio).lower().strip()
        print(f"[Listener] Query captured: '{text}'")
        return text

    except sr.WaitTimeoutError:
        print("[Listener] No question heard (timed out).")
        return None
    except sr.UnknownValueError:
        print("[Listener] Couldn't understand the question.")
        return None
    except sr.RequestError as e:
        print(f"[Listener] Recognition service error: {e}")
        return None
    except Exception as e:
        print(f"[Listener] Error capturing query: {e}")
        return None
