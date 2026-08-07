"""Load scan paths and iterate markdown files for doc quality checks."""
from __future__ import annotations

from doc_quality.config import CONFIG_NAME, DEFAULT_PATHS, load_config
from doc_quality.paths import iter_md_files

__all__ = ["CONFIG_NAME", "DEFAULT_PATHS", "iter_md_files", "load_config"]
