"""Pydantic schemas for the web application backend."""
from __future__ import annotations

from pydantic import BaseModel, Field


class SummaryRequest(BaseModel):
    transcript: str = Field(..., min_length=1, description="Transcribed text to summarise")


class SummaryResponse(BaseModel):
    summary: str = Field(..., description="Summary generated from the transcription")


class FrontendConfigResponse(BaseModel):
    component1_base_url: str
    poll_interval_seconds: float
