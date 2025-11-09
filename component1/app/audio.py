"""Audio utilities for conversion and transcription."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Optional


class AudioProcessingError(RuntimeError):
    """Raised when conversion or transcription fails."""


def convert_to_wav(source_path: Path, output_dir: Optional[Path] = None) -> Path:
    """Convert an audio file to WAV format using ffmpeg."""
    if output_dir is None:
        output_dir = Path(tempfile.gettempdir())
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{source_path.stem}.wav"

    command = [
        "ffmpeg",
        "-y",  # overwrite existing file
        "-i",
        str(source_path),
        str(output_path),
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError as exc:
        raise AudioProcessingError("ffmpeg executable was not found on the system path") from exc
    except subprocess.CalledProcessError as exc:
        raise AudioProcessingError(f"ffmpeg failed: {exc.stderr.decode('utf-8', errors='ignore')}") from exc

    if not output_path.exists():
        raise AudioProcessingError("WAV output file was not created by ffmpeg")

    return output_path


_WHISPER_MODEL = None


def _load_whisper_model(model_size: str = "base"):
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        try:
            import whisper
        except ImportError as exc:
            raise AudioProcessingError(
                "The 'whisper' package is required for transcription. Install openai-whisper."
            ) from exc
        _WHISPER_MODEL = whisper.load_model(model_size)
    return _WHISPER_MODEL


def transcribe_wav(path: Path, model_size: str = "base") -> str:
    """Transcribe a WAV file using OpenAI's Whisper models."""
    model = _load_whisper_model(model_size=model_size)
    try:
        result = model.transcribe(str(path))
    except Exception as exc:  # pragma: no cover - library level exception
        raise AudioProcessingError(f"Whisper transcription failed: {exc}") from exc
    text = result.get("text", "").strip()
    if not text:
        raise AudioProcessingError("Whisper did not return any text")
    return text
