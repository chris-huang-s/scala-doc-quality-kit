#!/usr/bin/env python3
"""Require a blank line before ## / ### headings (outside code fences)."""
from __future__ import annotations

import sys
from pathlib import Path

from doc_quality.markdown import HEADING_RE, toggle_fence
from doc_quality_config import iter_md_files, rule_enabled

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if not rule_enabled(ROOT, "require_heading_blank_line"):
        print("skipped: require_heading_blank_line is disabled")
        return 0

    bad = []
    checked = 0
    for md in iter_md_files(ROOT):
        lines = md.read_text(encoding="utf-8").splitlines()
        in_fence = False
        for i, line in enumerate(lines):
            in_fence = toggle_fence(in_fence, line)
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
