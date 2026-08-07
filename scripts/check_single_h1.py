#!/usr/bin/env python3
"""Require exactly one top-level (# ) heading per Markdown file."""
from __future__ import annotations

import sys
from pathlib import Path

from doc_quality.markdown import count_h1
from doc_quality_config import iter_md_files

ROOT = Path(__file__).resolve().parents[1]

__all__ = ["count_h1", "main"]


def main() -> int:
    bad = []
    checked = 0
    for md in iter_md_files(ROOT):
        checked += 1
        n = count_h1(md.read_text(encoding="utf-8"))
        if n != 1:
            bad.append((md, n))

    print(f"checked_markdown_files={checked}")
    if bad:
        for md, n in bad:
            print(f"BAD_H1_COUNT: {md.relative_to(ROOT)} has {n} top-level headings (want 1)")
        return 1
    print("ok: each markdown file has exactly one H1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
