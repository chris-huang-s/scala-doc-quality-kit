#!/usr/bin/env python3
"""Scan Markdown files for local markdown links and report broken paths."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from doc_quality.markdown import FENCE_RE, collect_heading_slugs, toggle_fence
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


def is_local_link(target: str) -> bool:
    t = target.strip()
    if t.startswith("#"):
        return True
    if "://" in t:
        return False
    if t.startswith("mailto:"):
        return False
    return True


def split_link_target(href: str) -> tuple[str, str | None]:
    """Split a href into path and optional fragment."""
    if "#" not in href:
        return href, None
    path_part, fragment = href.split("#", 1)
    return path_part, fragment or None


def resolve_target_file(source: Path, path_part: str) -> Path:
    """Resolve the markdown file a local link points at."""
    if not path_part:
        return source.resolve()
    return (source.parent / path_part).resolve()


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
            path_part, fragment = split_link_target(href)
            if path_part:
                resolved = resolve_target_file(md, path_part)
                try:
                    resolved.relative_to(ROOT.resolve())
                except ValueError:
                    broken.append((md, href, "outside repo"))
                    continue
                if not resolved.exists():
                    broken.append((md, href, "missing"))
                    continue
            else:
                resolved = md.resolve()

            if fragment:
                slugs = collect_heading_slugs(resolved.read_text(encoding="utf-8"))
                if fragment not in slugs:
                    broken.append((md, href, "missing anchor"))

    print(f"checked_local_links={checked}")
    if broken:
        for md, href, reason in broken:
            print(f"BROKEN ({reason}): {md.relative_to(ROOT)} -> {href}")
        return 1
    print("ok: no broken local markdown links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
