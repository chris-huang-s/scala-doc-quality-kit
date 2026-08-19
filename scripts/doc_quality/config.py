"""Configuration loading for doc quality checks."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

CONFIG_NAME = ".doc-quality.json"
DEFAULT_PATHS = ["."]
DEFAULT_IGNORE_GLOBS: list[str] = []
DEFAULT_VERSION = 1
DOC_QUALITY_PATHS_ENV = "DOC_QUALITY_PATHS"

DEFAULT_RULES = {
    "require_single_h1": True,
    "require_heading_blank_line": True,
    "require_fence_language": True,
    "require_scala_fence_info": True,
    "require_scala_mdoc": False,
}


def _normalize_rules(raw: Any) -> dict[str, bool]:
    """Merge optional rule toggles with defaults that preserve current behavior."""
    rules = dict(DEFAULT_RULES)
    if not isinstance(raw, dict):
        return rules
    for key in DEFAULT_RULES:
        value = raw.get(key)
        if isinstance(value, bool):
            rules[key] = value
    return rules



def _normalize_paths(raw: Any) -> list[str]:
    """Return cleaned scan paths; invalid input yields default paths."""
    if not isinstance(raw, list) or not raw:
        return list(DEFAULT_PATHS)
    cleaned = [p for p in raw if isinstance(p, str) and p.strip()]
    return cleaned if cleaned else list(DEFAULT_PATHS)


def _env_override_paths() -> list[str] | None:
    """Return path list from DOC_QUALITY_PATHS when provided."""
    raw = os.getenv(DOC_QUALITY_PATHS_ENV)
    if raw is None:
        return None
    cleaned = [p.strip() for p in raw.split(',') if p.strip()]
    return cleaned if cleaned else None

def _normalize_ignore_globs(raw: Any) -> list[str]:
    """Return cleaned ignore glob patterns; invalid input yields an empty list."""
    if not isinstance(raw, list):
        return list(DEFAULT_IGNORE_GLOBS)
    cleaned = [p for p in raw if isinstance(p, str) and p.strip()]
    return cleaned


def load_config(root: Path) -> dict:
    """Read .doc-quality.json or return defaults that scan the whole repo."""
    config_path = root / CONFIG_NAME
    if not config_path.is_file():
        return {
            "version": DEFAULT_VERSION,
            "paths": list(DEFAULT_PATHS),
            "ignore_globs": list(DEFAULT_IGNORE_GLOBS),
            "rules": dict(DEFAULT_RULES),
        }
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "version": DEFAULT_VERSION,
            "paths": list(DEFAULT_PATHS),
            "ignore_globs": list(DEFAULT_IGNORE_GLOBS),
            "rules": dict(DEFAULT_RULES),
        }

    version = data.get("version", DEFAULT_VERSION)
    if not isinstance(version, int) or version < 1:
        version = DEFAULT_VERSION

    paths = _normalize_paths(data.get("paths", DEFAULT_PATHS))

    env_paths = _env_override_paths()
    if env_paths is not None:
        paths = env_paths

    rules = _normalize_rules(data.get("rules"))
    ignore_globs = _normalize_ignore_globs(data.get("ignore_globs"))
    return {
        "version": version,
        "paths": paths,
        "ignore_globs": ignore_globs,
        "rules": rules,
    }


def rule_enabled(root: Path, name: str) -> bool:
    """Return whether a named rule toggle is enabled."""
    rules = load_config(root)["rules"]
    return bool(rules.get(name, DEFAULT_RULES.get(name, True)))
