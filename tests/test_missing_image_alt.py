"""Tests for missing markdown image alt text detection."""
from __future__ import annotations

from conftest import ROOT, load_checker


def test_is_missing_alt():
    mod = load_checker("check_missing_image_alt")
    assert mod.is_missing_alt("")
    assert mod.is_missing_alt("   ")
    assert mod.is_missing_alt("\t")
    assert not mod.is_missing_alt("diagram")
    assert not mod.is_missing_alt(" a ")


def test_empty_image_alt_fails(tmp_path, monkeypatch):
    mod = load_checker("check_missing_image_alt")
    (tmp_path / "doc.md").write_text("![](./pic.png)\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_whitespace_only_image_alt_fails(tmp_path, monkeypatch):
    mod = load_checker("check_missing_image_alt")
    (tmp_path / "doc.md").write_text("![  ](./pic.png)\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_labeled_image_passes(tmp_path, monkeypatch):
    mod = load_checker("check_missing_image_alt")
    (tmp_path / "doc.md").write_text("![ok](./pic.png)\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_empty_link_text_is_skipped(tmp_path, monkeypatch):
    mod = load_checker("check_missing_image_alt")
    (tmp_path / "doc.md").write_text(
        "[](./target.md)\n[  ](./target.md)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_empty_image_alt_inside_fence_ignored(tmp_path, monkeypatch):
    mod = load_checker("check_missing_image_alt")
    (tmp_path / "doc.md").write_text(
        "# Title\n\n```\n![](./inside.png)\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_empty_image_alt_inside_inline_code_ignored(tmp_path, monkeypatch):
    mod = load_checker("check_missing_image_alt")
    (tmp_path / "doc.md").write_text("`![](./inline.png)`\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_repo_docs_have_no_missing_image_alt():
    mod = load_checker("check_missing_image_alt")
    assert mod.ROOT == ROOT
    assert mod.main() == 0


def test_check_docs_includes_missing_image_alt_checker():
    mod = load_checker("check_docs")
    assert "check_missing_image_alt" in mod.CHECKERS
