"""Tests for ATX heading level skip detection."""
from __future__ import annotations

from conftest import ROOT, load_checker


def test_find_heading_level_skips_detects_jump():
    mod = load_checker("check_heading_level_skips")
    text = "# Title\n\n### Too deep\n"
    skips = mod.find_heading_level_skips(text)
    assert skips == [(3, 1, 3, "Too deep")]


def test_consecutive_levels_pass():
    mod = load_checker("check_heading_level_skips")
    text = "# Title\n\n## Section\n\n### Detail\n"
    assert mod.find_heading_level_skips(text) == []


def test_level_decrease_is_allowed():
    mod = load_checker("check_heading_level_skips")
    text = "# Title\n\n## Section\n\n### Detail\n\n## Next\n"
    assert mod.find_heading_level_skips(text) == []


def test_heading_level_skip_fails(tmp_path, monkeypatch):
    mod = load_checker("check_heading_level_skips")
    (tmp_path / "doc.md").write_text("# Title\n\n### Skip\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_consecutive_headings_pass_main(tmp_path, monkeypatch):
    mod = load_checker("check_heading_level_skips")
    (tmp_path / "doc.md").write_text(
        "# Title\n\n## Section\n\n### Detail\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_fenced_headings_are_ignored(tmp_path, monkeypatch):
    mod = load_checker("check_heading_level_skips")
    (tmp_path / "doc.md").write_text(
        "# Title\n\n```\n### Not a real heading\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_repo_docs_have_no_heading_level_skips():
    mod = load_checker("check_heading_level_skips")
    assert mod.ROOT == ROOT
    assert mod.main() == 0


def test_check_docs_includes_heading_level_skips_checker():
    mod = load_checker("check_docs")
    assert "check_heading_level_skips" in mod.CHECKERS
