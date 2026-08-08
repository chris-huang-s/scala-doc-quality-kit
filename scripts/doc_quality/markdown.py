"""Markdown fence and heading parsing helpers."""
from __future__ import annotations

import re

FENCE_RE = re.compile(r"^```")
FENCE_OPEN_RE = re.compile(r"^```([\w.+-]*)(?:\s+\S.*)?\s*$")
H1_RE = re.compile(r"^#\s+\S")
HEADING_RE = re.compile(r"^#{1,6}\s+\S")
HEADING_TEXT_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")


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


def heading_slug(title: str) -> str:
    """Build a GitHub-style anchor slug from heading text."""
    cleaned = re.sub(r"[*_`]", "", title.strip().lower())
    cleaned = re.sub(r"[^\w\s-]", "", cleaned)
    return re.sub(r"\s+", "-", cleaned).strip("-")


def collect_heading_slugs(text: str) -> set[str]:
    """Return anchor slugs for headings outside fenced code blocks."""
    slugs: set[str] = set()
    seen: dict[str, int] = {}
    in_fence = False
    for line in text.splitlines():
        in_fence = toggle_fence(in_fence, line)
        if in_fence:
            continue
        match = HEADING_TEXT_RE.match(line)
        if not match:
            continue
        base = heading_slug(match.group(1))
        if not base:
            continue
        count = seen.get(base, 0)
        slug = base if count == 0 else f"{base}-{count}"
        seen[base] = count + 1
        slugs.add(slug)
    return slugs
