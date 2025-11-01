"""hello_world package."""
import os

from dotenv import load_dotenv


__all__ = ["main"]


def main() -> None:
    load_dotenv()
    print("Hello from hello-world!")
    print("OPENAI_API_KEY:", os.environ.get("OPENAI_API_KEY"))
    print("GEMINI_API_KEY:", os.environ.get("GEMINI_API_KEY"))
