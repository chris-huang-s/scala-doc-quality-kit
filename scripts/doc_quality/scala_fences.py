"""Scala fenced code block info-string validation."""
from __future__ import annotations

import re

SCALA_FENCE_INFO_RE = re.compile(r"^scala(\s+mdoc(?:\:[\w-]+)?)?(\s+\S.*)?$")


def fence_info_string(line: str) -> str:
    """Return the info string on a fence delimiter line."""
    stripped = line.strip()
    if not stripped.startswith("```"):
        return ""
    return stripped[3:].strip()


def is_valid_scala_fence_info(info: str, *, require_mdoc: bool = False) -> bool:
    """Return whether a fence info string is valid for Scala docs."""
    if not info:
        return False
    if not SCALA_FENCE_INFO_RE.match(info):
        return False
    if require_mdoc and "mdoc" not in info.split():
        return False
    return True


def needs_scala_fence_info(lang: str, info: str) -> bool:
    """Return whether a fence opening should satisfy the Scala info policy."""
    if lang == "scala":
        return True
    if lang == "mdoc" or info.startswith("mdoc"):
        return True
    return False
