"""Tests for H1 and heading spacing checkers."""
from __future__ import annotations

from conftest import ROOT, load_checker


def test_count_h1_ignores_fenced_headings():
    mod = load_checker("check_single_h1")
    text = "# Real title\n\n```\n# not a heading\n```\n"
    assert mod.count_h1(text) == 1


def test_wrong_h1_count_fails(tmp_path, monkeypatch):
    mod = load_checker("check_single_h1")
    (tmp_path / "doc.md").write_text("# One\n# Two\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_single_h1_passes(tmp_path, monkeypatch):
    mod = load_checker("check_single_h1")
    (tmp_path / "doc.md").write_text("# Title\n\n## Section\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_missing_blank_before_heading_fails(tmp_path, monkeypatch):
    mod = load_checker("check_heading_spacing")
    (tmp_path / "doc.md").write_text(
        "# Title\n## No blank\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_blank_line_before_heading_passes(tmp_path, monkeypatch):
    mod = load_checker("check_heading_spacing")
    (tmp_path / "doc.md").write_text(
        "# Title\n\n## Section\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_examples_pass_heading_checks():
    h1 = load_checker("check_single_h1")
    spacing = load_checker("check_heading_spacing")
    assert h1.main() == 0
    assert spacing.main() == 0


def test_heading_slug_normalizes_formatting():
    from doc_quality.markdown import heading_slug

    assert heading_slug("  Hello, *Scala* Docs!  ") == "hello-scala-docs"


def test_heading_slug_collapses_whitespace_and_symbols():
    from doc_quality.markdown import heading_slug

    assert heading_slug("API   v2 / reference") == "api-v2-reference"


def test_iter_headings_yields_level_text_and_line_no():
    from doc_quality.markdown import iter_headings

    text = "# Title\n\n## Section\n### Detail\n"
    assert list(iter_headings(text)) == [
        (1, "Title", 1),
        (2, "Section", 3),
        (3, "Detail", 4),
    ]


def test_iter_headings_skips_headings_inside_fences():
    from doc_quality.markdown import iter_headings

    text = "# Real\n\n```text\n# Fake\n```\n\n## Outside\n"
    assert list(iter_headings(text)) == [
        (1, "Real", 1),
        (2, "Outside", 7),
    ]

