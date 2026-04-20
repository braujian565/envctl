"""Tests for envctl/aliaser.py."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envctl.aliaser import add_alias, list_aliases, remove_alias, resolve_alias
from envctl.cli_aliaser import alias_group


@pytest.fixture()
def alias_file(tmp_path):
    return tmp_path / "aliases.json"


# ---------- unit tests ----------

def test_list_aliases_empty_when_no_file(alias_file):
    assert list_aliases(alias_file) == []


def test_add_alias_returns_entry(alias_file):
    entry = add_alias("prod", "production", alias_file)
    assert entry == {"alias": "prod", "set": "production"}


def test_add_alias_persisted(alias_file):
    add_alias("dev", "development", alias_file)
    assert list_aliases(alias_file) == [{"alias": "dev", "set": "development"}]


def test_add_alias_overwrites(alias_file):
    add_alias("stg", "staging-old", alias_file)
    add_alias("stg", "staging-new", alias_file)
    assert resolve_alias("stg", alias_file) == "staging-new"


def test_resolve_alias_returns_none_for_unknown(alias_file):
    assert resolve_alias("ghost", alias_file) is None


def test_remove_alias_existing(alias_file):
    add_alias("tmp", "temporary", alias_file)
    assert remove_alias("tmp", alias_file) is True
    assert resolve_alias("tmp", alias_file) is None


def test_remove_alias_nonexistent(alias_file):
    assert remove_alias("nope", alias_file) is False


def test_list_aliases_multiple(alias_file):
    add_alias("a", "alpha", alias_file)
    add_alias("b", "beta", alias_file)
    names = {e["alias"] for e in list_aliases(alias_file)}
    assert names == {"a", "b"}


# ---------- CLI tests ----------

@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner, alias_file, *args):
    from unittest.mock import patch
    with patch("envctl.aliaser._ALIAS_FILE", alias_file), \
         patch("envctl.cli_aliaser.add_alias",
               lambda a, s, path=None: add_alias(a, s, alias_file)), \
         patch("envctl.cli_aliaser.remove_alias",
               lambda a, path=None: remove_alias(a, alias_file)), \
         patch("envctl.cli_aliaser.resolve_alias",
               lambda a, path=None: resolve_alias(a, alias_file)), \
         patch("envctl.cli_aliaser.list_aliases",
               lambda path=None: list_aliases(alias_file)):
        return runner.invoke(alias_group, list(args), catch_exceptions=False)


def test_cli_add_success(runner, alias_file):
    result = _invoke(runner, alias_file, "add", "p", "production")
    assert result.exit_code == 0
    assert "p" in result.output


def test_cli_resolve_found(runner, alias_file):
    add_alias("x", "xray", alias_file)
    result = _invoke(runner, alias_file, "resolve", "x")
    assert result.exit_code == 0
    assert "xray" in result.output


def test_cli_resolve_not_found(runner, alias_file):
    result = _invoke(runner, alias_file, "resolve", "missing")
    assert result.exit_code != 0


def test_cli_list_empty(runner, alias_file):
    result = _invoke(runner, alias_file, "list")
    assert "No aliases" in result.output
