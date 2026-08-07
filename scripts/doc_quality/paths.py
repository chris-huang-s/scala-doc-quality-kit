"""Path walking helpers for markdown doc quality scans."""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from doc_quality.config import load_config


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
