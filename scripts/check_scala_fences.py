#!/usr/bin/env python3
"""Require explicit Scala info strings on Scala documentation fences."""
from __future__ import annotations

import sys
from pathlib import Path

from doc_quality.markdown import parse_fence_line
from doc_quality.scala_fences import (
    fence_info_string,
    is_valid_scala_fence_info,
    needs_scala_fence_info,
)
from doc_quality_config import iter_md_files, rule_enabled

ROOT = Path(__file__).resolve().parents[1]

__all__ = ["main"]


def main() -> int:
    if not rule_enabled(ROOT, "require_scala_fence_info"):
        print("skipped: require_scala_fence_info is disabled")
        return 0

    require_mdoc = rule_enabled(ROOT, "require_scala_mdoc")
    bad = []
    checked = 0
    for md in iter_md_files(ROOT):
        lines = md.read_text(encoding="utf-8").splitlines()
        in_fence = False
        for i, line in enumerate(lines, start=1):
            is_fence, lang = parse_fence_line(line)
            if not is_fence:
                continue
            if not in_fence:
                in_fence = True
                info = fence_info_string(line)
                if not needs_scala_fence_info(lang, info):
                    continue
                checked += 1
                if not is_valid_scala_fence_info(info, require_mdoc=require_mdoc):
                    bad.append((md, i, info or "(none)"))
            else:
                in_fence = False

    print(f"checked_scala_fences={checked}")
    if bad:
        hint = "scala mdoc" if require_mdoc else "scala or scala mdoc"
        for md, line_no, info in bad:
            print(
                f"INVALID_SCALA_FENCE: {md.relative_to(ROOT)}:{line_no} "
                f"info={info!r} (want {hint!r})"
            )
        return 1
    print("ok: scala fences use an explicit scala info string")
    return 0


if __name__ == "__main__":
    sys.exit(main())
