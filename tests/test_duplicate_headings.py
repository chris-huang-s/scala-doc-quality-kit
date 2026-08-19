"""Tests for duplicate markdown heading slug detection."""
from __future__ import annotations

from conftest import ROOT, load_checker


def test_find_duplicate_headings_uses_slug():
    mod = load_checker("check_duplicate_headings")
    text = "# Title\n\n## Hello World\n\n## hello world\n"
    dups = mod.find_duplicate_headings(text)
    assert dups == [(5, "hello world", "hello-world")]


def test_duplicate_headings_fail(tmp_path, monkeypatch):
    mod = load_checker("check_duplicate_headings")
    (tmp_path / "doc.md").write_text(
        "# Title\n\n## Setup\n\n## Setup\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_unique_headings_pass(tmp_path, monkeypatch):
    mod = load_checker("check_duplicate_headings")
    (tmp_path / "doc.md").write_text(
        "# Title\n\n## Setup\n\n## Usage\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_fenced_headings_are_ignored(tmp_path, monkeypatch):
    mod = load_checker("check_duplicate_headings")
    (tmp_path / "doc.md").write_text(
        "# Title\n\n## Setup\n\n```\n## Setup\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_repo_docs_have_no_duplicate_headings():
    mod = load_checker("check_duplicate_headings")
    assert mod.ROOT == ROOT
    assert mod.main() == 0


def test_check_docs_includes_duplicate_heading_checker():
    mod = load_checker("check_docs")
    assert "check_duplicate_headings" in mod.CHECKERS


def test_find_duplicate_headings_detects_slug_collisions():
    mod = load_checker("check_duplicate_headings")
    text = "# Title\n\n## C++ Setup!\n\n## C Setup\n"
    dups = mod.find_duplicate_headings(text)
    assert dups == [(5, "C Setup", "c-setup")]


def test_find_duplicate_headings_ignores_non_slug_lines():
    mod = load_checker("check_duplicate_headings")
    text = "# Title\n\n## !!!\n\n## ???\n"
    dups = mod.find_duplicate_headings(text)
    assert dups == []
