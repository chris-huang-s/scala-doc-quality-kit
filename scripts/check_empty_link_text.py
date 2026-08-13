#!/usr/bin/env python3
"""Flag markdown links whose visible label is empty or whitespace-only."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from doc_quality.markdown import toggle_fence
from doc_quality_config import iter_md_files

ROOT = Path(__file__).resolve().parents[1]
LINK_OR_IMAGE_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def strip_code(text: str) -> str:
    """Ignore links that only appear inside code fences or inline code."""
    lines = text.splitlines(keepends=True)
    out = []
    in_fence = False
    for line in lines:
        in_fence = toggle_fence(in_fence, line)
        if in_fence:
            out.append("\n" if line.endswith("\n") else "")
            continue
        out.append(INLINE_CODE_RE.sub("", line))
    return "".join(out)


def is_empty_link_text(label: str) -> bool:
    """Return True when the link label is empty or whitespace-only."""
    return not label.strip()


def main() -> int:
    bad: list[tuple[Path, str]] = []
    checked = 0
    for md in iter_md_files(ROOT):
        text = strip_code(md.read_text(encoding="utf-8"))
        for bang, label, target in LINK_OR_IMAGE_RE.findall(text):
            if bang == "!":
                continue
            checked += 1
            if is_empty_link_text(label):
                href = target.strip().split()[0].strip('"').strip("'")
                bad.append((md, href))

    print(f"checked_markdown_links={checked}")
    if bad:
        for md, href in bad:
            print(f"EMPTY_LINK_TEXT: {md.relative_to(ROOT)} -> {href}")
        return 1
    print("ok: no empty or whitespace-only markdown link text")
    return 0


if __name__ == "__main__":
    sys.exit(main())
