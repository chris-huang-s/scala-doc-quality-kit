#!/usr/bin/env python3
"""Flag 3+ consecutive blank lines in markdown outside fenced code blocks."""
from __future__ import annotations

import sys
from pathlib import Path

from doc_quality.markdown import toggle_fence
from doc_quality_config import iter_md_files

ROOT = Path(__file__).resolve().parents[1]
MAX_CONSECUTIVE_BLANK_LINES = 2


def is_blank_line(line: str) -> bool:
    """Return True when the line is empty or whitespace-only."""
    return not line.strip()


def main() -> int:
    bad: list[tuple[Path, int, int]] = []
    checked = 0
    for md in iter_md_files(ROOT):
        lines = md.read_text(encoding="utf-8").splitlines()
        in_fence = False
        blank_run = 0
        run_start = 0
        for i, line in enumerate(lines, start=1):
            was_in_fence = in_fence
            in_fence = toggle_fence(in_fence, line)
            if in_fence or was_in_fence:
                blank_run = 0
                continue
            if is_blank_line(line):
                if blank_run == 0:
                    run_start = i
                blank_run += 1
                checked += 1
                if blank_run == MAX_CONSECUTIVE_BLANK_LINES + 1:
                    bad.append((md, run_start, blank_run))
            else:
                blank_run = 0
                checked += 1

    print(f"checked_content_lines={checked}")
    if bad:
        for md, line_no, count in bad:
            print(
                f"CONSECUTIVE_BLANK_LINES: {md.relative_to(ROOT)}:{line_no} "
                f"({count}+ blank lines)"
            )
        return 1
    print("ok: no runs of 3+ consecutive blank lines outside fences")
    return 0


if __name__ == "__main__":
    sys.exit(main())
