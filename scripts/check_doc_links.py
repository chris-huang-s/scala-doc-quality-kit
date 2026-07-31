#!/usr/bin/env python3
"""Scan Markdown files for local markdown links and report broken paths."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def iter_md_files(root: Path):
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        yield path


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
        text = md.read_text(encoding="utf-8")
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
