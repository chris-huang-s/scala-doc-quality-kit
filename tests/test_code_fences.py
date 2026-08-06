"""Tests for the fenced code language checker."""
from __future__ import annotations

from conftest import ROOT, load_checker


def test_unlabeled_fence_fails(tmp_path, monkeypatch):
    mod = load_checker("check_code_fences")
    (tmp_path / "doc.md").write_text(
        "# Doc\n\n```\ncode\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_labeled_fence_passes(tmp_path, monkeypatch):
    mod = load_checker("check_code_fences")
    (tmp_path / "doc.md").write_text(
        "# Doc\n\n```scala\nval x = 1\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_examples_pass_fence_check():
    mod = load_checker("check_code_fences")
    assert mod.main() == 0


def test_indented_fence_line_is_detected(tmp_path, monkeypatch):
    mod = load_checker("check_code_fences")
    (tmp_path / "doc.md").write_text(
        "# Doc\n\n  ```scala\nval x = 1\n  ```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_closing_fence_with_language_tag_passes(tmp_path, monkeypatch):
    mod = load_checker("check_code_fences")
    (tmp_path / "doc.md").write_text(
        "# Doc\n\n```scala\nval x = 1\n```scala\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_opening_fence_with_info_string_passes(tmp_path, monkeypatch):
    mod = load_checker("check_code_fences")
    (tmp_path / "doc.md").write_text(
        "# Doc\n\n```scala title=Example\nval x = 1\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_parse_fence_line_ignores_inline_backticks():
    mod = load_checker("check_code_fences")
    assert mod.parse_fence_line("use `code` here") == (False, "")


def test_parse_fence_line_handles_whitespace():
    mod = load_checker("check_code_fences")
    assert mod.parse_fence_line("  ```python  ") == (True, "python")
