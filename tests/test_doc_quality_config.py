"""Tests for .doc-quality.json path configuration."""
from __future__ import annotations

from pathlib import Path

from conftest import load_checker


def test_default_config_scans_repo_root(tmp_path):
    config = load_checker("doc_quality_config")
    (tmp_path / "a.md").write_text("# A\n", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.md").write_text("# B\n", encoding="utf-8")
    found = sorted(p.name for p in config.iter_md_files(tmp_path))
    assert found == ["a.md", "b.md"]


def test_config_limits_scan_paths(tmp_path):
    config = load_checker("doc_quality_config")
    docs = tmp_path / "docs"
    docs.mkdir()
    other = tmp_path / "other"
    other.mkdir()
    (docs / "keep.md").write_text("# Keep\n", encoding="utf-8")
    (other / "skip.md").write_text("# Skip\n", encoding="utf-8")
    (tmp_path / ".doc-quality.json").write_text(
        '{"paths": ["docs"]}',
        encoding="utf-8",
    )
    found = [p.name for p in config.iter_md_files(tmp_path)]
    assert found == ["keep.md"]


def test_invalid_config_falls_back_to_default(tmp_path):
    config = load_checker("doc_quality_config")
    (tmp_path / "one.md").write_text("# One\n", encoding="utf-8")
    (tmp_path / ".doc-quality.json").write_text("not json", encoding="utf-8")
    found = [p.name for p in config.iter_md_files(tmp_path)]
    assert found == ["one.md"]


def test_repo_config_keeps_examples_green():
    config = load_checker("doc_quality_config")
    root = Path(__file__).resolve().parents[1]
    names = sorted(p.relative_to(root).as_posix() for p in config.iter_md_files(root))
    assert names == ["README.md", "examples/sample-docs.md"]
