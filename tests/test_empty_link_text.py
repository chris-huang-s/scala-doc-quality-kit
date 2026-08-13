"""Tests for empty markdown link text detection."""
from __future__ import annotations

from conftest import ROOT, load_checker


def test_is_empty_link_text():
    mod = load_checker("check_empty_link_text")
    assert mod.is_empty_link_text("")
    assert mod.is_empty_link_text("   ")
    assert mod.is_empty_link_text("\t")
    assert not mod.is_empty_link_text("readme")
    assert not mod.is_empty_link_text(" a ")


def test_empty_link_text_fails(tmp_path, monkeypatch):
    mod = load_checker("check_empty_link_text")
    (tmp_path / "doc.md").write_text("[](./target.md)\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_whitespace_only_link_text_fails(tmp_path, monkeypatch):
    mod = load_checker("check_empty_link_text")
    (tmp_path / "doc.md").write_text("[  ](./target.md)\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_labeled_link_passes(tmp_path, monkeypatch):
    mod = load_checker("check_empty_link_text")
    (tmp_path / "doc.md").write_text("[ok](./target.md)\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_empty_image_alt_is_skipped(tmp_path, monkeypatch):
    mod = load_checker("check_empty_link_text")
    (tmp_path / "doc.md").write_text(
        "![](./pic.png)\n![  ](./pic.png)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_empty_link_inside_fence_ignored(tmp_path, monkeypatch):
    mod = load_checker("check_empty_link_text")
    (tmp_path / "doc.md").write_text(
        "# Title\n\n```\n[](./inside.md)\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_empty_link_inside_inline_code_ignored(tmp_path, monkeypatch):
    mod = load_checker("check_empty_link_text")
    (tmp_path / "doc.md").write_text("`[](./inline.md)`\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_repo_docs_have_no_empty_link_text():
    mod = load_checker("check_empty_link_text")
    assert mod.ROOT == ROOT
    assert mod.main() == 0


def test_check_docs_includes_empty_link_text_checker():
    mod = load_checker("check_docs")
    assert "check_empty_link_text" in mod.CHECKERS
