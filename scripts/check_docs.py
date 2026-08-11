#!/usr/bin/env python3
"""Run all markdown doc quality checks from one entrypoint."""
from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKERS = (
    "check_doc_links",
    "check_insecure_links",
    "check_doc_images",
    "check_code_fences",
    "check_scala_fences",
    "check_single_h1",
    "check_heading_spacing",
    "check_trailing_whitespace",
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
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a JSON summary {ok, passed, failed} instead of text.",
    )
    parser.add_argument(
        "--list-checkers",
        action="store_true",
        help="Print checker names in suite order and exit (ignores --only/--json).",
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
    if args.list_checkers:
        for name in CHECKERS:
            print(name)
        return 0

    selected = selected_checkers(args.only)
    if isinstance(selected, int):
        return selected

    passed: list[str] = []
    failed: list[str] = []
    for name in selected:
        if not args.json:
            print(f"--- {name} ---")
        if args.json:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = run_checker(name)
        else:
            rc = run_checker(name)
        if rc != 0:
            failed.append(name)
        else:
            passed.append(name)

    if args.json:
        payload = {"ok": not failed, "passed": passed, "failed": failed}
        print(json.dumps(payload, separators=(",", ":")))
        return 1 if failed else 0

    if failed:
        print(f"failed checkers: {', '.join(failed)}")
        return 1

    print("ok: all doc quality checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
