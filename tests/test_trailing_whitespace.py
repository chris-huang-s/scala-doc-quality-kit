"""Tests for trailing whitespace detection in markdown docs."""
from __future__ import annotations

from conftest import ROOT, load_checker


def test_line_has_trailing_whitespace():
    mod = load_checker("check_trailing_whitespace")
    assert mod.line_has_trailing_whitespace("hello ")
    assert mod.line_has_trailing_whitespace("hello\t")
    assert not mod.line_has_trailing_whitespace("hello")
    assert not mod.line_has_trailing_whitespace("   ")
    assert not mod.line_has_trailing_whitespace("")


def test_trailing_whitespace_fails(tmp_path, monkeypatch):
    mod = load_checker("check_trailing_whitespace")
    (tmp_path / "doc.md").write_text("# Title\n\nbad line \n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_clean_markdown_passes(tmp_path, monkeypatch):
    mod = load_checker("check_trailing_whitespace")
    (tmp_path / "doc.md").write_text("# Title\n\nclean line\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_trailing_ws_inside_fence_ignored(tmp_path, monkeypatch):
    mod = load_checker("check_trailing_whitespace")
    (tmp_path / "doc.md").write_text(
        "# Title\n\n```\ncode with space \n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_repo_docs_have_no_trailing_whitespace():
    mod = load_checker("check_trailing_whitespace")
    assert mod.ROOT == ROOT
    assert mod.main() == 0


def test_check_docs_includes_trailing_whitespace_checker():
    mod = load_checker("check_docs")
    assert "check_trailing_whitespace" in mod.CHECKERS
