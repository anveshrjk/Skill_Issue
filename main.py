"""
main.py — Entry Point for Skill Issue AI Dictionary Assistant

This file starts both components of the system:
  1. The FastAPI backend server (in a background thread)
  2. The voice assistant client (in the main thread)

Why threading?
  - The backend (FastAPI + Uvicorn) needs to run continuously
  - The client (listener loop) also runs continuously
  - They need to run simultaneously in the same process
  - A background thread for the server is the simplest approach

Architecture:
  ┌────────────────────────────────────┐
  │            main.py                 │
  │                                    │
  │  ┌──────────────┐  ┌───────────┐  │
  │  │  Backend      │  │  Client   │  │
  │  │  (FastAPI)    │  │  (Voice)  │  │
  │  │  Thread: bg   │  │  Thread:  │  │
  │  │  Port: 8000   │  │   main    │  │
  │  └──────┬───────┘  └─────┬─────┘  │
  │         │                │         │
  │         └──── HTTP ──────┘         │
  └────────────────────────────────────┘
           │
           ▼
     ┌──────────┐
     │  Ollama  │  (external, port 11434)
     │  (phi3)  │
     └──────────┘

Usage:
    python main.py

Prerequisites:
    1. Install dependencies: pip install -r requirements.txt
    2. Install & start Ollama: ollama serve
    3. Pull the model: ollama pull phi3
"""

import threading
import time
import uvicorn


def start_backend():
    """
    Start the FastAPI server in a background thread.

    Configuration:
        - Host: 127.0.0.1 (localhost only, not exposed to network)
        - Port: 8000
        - Log level: warning (suppress noisy request logs)

    The server runs in a daemon thread so it automatically
    shuts down when the main program exits (Ctrl+C).
    """
    uvicorn.run(
        "backend.api:app",     # Import path to the FastAPI app
        host="127.0.0.1",
        port=8000,
        log_level="info",      # Show request logs for debugging
    )


def main():
    """
    Application entry point.

    Steps:
        1. Launch the FastAPI backend in a daemon thread
        2. Wait briefly for the server to initialize
        3. Start the voice assistant loop (blocking, runs in main thread)
    """
    print("[Main] Starting Skill Issue AI Dictionary Assistant...\n")

    # ── Step 1: Start backend server in background ──
    server_thread = threading.Thread(target=start_backend, daemon=True)
    server_thread.start()
    print("[Main] Backend server starting on http://127.0.0.1:8000")

    # ── Step 2: Give the server a moment to boot ──
    time.sleep(2)
    print("[Main] Backend ready.\n")

    # ── Step 3: Start the voice assistant (blocks here) ──
    from client.assistant import run_assistant
    run_assistant()


if __name__ == "__main__":
    main()
