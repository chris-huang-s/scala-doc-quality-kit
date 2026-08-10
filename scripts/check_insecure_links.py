#!/usr/bin/env python3
"""Flag insecure http:// external markdown links."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from doc_quality.markdown import toggle_fence
from doc_quality_config import iter_md_files

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
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


def is_insecure_http_link(target: str) -> bool:
    """Return True for bare http:// URLs (https and non-URLs are fine)."""
    href = target.strip().split()[0].strip('"').strip("'")
    return href.lower().startswith("http://")


def main() -> int:
    insecure: list[tuple[Path, str]] = []
    checked = 0
    for md in iter_md_files(ROOT):
        text = strip_code(md.read_text(encoding="utf-8"))
        for _label, target in LINK_RE.findall(text):
            href = target.strip().split()[0].strip('"').strip("'")
            if not href.lower().startswith("http://") and not href.lower().startswith(
                "https://"
            ):
                continue
            checked += 1
            if is_insecure_http_link(href):
                insecure.append((md, href))

    print(f"checked_http_links={checked}")
    if insecure:
        for md, href in insecure:
            print(f"INSECURE: {md.relative_to(ROOT)} -> {href}")
        return 1
    print("ok: no insecure http:// markdown links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
