#!/usr/bin/env python3
"""Flag hard tab characters in markdown outside fenced code blocks."""
from __future__ import annotations

import sys
from pathlib import Path

from doc_quality.markdown import toggle_fence
from doc_quality_config import iter_md_files

ROOT = Path(__file__).resolve().parents[1]


def line_has_hard_tab(line: str) -> bool:
    """Return True when the line contains a tab outside newline characters."""
    return "\t" in line.rstrip("\n\r")


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
            checked += 1
            if line_has_hard_tab(line):
                bad.append((md, i))

    print(f"checked_content_lines={checked}")
    if bad:
        for md, line_no in bad:
            print(f"HARD_TAB: {md.relative_to(ROOT)}:{line_no}")
        return 1
    print("ok: no hard tabs outside fenced code")
    return 0


if __name__ == "__main__":
    sys.exit(main())
