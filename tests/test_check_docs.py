"""Tests for the unified doc quality entrypoint."""
from __future__ import annotations

from conftest import ROOT, load_checker


def test_check_docs_passes_on_valid_repo():
    mod = load_checker("check_docs")
    assert mod.main() == 0


def test_check_docs_fails_when_any_checker_fails(monkeypatch):
    mod = load_checker("check_docs")

    def fake_run(name: str) -> int:
        return 1 if name == mod.CHECKERS[0] else 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main() == 1


def test_check_docs_runs_all_checkers(monkeypatch):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main() == 0
    assert called == list(mod.CHECKERS)
