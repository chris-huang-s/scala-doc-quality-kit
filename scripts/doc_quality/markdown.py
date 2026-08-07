"""Markdown fence and heading parsing helpers."""
from __future__ import annotations

import re

FENCE_RE = re.compile(r"^```")
FENCE_OPEN_RE = re.compile(r"^```([\w.+-]*)(?:\s+\S.*)?\s*$")
H1_RE = re.compile(r"^#\s+\S")
HEADING_RE = re.compile(r"^#{2,6}\s+\S")


def parse_fence_line(line: str) -> tuple[bool, str]:
    """Return whether the line opens or closes a fence and its language tag."""
    stripped = line.strip()
    if not stripped.startswith("```"):
        return False, ""
    match = FENCE_OPEN_RE.match(stripped)
    if not match:
        return False, ""
    return True, match.group(1)


def toggle_fence(in_fence: bool, line: str) -> bool:
    """Flip fence state when the line is a fence delimiter."""
    if FENCE_RE.match(line.strip()):
        return not in_fence
    return in_fence


def count_h1(text: str) -> int:
    """Count top-level headings outside fenced code blocks."""
    count = 0
    in_fence = False
    for line in text.splitlines():
        in_fence = toggle_fence(in_fence, line)
        if in_fence:
            continue
        if H1_RE.match(line):
            count += 1
    return count
