"""Load scan paths and iterate markdown files for doc quality checks."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

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


def iter_md_files(root: Path, scan_paths: list[str] | None = None) -> Iterator[Path]:
    """Yield markdown files under configured paths, skipping .git."""
    if scan_paths is None:
        scan_paths = load_config(root)["paths"]

    seen: set[Path] = set()
    for rel in scan_paths:
        base = (root / rel).resolve()
        try:
            base.relative_to(root.resolve())
        except ValueError:
            continue

        if base.is_file() and base.suffix == ".md":
            if base not in seen:
                seen.add(base)
                yield base
            continue

        if not base.is_dir():
            continue

        for path in base.rglob("*.md"):
            if ".git" in path.parts:
                continue
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield resolved
