"""Backend application for the transcription web experience."""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import Settings, get_settings
from .schemas import FrontendConfigResponse, SummaryRequest, SummaryResponse
from ..clients.gemini import GeminiClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Transcription Web Backend", version="0.1.0")


@lru_cache()
def _build_gemini_client(api_key: str | None, model_name: str) -> GeminiClient:
    return GeminiClient(api_key=api_key, model_name=model_name)


def get_gemini_client(settings: Settings = Depends(get_settings)) -> GeminiClient:
    return _build_gemini_client(settings.gemini_api_key, settings.gemini_model)


@app.on_event("startup")
async def configure_app() -> None:
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(
        "Web backend started. Component 1 base URL: %s | Poll interval: %ss",
        settings.component1_base_url,
        settings.frontend_poll_interval,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/config.json", response_model=FrontendConfigResponse)
async def frontend_config(settings: Settings = Depends(get_settings)) -> FrontendConfigResponse:
    return FrontendConfigResponse(
        component1_base_url=settings.component1_base_url,
        poll_interval_seconds=settings.frontend_poll_interval,
    )


@app.post("/summaries", response_model=SummaryResponse)
async def create_summary(
    payload: SummaryRequest,
    client: GeminiClient = Depends(get_gemini_client),
) -> SummaryResponse:
    try:
        summary = client.summarise(payload.transcript)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return SummaryResponse(summary=summary)


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    logger.warning("Frontend directory %s does not exist; static files will not be served", FRONTEND_DIR)
