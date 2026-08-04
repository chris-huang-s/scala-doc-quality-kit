#!/usr/bin/env python3
"""Require a blank line before ## / ### headings (outside code fences)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADING_RE = re.compile(r"^#{2,6}\s+\S")
FENCE_RE = re.compile(r"^```")


def iter_md_files(root: Path):
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        yield path


def main() -> int:
    bad = []
    checked = 0
    for md in iter_md_files(ROOT):
        lines = md.read_text(encoding="utf-8").splitlines()
        in_fence = False
        for i, line in enumerate(lines):
            if FENCE_RE.match(line.strip()):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if not HEADING_RE.match(line):
                continue
            checked += 1
            if i == 0:
                continue
            prev = lines[i - 1]
            if prev.strip() != "":
                bad.append((md, i + 1, line.strip()))

    print(f"checked_headings={checked}")
    if bad:
        for md, line_no, text in bad:
            print(f"MISSING_BLANK_LINE: {md.relative_to(ROOT)}:{line_no} before {text}")
        return 1
    print("ok: headings are preceded by a blank line")
    return 0


if __name__ == "__main__":
    sys.exit(main())
