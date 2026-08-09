"""Tests for the markdown image path checker."""
from __future__ import annotations

from conftest import ROOT, load_checker


def test_is_local_image():
    mod = load_checker("check_doc_images")
    assert mod.is_local_image("./diagram.png")
    assert mod.is_local_image("docs/img.svg")
    assert not mod.is_local_image("https://example.com/a.png")
    assert not mod.is_local_image("http://example.com/a.png")
    assert not mod.is_local_image("data:image/png;base64,abc")


def test_strip_code_ignores_fenced_images():
    mod = load_checker("check_doc_images")
    text = (
        "![outside](./outside.png)\n"
        "```\n"
        "![inside](./inside.png)\n"
        "```\n"
    )
    stripped = mod.strip_code(text)
    assert "outside.png" in stripped
    assert "inside.png" not in stripped


def test_missing_local_image_fails(tmp_path, monkeypatch):
    mod = load_checker("check_doc_images")
    (tmp_path / "doc.md").write_text("![bad](./missing.png)\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_valid_local_image_passes(tmp_path, monkeypatch):
    mod = load_checker("check_doc_images")
    (tmp_path / "pic.png").write_bytes(b"png")
    (tmp_path / "doc.md").write_text("![ok](./pic.png)\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_remote_and_data_images_are_skipped(tmp_path, monkeypatch):
    mod = load_checker("check_doc_images")
    (tmp_path / "doc.md").write_text(
        "![a](https://example.com/a.png)\n"
        "![b](http://example.com/b.png)\n"
        "![c](data:image/png;base64,abc)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_examples_pass_image_check():
    mod = load_checker("check_doc_images")
    assert mod.ROOT == ROOT
    assert mod.main() == 0
