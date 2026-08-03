#!/usr/bin/env python3
"""Require exactly one top-level (# ) heading per Markdown file."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
H1_RE = re.compile(r"^#\s+\S")
FENCE_RE = re.compile(r"^```")


def iter_md_files(root: Path):
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        yield path


def count_h1(text: str) -> int:
    count = 0
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if H1_RE.match(line):
            count += 1
    return count


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
