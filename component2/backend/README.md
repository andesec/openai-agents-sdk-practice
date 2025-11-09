# Component 2 – Backend Service

This FastAPI service powers the web application experience. It exposes:

- `GET /config.json` – Provides runtime configuration for the browser client (Component 1 base URL and polling interval).
- `POST /summaries` – Accepts a transcription text payload and returns a summary generated via Google Gemini when credentials are supplied. If no API key is configured, a heuristic summary is returned instead.
- `GET /health` – Simple health check endpoint.

The backend also serves the static frontend assets located in `../frontend`.

## Running locally

```bash
cd component2/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8100
```

The application reads configuration from environment variables (they can also be defined in a `.env` file):

| Variable | Description | Default |
| --- | --- | --- |
| `COMPONENT1_BASE_URL` | Base URL of the transcription service (Component 1). | `http://localhost:8000` |
| `FRONTEND_POLL_INTERVAL_SECONDS` | Polling interval used by the frontend for job status checks. | `3.0` |
| `GEMINI_API_KEY` | API key for Google Gemini. If unset, a heuristic summary is returned. | `None` |
| `GEMINI_MODEL` | Gemini model identifier to use for summarisation. | `gemini-pro` |
| `CORS_ALLOW_ORIGINS` | Comma-separated list of allowed origins for CORS. | `*` |

## Gemini integration

Install the `google-generativeai` dependency and set a valid `GEMINI_API_KEY` to enable real summaries. Without the key, the service logs a warning and falls back to a concise heuristic summary so that local development remains convenient.
