"""Tests for consecutive blank line detection in markdown docs."""
from __future__ import annotations

from conftest import ROOT, load_checker


def test_is_blank_line():
    mod = load_checker("check_consecutive_blank_lines")
    assert mod.is_blank_line("")
    assert mod.is_blank_line("   ")
    assert mod.is_blank_line("\t")
    assert not mod.is_blank_line("text")
    assert not mod.is_blank_line(" a ")


def test_three_consecutive_blank_lines_fails(tmp_path, monkeypatch):
    mod = load_checker("check_consecutive_blank_lines")
    (tmp_path / "doc.md").write_text("# Title\n\n\n\nbody\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_two_consecutive_blank_lines_passes(tmp_path, monkeypatch):
    mod = load_checker("check_consecutive_blank_lines")
    (tmp_path / "doc.md").write_text("# Title\n\n\nbody\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_blank_run_inside_fence_ignored(tmp_path, monkeypatch):
    mod = load_checker("check_consecutive_blank_lines")
    (tmp_path / "doc.md").write_text(
        "# Title\n\n```\n\n\n\n```\n\nbody\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_repo_docs_have_no_consecutive_blank_runs():
    mod = load_checker("check_consecutive_blank_lines")
    assert mod.ROOT == ROOT
    assert mod.main() == 0


def test_check_docs_includes_consecutive_blank_lines_checker():
    mod = load_checker("check_docs")
    assert "check_consecutive_blank_lines" in mod.CHECKERS
