"""Tests for insecure http:// markdown link detection."""
from __future__ import annotations

from conftest import ROOT, load_checker


def test_is_insecure_http_link():
    mod = load_checker("check_insecure_links")
    assert mod.is_insecure_http_link("http://example.com/docs")
    assert mod.is_insecure_http_link("HTTP://Example.COM")
    assert not mod.is_insecure_http_link("https://example.com/docs")
    assert not mod.is_insecure_http_link("./local.md")
    assert not mod.is_insecure_http_link("mailto:a@b.com")


def test_insecure_http_link_fails(tmp_path, monkeypatch):
    mod = load_checker("check_insecure_links")
    (tmp_path / "doc.md").write_text(
        "[bad](http://example.com/path)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_https_link_passes(tmp_path, monkeypatch):
    mod = load_checker("check_insecure_links")
    (tmp_path / "doc.md").write_text(
        "[ok](https://example.com/path)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_http_inside_code_ignored(tmp_path, monkeypatch):
    mod = load_checker("check_insecure_links")
    (tmp_path / "doc.md").write_text(
        "Use `http://example.com` in docs.\n\n"
        "```\n"
        "[inside](http://example.com/in-fence)\n"
        "```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_repo_docs_have_no_insecure_http():
    mod = load_checker("check_insecure_links")
    assert mod.ROOT == ROOT
    assert mod.main() == 0


def test_check_docs_includes_insecure_checker():
    mod = load_checker("check_docs")
    assert "check_insecure_links" in mod.CHECKERS
