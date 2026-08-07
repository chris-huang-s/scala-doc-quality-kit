"""Tests for Scala fence info-string policy."""
from __future__ import annotations

from pathlib import Path

from conftest import load_checker

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_scala_fence_passes(tmp_path, monkeypatch):
    mod = load_checker("check_scala_fences")
    (tmp_path / "doc.md").write_text(
        "# Doc\n\n```scala\nval x = 1\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_scala_mdoc_fence_passes(tmp_path, monkeypatch):
    mod = load_checker("check_scala_fences")
    (tmp_path / "doc.md").write_text(
        "# Doc\n\n```scala mdoc\nval x = 1\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_mdoc_without_scala_prefix_fails(tmp_path, monkeypatch):
    mod = load_checker("check_scala_fences")
    (tmp_path / "doc.md").write_text(
        "# Doc\n\n```mdoc\nobject Bad\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_non_scala_fence_is_ignored(tmp_path, monkeypatch):
    mod = load_checker("check_scala_fences")
    (tmp_path / "doc.md").write_text(
        "# Doc\n\n```python\nprint('ok')\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0


def test_fixture_mdoc_without_scala_is_invalid(tmp_path, monkeypatch):
    mod = load_checker("check_scala_fences")
    (tmp_path / "doc.md").write_text(
        (FIXTURES / "mdoc-without-scala.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 1


def test_examples_pass_scala_fence_check():
    mod = load_checker("check_scala_fences")
    assert mod.main() == 0


def test_rule_toggle_can_disable_scala_fence_check(tmp_path, monkeypatch):
    mod = load_checker("check_scala_fences")
    (tmp_path / "doc.md").write_text(
        "# Doc\n\n```mdoc\nobject Bad\n```\n",
        encoding="utf-8",
    )
    (tmp_path / ".doc-quality.json").write_text(
        '{"version": 1, "paths": ["."], "rules": {"require_scala_fence_info": false}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    assert mod.main() == 0
