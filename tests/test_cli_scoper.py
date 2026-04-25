"""Tests for envctl.cli_scoper."""
from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch

from envctl.cli_scoper import scope_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def scope_file(tmp_path: Path) -> Path:
    return tmp_path / "scopes.json"


def invoke(runner: CliRunner, scope_file: Path, *args: str):
    with patch("envctl.scoper._SCOPE_FILE", scope_file):
        with patch("envctl.cli_scoper.set_scope", wraps=_make_patched_set_scope(scope_file)):
            pass
    return runner.invoke(scope_group, list(args), catch_exceptions=False)


def _make_patched_set_scope(scope_file: Path):
    from envctl import scoper
    def _patched(set_name, scope, path=None):
        return scoper.set_scope(set_name, scope, scope_file)
    return _patched


def _run(runner: CliRunner, scope_file: Path, *args: str):
    """Invoke CLI with patched scope file."""
    import envctl.scoper as scoper_mod
    import envctl.cli_scoper as cli_mod

    originals = {
        fn: getattr(cli_mod, fn)
        for fn in ("set_scope", "get_scope", "remove_scope", "list_scopes", "find_by_scope")
    }
    for fn_name in originals:
        orig = getattr(scoper_mod, fn_name)
        def _wrap(orig=orig):
            def _inner(*a, **kw):
                kw.setdefault("path", scope_file)
                return orig(*a, **kw)
            return _inner
        setattr(cli_mod, fn_name, _wrap())

    result = runner.invoke(scope_group, list(args), catch_exceptions=False)

    for fn_name, orig_fn in originals.items():
        setattr(cli_mod, fn_name, orig_fn)
    return result


def test_set_scope_success(runner: CliRunner, scope_file: Path) -> None:
    result = _run(runner, scope_file, "set", "myapp", "local")
    assert result.exit_code == 0
    assert "local" in result.output
    assert "myapp" in result.output


def test_get_scope_found(runner: CliRunner, scope_file: Path) -> None:
    _run(runner, scope_file, "set", "myapp", "team")
    result = _run(runner, scope_file, "get", "myapp")
    assert result.exit_code == 0
    assert "team" in result.output


def test_get_scope_not_found(runner: CliRunner, scope_file: Path) -> None:
    result = _run(runner, scope_file, "get", "ghost")
    assert result.exit_code == 0
    assert "No scope" in result.output


def test_remove_scope_found(runner: CliRunner, scope_file: Path) -> None:
    _run(runner, scope_file, "set", "myapp", "global")
    result = _run(runner, scope_file, "remove", "myapp")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_scopes_empty(runner: CliRunner, scope_file: Path) -> None:
    result = _run(runner, scope_file, "list")
    assert result.exit_code == 0
    assert "No scopes" in result.output


def test_find_by_scope_shows_sets(runner: CliRunner, scope_file: Path) -> None:
    _run(runner, scope_file, "set", "alpha", "project")
    _run(runner, scope_file, "set", "beta", "project")
    result = _run(runner, scope_file, "find", "project")
    assert "alpha" in result.output
    assert "beta" in result.output
