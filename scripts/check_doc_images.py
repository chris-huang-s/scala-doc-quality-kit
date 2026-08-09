#!/usr/bin/env python3
"""Scan Markdown files for local image paths and report missing files."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from doc_quality.markdown import toggle_fence
from doc_quality_config import iter_md_files

ROOT = Path(__file__).resolve().parents[1]
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def strip_code(text: str) -> str:
    """Ignore images that only appear inside code fences or inline code."""
    lines = text.splitlines(keepends=True)
    out = []
    in_fence = False
    for line in lines:
        in_fence = toggle_fence(in_fence, line)
        if in_fence:
            out.append("\n" if line.endswith("\n") else "")
            continue
        out.append(INLINE_CODE_RE.sub("", line))
    return "".join(out)


def is_local_image(target: str) -> bool:
    """Return True when the image target should be resolved as a local path."""
    t = target.strip()
    if t.startswith("data:"):
        return False
    if t.startswith("http://") or t.startswith("https://"):
        return False
    if "://" in t:
        return False
    return True


def resolve_image_path(source: Path, path_part: str) -> Path:
    """Resolve a relative image path against the source markdown file."""
    return (source.parent / path_part).resolve()


def main() -> int:
    missing = []
    checked = 0
    for md in iter_md_files(ROOT):
        text = strip_code(md.read_text(encoding="utf-8"))
        for _alt, target in IMAGE_RE.findall(text):
            href = target.strip().split()[0].strip('"')
            if not is_local_image(href):
                continue
            checked += 1
            # Strip optional title / fragment noise already handled by split()[0]
            path_part = href.split("#", 1)[0]
            if not path_part:
                missing.append((md, href, "empty path"))
                continue
            resolved = resolve_image_path(md, path_part)
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                missing.append((md, href, "outside repo"))
                continue
            if not resolved.exists():
                missing.append((md, href, "missing"))

    print(f"checked_local_images={checked}")
    if missing:
        for md, href, reason in missing:
            print(f"MISSING ({reason}): {md.relative_to(ROOT)} -> {href}")
        return 1
    print("ok: no missing local markdown images")
    return 0


if __name__ == "__main__":
    sys.exit(main())
