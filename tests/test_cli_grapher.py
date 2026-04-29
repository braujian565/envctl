"""Tests for envctl.cli_grapher."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envctl.cli_grapher import graph_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_store(monkeypatch):
    """Patch EnvStore so CLI tests don't touch the filesystem."""
    sets = {
        "dev": {"API_URL": "{{base:API_URL}}", "DEBUG": "true"},
        "base": {"API_URL": "https://api.example.com"},
        "staging": {"API_URL": "{{base:API_URL}}", "STAGE": "1"},
    }

    class _Store:
        def __init__(self, *a, **kw):
            pass

        def list_sets(self):
            return list(sets.keys())

        def load(self, name):
            return sets.get(name)

    monkeypatch.setattr("envctl.cli_grapher.EnvStore", _Store)
    return sets


def invoke(runner, *args):
    return runner.invoke(graph_group, list(args), catch_exceptions=False)


def test_show_prints_graph(runner, mock_store):
    result = invoke(runner, "show")
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "base" in result.output


def test_deps_known_set(runner, mock_store):
    result = invoke(runner, "deps", "dev")
    assert result.exit_code == 0
    assert "base" in result.output


def test_deps_no_dependencies(runner, mock_store):
    result = invoke(runner, "deps", "base")
    assert result.exit_code == 0
    assert "no dependencies" in result.output


def test_deps_unknown_set_exits_nonzero(runner, mock_store):
    result = runner.invoke(graph_group, ["deps", "nonexistent"], catch_exceptions=False)
    assert result.exit_code != 0


def test_dependents_lists_sets(runner, mock_store):
    result = invoke(runner, "dependents", "base")
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "staging" in result.output


def test_dependents_none(runner, mock_store):
    result = invoke(runner, "dependents", "staging")
    assert result.exit_code == 0
    assert "No sets depend on" in result.output


def test_order_lists_all_sets(runner, mock_store):
    result = invoke(runner, "order")
    assert result.exit_code == 0
    assert "base" in result.output
    assert "dev" in result.output
    assert "staging" in result.output


def test_order_base_before_dev(runner, mock_store):
    result = invoke(runner, "order")
    assert result.output.index("base") < result.output.index("dev")
