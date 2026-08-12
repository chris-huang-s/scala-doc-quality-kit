#!/usr/bin/env python3
"""Flag duplicate heading slugs in a markdown file (outside code fences)."""
from __future__ import annotations

import sys
from pathlib import Path

from doc_quality.markdown import HEADING_TEXT_RE, heading_slug, toggle_fence
from doc_quality_config import iter_md_files

ROOT = Path(__file__).resolve().parents[1]


def find_duplicate_headings(text: str) -> list[tuple[int, str, str]]:
    """Return (line_no, title, slug) for headings that reuse a prior slug."""
    seen: dict[str, int] = {}
    duplicates: list[tuple[int, str, str]] = []
    in_fence = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        in_fence = toggle_fence(in_fence, line)
        if in_fence:
            continue
        match = HEADING_TEXT_RE.match(line)
        if not match:
            continue
        title = match.group(1)
        slug = heading_slug(title)
        if not slug:
            continue
        if slug in seen:
            duplicates.append((line_no, title, slug))
        else:
            seen[slug] = line_no
    return duplicates


def main() -> int:
    bad: list[tuple[Path, int, str, str]] = []
    checked = 0
    for md in iter_md_files(ROOT):
        checked += 1
        text = md.read_text(encoding="utf-8")
        for line_no, title, slug in find_duplicate_headings(text):
            bad.append((md, line_no, title, slug))

    print(f"checked_markdown_files={checked}")
    if bad:
        for md, line_no, title, slug in bad:
            rel = md.relative_to(ROOT)
            print(f"DUPLICATE_HEADING: {rel}:{line_no} {title!r} slug={slug}")
        return 1
    print("ok: no duplicate heading slugs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
