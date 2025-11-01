import os

from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    print("Hello from hello-world!")
    print("OPENAI_API_KEY:", os.environ.get("OPENAI_API_KEY"))
    print("GEMINI_API_KEY:", os.environ.get("GEMINI_API_KEY"))


if __name__ == "__main__":
    main()
