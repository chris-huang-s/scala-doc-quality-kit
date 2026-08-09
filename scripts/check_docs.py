#!/usr/bin/env python3
"""Run all markdown doc quality checks from one entrypoint."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKERS = (
    "check_doc_links",
    "check_doc_images",
    "check_code_fences",
    "check_scala_fences",
    "check_single_h1",
    "check_heading_spacing",
)


def run_checker(name: str) -> int:
    """Import and run one checker module's main()."""
    mod = importlib.import_module(name)
    return int(mod.main())


def main() -> int:
    failed: list[str] = []
    for name in CHECKERS:
        print(f"--- {name} ---")
        rc = run_checker(name)
        if rc != 0:
            failed.append(name)

    if failed:
        print(f"failed checkers: {', '.join(failed)}")
        return 1

    print("ok: all doc quality checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
