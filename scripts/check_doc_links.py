#!/usr/bin/env python3
"""Scan Markdown files for local markdown links and report broken paths."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
FENCE_RE = re.compile(r"^```")


def iter_md_files(root: Path):
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        yield path


def strip_code(text: str) -> str:
    """Ignore links that only appear inside code fences or inline code."""
    lines = text.splitlines(keepends=True)
    out = []
    in_fence = False
    for line in lines:
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            out.append("\n" if line.endswith("\n") else "")
            continue
        if in_fence:
            out.append("\n" if line.endswith("\n") else "")
            continue
        out.append(INLINE_CODE_RE.sub("", line))
    return "".join(out)


def is_local_link(target: str) -> bool:
    t = target.strip()
    if t.startswith("#"):
        return False
    if "://" in t:
        return False
    if t.startswith("mailto:"):
        return False
    return True


def main() -> int:
    broken = []
    checked = 0
    for md in iter_md_files(ROOT):
        text = strip_code(md.read_text(encoding="utf-8"))
        for _label, target in LINK_RE.findall(text):
            href = target.strip().split()[0].strip('"')
            if not is_local_link(href):
                continue
            checked += 1
            path_part = href.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (md.parent / path_part).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                broken.append((md, href, "outside repo"))
                continue
            if not resolved.exists():
                broken.append((md, href, "missing"))

    print(f"checked_local_links={checked}")
    if broken:
        for md, href, reason in broken:
            print(f"BROKEN ({reason}): {md.relative_to(ROOT)} -> {href}")
        return 1
    print("ok: no broken local markdown links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
