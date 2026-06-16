"""
client/speech_to_text.py — Speech-to-Text Module

Converts spoken audio from the microphone into text using
Google's free Web Speech API (via the SpeechRecognition library).

Why SpeechRecognition + Google Web API?
  - Zero setup, no API key needed for basic usage
  - Good accuracy for English
  - Works out of the box on Windows/Mac/Linux
  - The free tier is more than enough for a personal assistant

Note: This uses the internet for recognition. For fully offline STT,
you could swap in Vosk or whisper, but that adds heavyweight dependencies.
"""

import speech_recognition as sr


# ──────────────────────────────────────────────
# Recognizer Setup
# ──────────────────────────────────────────────

# Create a single recognizer instance (reused across calls)
recognizer = sr.Recognizer()

# Adjust for ambient noise sensitivity
# energy_threshold auto-calibrates, but we set a sane default
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True  # Adapts to background noise


# ──────────────────────────────────────────────
# Core STT Function
# ──────────────────────────────────────────────

def recognize_speech(timeout: int = 5, phrase_time_limit: int = 8) -> str | None:
    """
    Listen on the default microphone and convert speech to text.

    Args:
        timeout:  Max seconds to wait for speech to START.
                  If nothing is heard in this window, returns None.
        phrase_time_limit:  Max seconds of speech to capture once
                           it starts. Prevents runaway recordings.

    Returns:
        str  — Recognized text (lowercase, stripped)
        None — If nothing was understood or an error occurred

    Flow:
        1. Open microphone
        2. Briefly calibrate for ambient noise (0.5s)
        3. Wait up to `timeout` seconds for speech to begin
        4. Once speech starts, record up to `phrase_time_limit` seconds
        5. Send audio to Google Web Speech API
        6. Return recognized text
    """
    try:
        with sr.Microphone() as source:
            # Quick ambient noise calibration (keeps it snappy)
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            # Listen for audio input
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )

        # Send to Google's free speech recognition API
        text = recognizer.recognize_google(audio)
        return text.lower().strip()

    except sr.WaitTimeoutError:
        # No speech detected within the timeout window
        return None
    except sr.UnknownValueError:
        # Audio was captured but couldn't be understood
        return None
    except sr.RequestError as e:
        # Network issue or API problem
        print(f"[STT] Recognition service error: {e}")
        return None
    except Exception as e:
        # Catch-all to prevent crashes
        print(f"[STT] Unexpected error: {e}")
        return None
