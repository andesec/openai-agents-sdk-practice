# Audio Transcription &amp; Summarisation Platform

This repository hosts two deployable components that work together to convert audio to text, persist the transcription, and deliver summarised insights to end users.

## Components

### Component 1 – Transcription Service
- FastAPI application that accepts audio uploads via REST.
- Converts audio to WAV using `ffmpeg` and transcribes it with an OpenAI Whisper model.
- Persists transcription jobs and results in a relational database.
- Exposes polling endpoints so clients can track asynchronous processing.

Located in [`component1/`](component1/). See its [README](component1/README.md) for setup instructions.

### Component 2 – Web Application
- User-facing single page app for uploading audio files and viewing results.
- Backend FastAPI service that serves the frontend, fetches configuration, and integrates with the Gemini API for summarisation.
- Frontend polls Component 1 for job progress, renders transcriptions, and displays summaries returned by the backend.

Located in [`component2/`](component2/). Refer to the frontend and backend READMEs for detailed guidance.

## Getting started locally

1. Start Component 1 (transcription service) on port `8000`.
2. Start Component 2 backend on port `8100` (serves the frontend at `http://localhost:8100/`).
3. Open the frontend in your browser, upload an audio file, and follow the workflow.

Ensure `ffmpeg` is installed and accessible. Configure `GEMINI_API_KEY` for real summaries or rely on the fallback summariser for local experimentation.
