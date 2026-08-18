#!/usr/bin/env python3
"""Flag CR and CRLF line endings in markdown files."""
from __future__ import annotations

import sys
from pathlib import Path

from doc_quality_config import iter_md_files

ROOT = Path(__file__).resolve().parents[1]


def classify_ending(line: bytes) -> str | None:
    """Return 'CRLF' or 'CR' when the line does not use LF-only endings."""
    if line.endswith(b"\r\n"):
        return "CRLF"
    if line.endswith(b"\r"):
        return "CR"
    return None


def find_non_lf_lines(data: bytes) -> list[tuple[int, str]]:
    """Return (line_no, kind) for lines that end with CR or CRLF."""
    found: list[tuple[int, str]] = []
    for line_no, line in enumerate(data.splitlines(keepends=True), start=1):
        kind = classify_ending(line)
        if kind is not None:
            found.append((line_no, kind))
    return found


def main() -> int:
    bad: list[tuple[Path, int, str]] = []
    checked = 0
    for md in iter_md_files(ROOT):
        checked += 1
        for line_no, kind in find_non_lf_lines(md.read_bytes()):
            bad.append((md, line_no, kind))

    print(f"checked_markdown_files={checked}")
    if bad:
        for md, line_no, kind in bad:
            rel = md.relative_to(ROOT)
            print(f"MIXED_LINE_ENDING: {rel}:{line_no} {kind}")
        return 1
    print("ok: markdown files use LF line endings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
