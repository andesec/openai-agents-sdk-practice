# Component 2 – Frontend

A minimalist single-page application that allows users to:

1. Upload an audio file.
2. Poll the transcription service (Component 1) for job completion.
3. Display the transcription once available.
4. Request a summary from the backend service and render it for the user.

The frontend is served by the backend service in `../backend`. During development you can also open `index.html` directly in the browser, but API calls must point to running backend and transcription services with permissive CORS settings.
