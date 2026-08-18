"""Tests for CR/CRLF line-ending detection in markdown docs."""
from __future__ import annotations

from conftest import ROOT, load_checker


def test_classify_ending():
    mod = load_checker("check_mixed_line_endings")
    assert mod.classify_ending(b"hello\r\n") == "CRLF"
    assert mod.classify_ending(b"hello\r") == "CR"
    assert mod.classify_ending(b"hello\n") is None
    assert mod.classify_ending(b"hello") is None
    assert mod.classify_ending(b"") is None


def test_find_non_lf_lines_detects_crlf_and_cr():
    mod = load_checker("check_mixed_line_endings")
    data = b"# Title\r\n\nbody\r"
    found = mod.find_non_lf_lines(data)
    assert found == [(1, "CRLF"), (3, "CR")]


def test_lf_only_has_no_findings():
    mod = load_checker("check_mixed_line_endings")
    assert mod.find_non_lf_lines(b"# Title\n\nbody\n") == []


def test_crlf_file_fails(tmp_path, monkeypatch):
    mod = load_checker("check_mixed_line_endings")
    (tmp_path / "doc.md").write_bytes(b"# Title\r\n\r\nbody\r\n")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_cr_file_fails(tmp_path, monkeypatch):
    mod = load_checker("check_mixed_line_endings")
    (tmp_path / "doc.md").write_bytes(b"# Title\r\rbody\r")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_lf_file_passes(tmp_path, monkeypatch):
    mod = load_checker("check_mixed_line_endings")
    (tmp_path / "doc.md").write_bytes(b"# Title\n\nbody\n")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_readme_and_examples_are_lf():
    readme = (ROOT / "README.md").read_bytes()
    sample = (ROOT / "examples" / "sample-docs.md").read_bytes()
    assert b"\r" not in readme
    assert b"\r" not in sample


def test_repo_docs_have_lf_endings():
    mod = load_checker("check_mixed_line_endings")
    assert mod.ROOT == ROOT
    assert mod.main() == 0


def test_check_docs_includes_mixed_line_endings_checker():
    mod = load_checker("check_docs")
    assert "check_mixed_line_endings" in mod.CHECKERS
