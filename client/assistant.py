"""
client/assistant.py — Main Orchestrator for the Voice Assistant

This is the brain of the client side. It ties together:
  - Wake word detection  (listener.py)
  - Query capture         (listener.py)
  - Backend communication (HTTP → FastAPI)
  - Text-to-Speech output (text_to_speech.py)

The assistant runs an infinite loop:
  1. IDLE:    Listen for the trigger phrase
  2. ACTIVE:  Capture user's query
  3. PROCESS: Send query to FastAPI backend
  4. SPEAK:   Read the AI response aloud
  5. REPEAT:  Go back to idle

Threading Model:
  - The main assistant loop runs in its own thread (started by main.py)
  - TTS runs synchronously (blocks until speech finishes, which is fine
    because we don't want to listen while speaking)
  - Backend calls are synchronous too (the user is waiting anyway)
"""

import requests
from client.listener import listen_for_wake_word, capture_query
from client.text_to_speech import speak


# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

BACKEND_URL = "http://localhost:8000/ask"  # FastAPI endpoint


# ──────────────────────────────────────────────
# Backend Communication
# ──────────────────────────────────────────────

def get_definition(query: str) -> str:
    """
    Send the query to the FastAPI backend and return the response.

    Args:
        query: The word or phrase to look up.

    Returns:
        str — The AI-generated explanation, or an error message.

    Error handling:
        - ConnectionError  → Backend not running
        - Timeout          → Backend too slow (10s limit)
        - Other exceptions → Generic error message
    """
    try:
        print(f"[Assistant] Sending to backend: {BACKEND_URL}?query={query}")
        response = requests.get(
            BACKEND_URL,
            params={"query": query},
            timeout=120,  # Must be >= Ollama timeout (model loading can be slow)
        )
        response.raise_for_status()
        result = response.text.strip()
        print(f"[Assistant] Backend returned: {result[:80]}")
        return result

    except requests.ConnectionError:
        print("[Assistant] ERROR: Cannot connect to backend!")
        return "Backend is not running. Start the server first."
    except requests.Timeout:
        print("[Assistant] ERROR: Backend timed out (120s)!")
        return "Backend took too long to respond."
    except Exception as e:
        print(f"[Assistant] ERROR: {e}")
        return f"Error contacting backend: {str(e)}"


# ──────────────────────────────────────────────
# Main Assistant Loop
# ──────────────────────────────────────────────

def run_assistant():
    """
    The core assistant loop — runs forever until interrupted.

    State Machine:
        ┌──────────┐     trigger      ┌──────────┐
        │   IDLE   │ ──────────────► │  ACTIVE  │
        │ (listen) │                  │ (capture)│
        └──────────┘                  └────┬─────┘
              ▲                            │ query
              │                            ▼
        ┌─────┴──────┐              ┌──────────┐
        │   SPEAK    │ ◄─────────── │ PROCESS  │
        │  (TTS out) │   response   │ (backend)│
        └────────────┘              └──────────┘
    """
    print("=" * 50)
    print("  Skill Issue — AI Dictionary Assistant")
    print("  Say 'hello hello' to activate!")
    print("  Press Ctrl+C to quit.")
    print("=" * 50)

    # Announce startup
    speak("Skill Issue assistant is ready. Say hello hello to ask a question.")

    while True:
        try:
            # ── PHASE 1: IDLE — Wait for wake word ──
            if listen_for_wake_word():
                print("\n[Assistant] Wake word detected!")
                speak("Yes? What would you like to know?")

                # ── PHASE 2: ACTIVE — Capture the query ──
                query = capture_query()

                if query is None:
                    speak("I didn't catch that. Try again.")
                    continue

                print(f"[Assistant] Looking up: '{query}'")
                speak(f"Looking up {query}")

                # ── PHASE 3: PROCESS — Get AI response ──
                answer = get_definition(query)
                print(f"[Assistant] Answer: {answer}")

                # ── PHASE 4: SPEAK — Read response aloud ──
                speak(answer)

                print("[Assistant] Ready for next question.\n")

        except KeyboardInterrupt:
            print("\n[Assistant] Shutting down. Goodbye!")
            speak("Goodbye!")
            break
        except Exception as e:
            # Catch-all: never crash, just log and continue
            print(f"[Assistant] Error in main loop: {e}")
            continue
