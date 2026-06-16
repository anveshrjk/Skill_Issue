"""
backend/api.py — FastAPI Backend for Skill Issue Dictionary Assistant

This module provides a single REST endpoint (/ask) that:
  1. Receives a user query (a word or phrase to define)
  2. Builds a carefully constrained prompt
  3. Sends it to a locally-running Ollama instance (phi3 model)
  4. Returns the AI-generated explanation as plain text

Why FastAPI?
  - Lightweight, fast, async-capable
  - Auto-generates docs at /docs for easy testing
  - Clean separation between client logic and AI processing
"""

import requests
from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse

# ──────────────────────────────────────────────
# App Initialization
# ──────────────────────────────────────────────

app = FastAPI(
    title="Skill Issue – AI Dictionary Backend",
    description="Hands-free dictionary assistant powered by Ollama + phi3",
    version="1.0.0",
)

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

OLLAMA_URL = "http://localhost:11434/api/generate"  # Default Ollama endpoint
MODEL_NAME = "tinyllama"                              # Lightweight local LLM (phi3 alternative)

# ──────────────────────────────────────────────
# Prompt Builder
# ──────────────────────────────────────────────

def build_prompt(term: str) -> str:
    """
    Construct a tightly-constrained prompt so the LLM returns
    short, clear, viva-friendly answers every time.

    The prompt explicitly asks for:
      - 1–3 lines only
      - Simple language
      - One short example
      - Slang handling
      - A fallback phrase if unsure
    """
    return (
        "Explain the following term in 1-3 short lines in simple language. "
        "Include one short example. "
        "If it is slang, explain the slang meaning. "
        "If unsure, reply exactly: Meaning not known.\n\n"
        f"Term: {term}"
    )

# ──────────────────────────────────────────────
# Ollama Communication
# ──────────────────────────────────────────────

def query_ollama(prompt: str) -> str:
    """
    Send the prompt to the local Ollama server and collect the
    full streamed response.

    Ollama streams JSON objects line-by-line.  We set stream=False
    so the server concatenates the full answer into one response,
    which is simpler and fast enough for our use-case.

    Returns:
        str — The model's generated text, or an error message.
    """
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,       # Get complete response at once
            "options": {
                "temperature": 0.3,  # Low temp → deterministic, concise answers
                "num_predict": 150,  # Hard cap on token count to keep it short
            },
        }

        print(f"[Backend] Sending prompt to Ollama ({MODEL_NAME})...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        answer = data.get("response", "Meaning not known.").strip()
        print(f"[Backend] Got response: {answer[:80]}...")
        return answer

    except requests.ConnectionError:
        # Ollama service is not running
        print("[Backend] ERROR: Cannot connect to Ollama!")
        return "AI not available. Make sure Ollama is running (ollama serve)."
    except requests.Timeout:
        print("[Backend] ERROR: Ollama timed out (120s)!")
        return "AI took too long to respond. Try again."
    except Exception as e:
        print(f"[Backend] ERROR: {e}")
        return f"Error communicating with AI: {str(e)}"

# ──────────────────────────────────────────────
# API Endpoint
# ──────────────────────────────────────────────

@app.get("/ask", response_class=PlainTextResponse)
def ask(query: str = Query(..., description="The word or phrase to look up")):
    """
    Main endpoint — receives a term, gets an AI explanation.

    Usage:
        GET /ask?query=recursion
        GET /ask?query=bruh

    Returns:
        Plain-text explanation (1–3 lines + example).
    """
    # Guard: reject empty queries
    if not query.strip():
        return "No query provided."

    print(f"[Backend] Received query: '{query}'")

    # Build the constrained prompt and call the LLM
    prompt = build_prompt(query.strip())
    answer = query_ollama(prompt)

    print(f"[Backend] Returning answer ({len(answer)} chars)")
    return answer


# ──────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────

@app.get("/health")
def health():
    """Simple health-check so the client can verify the backend is up."""
    return {"status": "ok", "model": MODEL_NAME}
