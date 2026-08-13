"""Tests for hard tab detection in markdown docs."""
from __future__ import annotations

from conftest import ROOT, load_checker


def test_line_has_hard_tab():
    mod = load_checker("check_hard_tabs")
    assert mod.line_has_hard_tab("hello\tworld")
    assert mod.line_has_hard_tab("\tindented")
    assert not mod.line_has_hard_tab("hello world")
    assert not mod.line_has_hard_tab("")
    assert not mod.line_has_hard_tab("    spaces")


def test_hard_tab_fails(tmp_path, monkeypatch):
    mod = load_checker("check_hard_tabs")
    (tmp_path / "doc.md").write_text("# Title\n\nbad\tline\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_spaces_only_passes(tmp_path, monkeypatch):
    mod = load_checker("check_hard_tabs")
    (tmp_path / "doc.md").write_text(
        "# Title\n\n    indented with spaces\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_hard_tab_inside_fence_ignored(tmp_path, monkeypatch):
    mod = load_checker("check_hard_tabs")
    (tmp_path / "doc.md").write_text(
        "# Title\n\n```\ncode\twith\ttab\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_repo_docs_have_no_hard_tabs():
    mod = load_checker("check_hard_tabs")
    assert mod.ROOT == ROOT
    assert mod.main() == 0


def test_check_docs_includes_hard_tabs_checker():
    mod = load_checker("check_docs")
    assert "check_hard_tabs" in mod.CHECKERS
