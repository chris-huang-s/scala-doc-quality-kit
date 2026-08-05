"""Tests for the markdown link checker."""
from __future__ import annotations

from conftest import ROOT, load_checker


def test_is_local_link():
    mod = load_checker("check_doc_links")
    assert mod.is_local_link("./foo.md")
    assert mod.is_local_link("docs/bar.md")
    assert not mod.is_local_link("https://example.com")
    assert not mod.is_local_link("#section")
    assert not mod.is_local_link("mailto:a@b.com")


def test_strip_code_ignores_fenced_links():
    mod = load_checker("check_doc_links")
    text = (
        "See [outside](./outside.md)\n"
        "```\n"
        "[inside](./inside.md)\n"
        "```\n"
    )
    stripped = mod.strip_code(text)
    assert "outside.md" in stripped
    assert "inside.md" not in stripped


def test_broken_local_link_detected(tmp_path, monkeypatch):
    mod = load_checker("check_doc_links")
    (tmp_path / "doc.md").write_text("[bad](./missing.md)\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_valid_local_link_passes(tmp_path, monkeypatch):
    mod = load_checker("check_doc_links")
    (tmp_path / "target.md").write_text("# Target\n", encoding="utf-8")
    (tmp_path / "doc.md").write_text("[ok](./target.md)\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_examples_pass_link_check():
    mod = load_checker("check_doc_links")
    assert mod.ROOT == ROOT
    assert mod.main() == 0
