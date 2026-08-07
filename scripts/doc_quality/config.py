"""Configuration loading for doc quality checks."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONFIG_NAME = ".doc-quality.json"
DEFAULT_PATHS = ["."]
DEFAULT_VERSION = 1
DEFAULT_RULES = {
    "require_single_h1": True,
    "require_heading_blank_line": True,
    "require_fence_language": True,
    "require_scala_fence_info": True,
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


def load_config(root: Path) -> dict:
    """Read .doc-quality.json or return defaults that scan the whole repo."""
    config_path = root / CONFIG_NAME
    if not config_path.is_file():
        return {
            "version": DEFAULT_VERSION,
            "paths": list(DEFAULT_PATHS),
            "rules": dict(DEFAULT_RULES),
        }
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "version": DEFAULT_VERSION,
            "paths": list(DEFAULT_PATHS),
            "rules": dict(DEFAULT_RULES),
        }

    version = data.get("version", DEFAULT_VERSION)
    if not isinstance(version, int) or version < 1:
        version = DEFAULT_VERSION

    paths = data.get("paths", DEFAULT_PATHS)
    if not isinstance(paths, list) or not paths:
        paths = list(DEFAULT_PATHS)
    else:
        cleaned = [p for p in paths if isinstance(p, str) and p.strip()]
        paths = cleaned if cleaned else list(DEFAULT_PATHS)

    rules = _normalize_rules(data.get("rules"))
    return {"version": version, "paths": paths, "rules": rules}


def rule_enabled(root: Path, name: str) -> bool:
    """Return whether a named rule toggle is enabled."""
    rules = load_config(root)["rules"]
    return bool(rules.get(name, DEFAULT_RULES.get(name, True)))
