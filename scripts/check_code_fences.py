#!/usr/bin/env python3
"""Require language tags on Markdown fenced code blocks."""
from __future__ import annotations

import sys
from pathlib import Path

from doc_quality.markdown import parse_fence_line
from doc_quality_config import iter_md_files

ROOT = Path(__file__).resolve().parents[1]

__all__ = ["main", "parse_fence_line"]


def main() -> int:
    unlabeled = []
    fences = 0
    for md in iter_md_files(ROOT):
        lines = md.read_text(encoding="utf-8").splitlines()
        in_fence = False
        for i, line in enumerate(lines, start=1):
            is_fence, lang = parse_fence_line(line)
            if not is_fence:
                continue
            if not in_fence:
                fences += 1
                in_fence = True
                if not lang:
                    unlabeled.append((md, i))
            else:
                in_fence = False

    print(f"checked_fences={fences}")
    if unlabeled:
        for md, line_no in unlabeled:
            print(f"UNLABELED_FENCE: {md.relative_to(ROOT)}:{line_no}")
        return 1
    print("ok: all fenced code blocks have a language tag")
    return 0


if __name__ == "__main__":
    sys.exit(main())
