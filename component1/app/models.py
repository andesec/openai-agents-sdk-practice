"""SQLAlchemy models for transcription jobs."""
from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import Column, DateTime, String, Text

from .db import Base


class TranscriptionJob(Base):
    __tablename__ = "transcription_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    original_filename = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="queued")
    transcript = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=dt.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
        nullable=False,
    )

    def mark_processing(self) -> None:
        self.status = "processing"
        self.updated_at = dt.datetime.utcnow()

    def mark_complete(self, transcript: str) -> None:
        self.status = "completed"
        self.transcript = transcript
        self.updated_at = dt.datetime.utcnow()

    def mark_failed(self, error_message: str) -> None:
        self.status = "failed"
        self.error_message = error_message
        self.updated_at = dt.datetime.utcnow()
