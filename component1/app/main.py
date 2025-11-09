"""FastAPI application that exposes transcription capabilities."""
from __future__ import annotations

import logging
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import List

from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseSettings, Field
from sqlalchemy.orm import Session

from . import audio
from .db import Base, engine, get_session, session_scope
from .models import TranscriptionJob
from .schemas import CreateTranscriptionResponse, HealthResponse, TranscriptionJobResponse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Settings(BaseSettings):
    """Runtime configuration for the service."""

    whisper_model_size: str = Field("base", env="WHISPER_MODEL_SIZE")
    cors_allow_origins: str | None = Field(None, env="CORS_ALLOW_ORIGINS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def allowed_origins(self) -> List[str]:
        if not self.cors_allow_origins:
            return ["*"]
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def init_database() -> None:
    Base.metadata.create_all(bind=engine)


def process_transcription_job(job_id: str, source_path: Path, model_size: str) -> None:
    """Background task that converts and transcribes the audio file."""
    wav_path: Path | None = None
    try:
        with session_scope() as session:
            job = session.get(TranscriptionJob, job_id)
            if job is None:
                logger.error("Unable to find job %s during background processing", job_id)
                return
            job.mark_processing()

        wav_path = audio.convert_to_wav(source_path)
        transcript = audio.transcribe_wav(wav_path, model_size=model_size)

        with session_scope() as session:
            job = session.get(TranscriptionJob, job_id)
            if job is None:
                logger.error("Unable to find job %s to store the transcription", job_id)
                return
            job.mark_complete(transcript)
            logger.info("Job %s completed", job_id)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Job %s failed: %s", job_id, exc)
        with session_scope() as session:
            job = session.get(TranscriptionJob, job_id)
            if job is not None:
                job.mark_failed(str(exc))
    finally:
        source_path.unlink(missing_ok=True)
        if wav_path and wav_path.exists():
            wav_path.unlink()


app = FastAPI(title="Transcription Service", version="0.1.0")


@app.on_event("startup")
async def on_startup() -> None:
    init_database()
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("Transcription service started with Whisper model '%s'", settings.whisper_model_size)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/transcriptions", response_model=CreateTranscriptionResponse, status_code=202)
async def create_transcription(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CreateTranscriptionResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")

    suffix = Path(file.filename).suffix or ".tmp"
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            while chunk := await file.read(1024 * 1024):
                temp_file.write(chunk)
        temp_path = Path(temp_file.name)
    finally:
        await file.close()

    job = TranscriptionJob(original_filename=file.filename, status="queued")
    session.add(job)
    session.flush()  # ensures job.id is available

    background_tasks.add_task(
        process_transcription_job,
        job.id,
        temp_path,
        settings.whisper_model_size,
    )

    logger.info("Queued transcription job %s for '%s'", job.id, file.filename)
    return CreateTranscriptionResponse(job_id=job.id, status=job.status)


@app.get("/transcriptions/{job_id}", response_model=TranscriptionJobResponse)
async def get_transcription(job_id: str, session: Session = Depends(get_session)) -> TranscriptionJobResponse:
    job = session.get(TranscriptionJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Transcription job not found")

    return TranscriptionJobResponse(
        job_id=job.id,
        status=job.status,  # type: ignore[arg-type]
        original_filename=job.original_filename,
        created_at=job.created_at,
        updated_at=job.updated_at,
        transcript=job.transcript,
        error_message=job.error_message,
    )
