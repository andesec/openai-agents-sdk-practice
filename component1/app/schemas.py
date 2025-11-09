"""Pydantic schemas for the transcription API."""
from __future__ import annotations

import datetime as dt
from typing import Literal, Optional

from pydantic import BaseModel, Field

TranscriptionStatusLiteral = Literal["queued", "processing", "completed", "failed"]


class TranscriptionJobResponse(BaseModel):
    job_id: str = Field(..., description="Identifier of the transcription job")
    status: TranscriptionStatusLiteral
    original_filename: str
    created_at: dt.datetime
    updated_at: dt.datetime
    transcript: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        orm_mode = True


class CreateTranscriptionResponse(BaseModel):
    job_id: str
    status: TranscriptionStatusLiteral


class HealthResponse(BaseModel):
    status: str
