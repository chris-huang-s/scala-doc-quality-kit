"""Path walking helpers for markdown doc quality scans."""
from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Iterator

from doc_quality.config import load_config


def _is_ignored(rel_posix: str, ignore_globs: list[str]) -> bool:
    """Return True when rel_posix matches any configured ignore glob."""
    if not ignore_globs:
        return False
    name = Path(rel_posix).name
    for pattern in ignore_globs:
        if fnmatch.fnmatch(rel_posix, pattern) or fnmatch.fnmatch(name, pattern):
            return True
    return False


def iter_md_files(root: Path, scan_paths: list[str] | None = None) -> Iterator[Path]:
    """Yield markdown files under configured paths, skipping .git and ignore_globs."""
    cfg = load_config(root) if scan_paths is None else None
    if scan_paths is None:
        assert cfg is not None
        scan_paths = cfg["paths"]
    ignore_globs = list((cfg or load_config(root)).get("ignore_globs") or [])

    root_resolved = root.resolve()
    seen: set[Path] = set()
    for rel in scan_paths:
        base = (root / rel).resolve()
        try:
            base.relative_to(root_resolved)
        except ValueError:
            continue

        if base.is_file() and base.suffix == ".md":
            rel_posix = base.relative_to(root_resolved).as_posix()
            if _is_ignored(rel_posix, ignore_globs):
                continue
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
            rel_posix = resolved.relative_to(root_resolved).as_posix()
            if _is_ignored(rel_posix, ignore_globs):
                continue
            if resolved not in seen:
                seen.add(resolved)
                yield resolved
