"""Configuration helpers for the component 2 backend."""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    component1_base_url: str = Field("http://localhost:8000", env="COMPONENT1_BASE_URL")
    frontend_poll_interval: float = Field(3.0, env="FRONTEND_POLL_INTERVAL_SECONDS")
    gemini_api_key: str | None = Field(default=None, env="GEMINI_API_KEY")
    gemini_model: str = Field("gemini-pro", env="GEMINI_MODEL")
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
