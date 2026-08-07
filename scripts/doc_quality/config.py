"""Configuration loading for doc quality checks."""
from __future__ import annotations

import json
from pathlib import Path

CONFIG_NAME = ".doc-quality.json"
DEFAULT_PATHS = ["."]


def load_config(root: Path) -> dict:
    """Read .doc-quality.json or return defaults that scan the whole repo."""
    config_path = root / CONFIG_NAME
    if not config_path.is_file():
        return {"paths": list(DEFAULT_PATHS)}
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"paths": list(DEFAULT_PATHS)}
    paths = data.get("paths", DEFAULT_PATHS)
    if not isinstance(paths, list) or not paths:
        return {"paths": list(DEFAULT_PATHS)}
    cleaned = [p for p in paths if isinstance(p, str) and p.strip()]
    if not cleaned:
        return {"paths": list(DEFAULT_PATHS)}
    return {"paths": cleaned}
