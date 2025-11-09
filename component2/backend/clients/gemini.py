"""Client utilities for interacting with the Gemini API."""
from __future__ import annotations

import logging
from textwrap import shorten

logger = logging.getLogger(__name__)


class GeminiClient:
    """Lightweight wrapper around Google Gemini models with graceful fallbacks."""

    def __init__(self, api_key: str | None, model_name: str) -> None:
        self.api_key = api_key
        self.model_name = model_name

    def summarise(self, transcript: str) -> str:
        cleaned = transcript.strip()
        if not cleaned:
            raise ValueError("Transcript must contain text to summarise")

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured; returning fallback summary")
            return self._fallback_summary(cleaned)

        try:
            import google.generativeai as genai
        except ImportError:
            logger.warning("google-generativeai package not installed; returning fallback summary")
            return self._fallback_summary(cleaned)

        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            prompt = (
                "Summarise the following transcription in clear, concise language suitable for end users.\n\n"
                f"Transcription:\n{cleaned}"
            )
            response = model.generate_content(prompt)
        except Exception as exc:  # pragma: no cover - network layer
            logger.exception("Gemini API call failed: %s", exc)
            return self._fallback_summary(cleaned)

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        try:
            # Some SDK versions return a list of candidates instead of a `text` attribute.
            for candidate in getattr(response, "candidates", []):
                parts = getattr(candidate, "content", {}).get("parts") if hasattr(candidate, "content") else None
                if not parts:
                    continue
                text_fragments = [getattr(part, "text", "") for part in parts]
                cleaned_output = "\n".join(fragment for fragment in text_fragments if fragment)
                if cleaned_output:
                    return cleaned_output.strip()
        except Exception:  # pragma: no cover - defensive branch
            pass

        logger.warning("Gemini API returned an unexpected payload; falling back to heuristic summary")
        return self._fallback_summary(cleaned)

    @staticmethod
    def _fallback_summary(text: str) -> str:
        snippet = shorten(text, width=280, placeholder="...")
        return f"(Heuristic summary) {snippet}"
