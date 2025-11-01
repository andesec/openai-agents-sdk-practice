"""hello_world package."""
import os

from dotenv import load_dotenv


__all__ = ["main"]


def main() -> None:
    load_dotenv()
    print("Hello from hello-world!")
