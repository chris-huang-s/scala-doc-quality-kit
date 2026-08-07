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


def test_config_includes_version_and_rules():
    config = load_checker("doc_quality_config")
    root = Path(__file__).resolve().parents[1]
    loaded = config.load_config(root)
    assert loaded["version"] == 1
    assert loaded["rules"]["require_single_h1"] is True
    assert loaded["rules"]["require_heading_blank_line"] is True
    assert loaded["rules"]["require_fence_language"] is True


def test_missing_config_uses_default_version_and_rules(tmp_path):
    config = load_checker("doc_quality_config")
    loaded = config.load_config(tmp_path)
    assert loaded["version"] == 1
    assert loaded["rules"]["require_single_h1"] is True


def test_rule_toggle_can_disable_single_h1(tmp_path, monkeypatch):
    config = load_checker("doc_quality_config")
    h1 = load_checker("check_single_h1")
    (tmp_path / "doc.md").write_text("# One\n# Two\n", encoding="utf-8")
    (tmp_path / ".doc-quality.json").write_text(
        '{"version": 1, "paths": ["."], "rules": {"require_single_h1": false}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(h1, "ROOT", tmp_path)
    assert h1.main() == 0


def test_partial_rules_keep_defaults_for_others(tmp_path):
    config = load_checker("doc_quality_config")
    (tmp_path / ".doc-quality.json").write_text(
        '{"version": 1, "paths": ["."], "rules": {"require_fence_language": false}}',
        encoding="utf-8",
    )
    loaded = config.load_config(tmp_path)
    assert loaded["rules"]["require_fence_language"] is False
    assert loaded["rules"]["require_single_h1"] is True
