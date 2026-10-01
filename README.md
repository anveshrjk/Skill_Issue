# Skill Issue

### AI-Powered Voice Dictionary Assistant

Skill Issue is a hands-free dictionary assistant designed for quick vocabulary lookup while studying or working. It uses speech recognition to capture a spoken word and a locally hosted Large Language Model (LLM) to generate a concise explanation with an example.

The project combines voice input, local AI inference, and a lightweight desktop interface to provide dictionary-style assistance without requiring constant keyboard or mouse interaction.

## Features

- Voice-based word input using speech recognition
- Concise AI-generated definitions and explanations
- Example-based responses for better understanding
- Local LLM inference using Ollama
- FastAPI backend for handling application requests
- Lightweight desktop interface
- Option to read generated responses aloud
- Designed for minimal user interaction

## How It Works

The application follows a simple pipeline:

**Voice Input → Speech-to-Text → FastAPI Backend → Local LLM → Response → Desktop Interface**

1. The user speaks a word through the microphone.
2. Whisper converts the speech into text.
3. The text is sent to the FastAPI backend.
4. The backend communicates with the locally running LLM through Ollama.
5. The model generates a concise explanation and example.
6. The response is displayed in the desktop interface and can be read aloud.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| FastAPI | Backend and API handling |
| Whisper | Speech-to-text conversion |
| Ollama | Local LLM inference |
| Phi-3 | Language model |
| CustomTkinter | Desktop user interface |
| Uvicorn | FastAPI server |
| Requests | API communication |

## Project Structure

```text
Skill_Issue/
│
├── backend/
│   └── api.py
│
├── main.py
├── requirements.txt
└── README.md

