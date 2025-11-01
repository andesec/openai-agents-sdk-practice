"""Simple helper to load environment variables from a .env file."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict


def load_env(dotenv_path: str | os.PathLike[str] = ".env") -> Dict[str, str]:
    """Load variables from ``dotenv_path`` into ``os.environ`` and return them."""
    path = Path(dotenv_path)
    if not path.exists():
        return {}

    loaded: Dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        os.environ[key] = value
        loaded[key] = value
    return loaded
