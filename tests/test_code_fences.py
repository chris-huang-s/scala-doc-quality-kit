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
