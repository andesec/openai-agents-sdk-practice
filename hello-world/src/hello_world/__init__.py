"""hello_world package."""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from env_loader import load_env


__all__ = ["main"]


def main() -> None:
    load_env()
    print("Hello from hello-world!")
    print("OPENAI_API_KEY:", os.environ.get("OPENAI_API_KEY"))
    print("GEMINI_API_KEY:", os.environ.get("GEMINI_API_KEY"))
