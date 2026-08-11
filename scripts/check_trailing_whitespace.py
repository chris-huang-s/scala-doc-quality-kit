#!/usr/bin/env python3
"""Flag trailing spaces or tabs on non-blank markdown lines outside fences."""
from __future__ import annotations

import sys
from pathlib import Path

from doc_quality.markdown import toggle_fence
from doc_quality_config import iter_md_files

ROOT = Path(__file__).resolve().parents[1]


def line_has_trailing_whitespace(line: str) -> bool:
    """Return True for non-blank lines that end with space or tab."""
    raw = line.rstrip("\n\r")
    if not raw.strip():
        return False
    return raw != raw.rstrip(" \t")


def main() -> int:
    bad: list[tuple[Path, int]] = []
    checked = 0
    for md in iter_md_files(ROOT):
        lines = md.read_text(encoding="utf-8").splitlines()
        in_fence = False
        for i, line in enumerate(lines, start=1):
            in_fence = toggle_fence(in_fence, line)
            if in_fence:
                continue
            if not line.strip():
                continue
            checked += 1
            if line_has_trailing_whitespace(line):
                bad.append((md, i))

    print(f"checked_content_lines={checked}")
    if bad:
        for md, line_no in bad:
            print(f"TRAILING_WHITESPACE: {md.relative_to(ROOT)}:{line_no}")
        return 1
    print("ok: no trailing whitespace on non-blank markdown lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
