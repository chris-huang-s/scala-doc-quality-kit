#!/usr/bin/env python3
"""Flag ATX heading level jumps greater than one (outside code fences)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from doc_quality.markdown import toggle_fence
from doc_quality_config import iter_md_files

ROOT = Path(__file__).resolve().parents[1]
ATX_HEADING_RE = re.compile(r"^(#{1,6})\s+(\S.*)$")


def find_heading_level_skips(text: str) -> list[tuple[int, int, int, str]]:
    """Return (line_no, prev_level, level, title) for ATX jumps greater than 1."""
    skips: list[tuple[int, int, int, str]] = []
    prev_level: int | None = None
    in_fence = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        in_fence = toggle_fence(in_fence, line)
        if in_fence:
            continue
        match = ATX_HEADING_RE.match(line)
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        if prev_level is not None and level - prev_level > 1:
            skips.append((line_no, prev_level, level, title))
        prev_level = level
    return skips


def main() -> int:
    bad: list[tuple[Path, int, int, int, str]] = []
    checked = 0
    for md in iter_md_files(ROOT):
        checked += 1
        text = md.read_text(encoding="utf-8")
        for line_no, prev_level, level, title in find_heading_level_skips(text):
            bad.append((md, line_no, prev_level, level, title))

    print(f"checked_markdown_files={checked}")
    if bad:
        for md, line_no, prev_level, level, title in bad:
            rel = md.relative_to(ROOT)
            print(
                f"HEADING_LEVEL_SKIP: {rel}:{line_no} "
                f"h{prev_level}->h{level} {title!r}"
            )
        return 1
    print("ok: no ATX heading level skips")
    return 0


if __name__ == "__main__":
    sys.exit(main())
