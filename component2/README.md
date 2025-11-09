# Component 2 – Web Application

Component 2 bundles the browser frontend and backend service that interacts with the transcription API (Component 1).

- `frontend/` contains a lightweight HTML/CSS/JavaScript experience. Users can upload audio files, track job progress, and view the final transcription and summary.
- `backend/` is a FastAPI application that serves the frontend assets, proxies configuration to the browser, and integrates with the Gemini API for summarisation.

See the dedicated READMEs inside `frontend/` and `backend/` for setup instructions.
