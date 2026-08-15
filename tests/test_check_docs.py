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


def test_only_runs_selected_checkers(monkeypatch):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--only", "check_doc_links", "--only", "check_doc_images"]) == 0
    assert called == ["check_doc_links", "check_doc_images"]


def test_only_unknown_checker_exits_2(capsys):
    mod = load_checker("check_docs")
    assert mod.main(["--only", "not_a_real_checker"]) == 2
    err = capsys.readouterr().err
    assert "unknown checker: not_a_real_checker" in err


def test_default_path_unchanged_without_only(monkeypatch):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main([]) == 0
    assert called == list(mod.CHECKERS)


def test_json_summary_all_pass(monkeypatch, capsys):
    mod = load_checker("check_docs")

    def fake_run(name: str) -> int:
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--json"]) == 0
    import json

    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["ok"] is True
    assert payload["failed"] == []
    assert payload["passed"] == list(mod.CHECKERS)


def test_json_summary_reports_failures(monkeypatch, capsys):
    mod = load_checker("check_docs")

    def fake_run(name: str) -> int:
        return 1 if name == "check_doc_links" else 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--json"]) == 1
    import json

    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["ok"] is False
    assert payload["failed"] == ["check_doc_links"]
    assert "check_doc_links" not in payload["passed"]


def test_json_with_only_filter(monkeypatch, capsys):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--json", "--only", "check_doc_links", "--only", "check_doc_images"]) == 0
    import json

    payload = json.loads(capsys.readouterr().out.strip())
    assert called == ["check_doc_links", "check_doc_images"]
    assert payload["passed"] == ["check_doc_links", "check_doc_images"]
    assert payload["failed"] == []
    assert payload["ok"] is True


def test_default_text_mode_unchanged(monkeypatch, capsys):
    mod = load_checker("check_docs")

    def fake_run(name: str) -> int:
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main([]) == 0
    out = capsys.readouterr().out
    assert "ok: all doc quality checks passed" in out
    assert not out.strip().startswith("{")

def test_json_output_is_only_summary_object(capsys):
    mod = load_checker("check_docs")
    assert mod.main(["--json"]) == 0
    import json

    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert payload["ok"] is True
    assert "---" not in out


def test_list_checkers_prints_suite_order(capsys):
    mod = load_checker("check_docs")
    assert mod.main(["--list-checkers"]) == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert out == list(mod.CHECKERS)


def test_list_checkers_skips_running_checkers(monkeypatch, capsys):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--list-checkers", "--only", "check_doc_links", "--json"]) == 0
    assert called == []
    out = capsys.readouterr().out.strip().splitlines()
    assert out == list(mod.CHECKERS)

def test_skip_removes_named_checkers(monkeypatch):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--skip", "check_code_fences"]) == 0
    assert called == [name for name in mod.CHECKERS if name != "check_code_fences"]


def test_skip_is_repeatable(monkeypatch):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--skip", "check_doc_links", "--skip", "check_doc_images"]) == 0
    skipped = {"check_doc_links", "check_doc_images"}
    assert called == [name for name in mod.CHECKERS if name not in skipped]


def test_skip_applied_after_only_preserves_order(monkeypatch):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    rc = mod.main(
        [
            "--only",
            "check_trailing_whitespace",
            "--only",
            "check_doc_links",
            "--only",
            "check_doc_images",
            "--skip",
            "check_doc_links",
        ]
    )
    assert rc == 0
    assert called == ["check_doc_images", "check_trailing_whitespace"]


def test_skip_unknown_checker_exits_2(capsys):
    mod = load_checker("check_docs")
    assert mod.main(["--skip", "not_a_real_checker"]) == 2
    err = capsys.readouterr().err
    assert "unknown checker: not_a_real_checker" in err


def test_default_path_unchanged_without_skip(monkeypatch):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main([]) == 0
    assert called == list(mod.CHECKERS)


def test_list_checkers_ignores_skip(monkeypatch, capsys):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--list-checkers", "--skip", "check_doc_links"]) == 0
    assert called == []
    out = capsys.readouterr().out.strip().splitlines()
    assert out == list(mod.CHECKERS)


def test_fail_fast_stops_after_first_failure(monkeypatch):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 1 if name == mod.CHECKERS[1] else 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--fail-fast"]) == 1
    assert called == list(mod.CHECKERS[:2])


def test_without_fail_fast_runs_full_suite_after_failure(monkeypatch):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 1 if name == mod.CHECKERS[0] else 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main([]) == 1
    assert called == list(mod.CHECKERS)


def test_fail_fast_all_pass_runs_full_suite(monkeypatch):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--fail-fast"]) == 0
    assert called == list(mod.CHECKERS)


def test_list_checkers_ignores_fail_fast(monkeypatch, capsys):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--list-checkers", "--fail-fast"]) == 0
    assert called == []
    out = capsys.readouterr().out.strip().splitlines()
    assert out == list(mod.CHECKERS)


def test_fail_fast_unknown_checker_exits_2(capsys):
    mod = load_checker("check_docs")
    assert mod.main(["--fail-fast", "--only", "not_a_real_checker"]) == 2
    err = capsys.readouterr().err
    assert "unknown checker: not_a_real_checker" in err


def test_fail_fast_unknown_skip_exits_2(capsys):
    mod = load_checker("check_docs")
    assert mod.main(["--fail-fast", "--skip", "not_a_real_checker"]) == 2
    err = capsys.readouterr().err
    assert "unknown checker: not_a_real_checker" in err


def test_version_prints_package_version(capsys):
    mod = load_checker("check_docs")
    assert mod.main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == "0.1.0"


def test_version_skips_running_checkers(monkeypatch, capsys):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--version"]) == 0
    assert called == []
    assert capsys.readouterr().out.strip() == "0.1.0"


def test_version_matches_pyproject():
    mod = load_checker("check_docs")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version_line = next(
        line for line in pyproject.splitlines() if line.startswith("version = ")
    )
    assert mod.VERSION == version_line.split("=", 1)[1].strip().strip('"')


def test_list_checkers_ignores_version_flag_order(monkeypatch, capsys):
    """--version takes precedence when both are passed (early return)."""
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--list-checkers", "--version"]) == 0
    assert called == []
    assert capsys.readouterr().out.strip() == "0.1.0"


def test_quiet_suppresses_banners(monkeypatch, capsys):
    mod = load_checker("check_docs")

    def fake_run(name: str) -> int:
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--quiet"]) == 0
    out = capsys.readouterr().out
    assert "---" not in out
    assert "ok: all doc quality checks passed" in out


def test_default_prints_banners(monkeypatch, capsys):
    mod = load_checker("check_docs")

    def fake_run(name: str) -> int:
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main([]) == 0
    out = capsys.readouterr().out
    assert f"--- {mod.CHECKERS[0]} ---" in out
    assert "ok: all doc quality checks passed" in out


def test_quiet_still_runs_all_checkers(monkeypatch):
    mod = load_checker("check_docs")
    called: list[str] = []

    def fake_run(name: str) -> int:
        called.append(name)
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--quiet"]) == 0
    assert called == list(mod.CHECKERS)


def test_quiet_with_json_unchanged(monkeypatch, capsys):
    mod = load_checker("check_docs")

    def fake_run(name: str) -> int:
        return 0

    monkeypatch.setattr(mod, "run_checker", fake_run)
    assert mod.main(["--quiet", "--json"]) == 0
    import json

    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert payload["ok"] is True
    assert "---" not in out

