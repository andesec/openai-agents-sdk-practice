# Component 1 – Transcription Service

This service exposes an HTTP API for accepting audio uploads, converting them to WAV using `ffmpeg`, transcribing the audio with an OpenAI Whisper model, and storing the results in a relational database.

## Features

- `POST /transcriptions`: upload an audio file. The endpoint queues a background job that converts the audio to WAV and transcribes it using Whisper. The response immediately returns a `job_id` that can be polled.
- `GET /transcriptions/{job_id}`: retrieve the current state of a job (`queued`, `processing`, `completed`, `failed`) together with the transcription or error details once available.
- `GET /health`: lightweight health-check endpoint.

## Running locally

1. Install system dependencies:
   - Python 3.11+
   - `ffmpeg` binary available on the system `PATH`.

2. Create a virtual environment and install dependencies:

   ```bash
   cd component1
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

   > **Note:** The official Whisper package requires PyTorch. Install a compatible version of `torch` for your platform if it is not pulled in automatically.

3. Start the API server:

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. Upload an audio file for transcription using `curl`:

   ```bash
   curl -F "file=@sample.mp3" http://localhost:8000/transcriptions
   ```

5. Poll for the result until the status becomes `completed`:

   ```bash
   curl http://localhost:8000/transcriptions/<job_id>
   ```

## Configuration

Environment variables supported by the service:

| Variable | Description | Default |
| --- | --- | --- |
| `WHISPER_MODEL_SIZE` | Whisper model size (e.g. `tiny`, `base`, `small`). | `base` |
| `CORS_ALLOW_ORIGINS` | Comma-separated origins allowed for cross-origin requests. | `*` |
| `TRANSCRIPTION_DATABASE_URL` | SQLAlchemy database URL. | `sqlite:///./transcriptions.db` |

## Database

By default the service stores data in a local SQLite database file named `transcriptions.db`. Switching to PostgreSQL or another RDBMS simply requires updating the `TRANSCRIPTION_DATABASE_URL` environment variable.
