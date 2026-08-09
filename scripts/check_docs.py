#!/usr/bin/env python3
"""Run all markdown doc quality checks from one entrypoint."""
from __future__ import annotations

import argparse
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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the unified checker entrypoint."""
    parser = argparse.ArgumentParser(
        description="Run markdown doc quality checks",
    )
    parser.add_argument(
        "--only",
        action="append",
        dest="only",
        metavar="NAME",
        help="Run only the named checker (repeatable). Default: full suite.",
    )
    # Default to [] so library/test callers are not polluted by process argv.
    return parser.parse_args([] if argv is None else argv)


def selected_checkers(only: list[str] | None) -> list[str] | int:
    """Return checker names to run, or exit code 2 when a name is unknown."""
    if not only:
        return list(CHECKERS)
    unknown = [name for name in only if name not in CHECKERS]
    if unknown:
        for name in unknown:
            print(f"unknown checker: {name}", file=sys.stderr)
        print(
            f"known checkers: {', '.join(CHECKERS)}",
            file=sys.stderr,
        )
        return 2
    # Preserve CHECKERS order while honoring requested names
    wanted = set(only)
    return [name for name in CHECKERS if name in wanted]


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    selected = selected_checkers(args.only)
    if isinstance(selected, int):
        return selected

    failed: list[str] = []
    for name in selected:
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
    sys.exit(main(sys.argv[1:]))
