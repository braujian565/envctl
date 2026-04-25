"""Tests for envctl.inspector."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from envctl.inspector import format_inspection_report, inspect_set
from click.testing import CliRunner
from envctl.cli_inspector import inspect_group


# ---------------------------------------------------------------------------
# Unit tests for inspect_set
# ---------------------------------------------------------------------------

def test_inspect_set_returns_name():
    report = inspect_set("dev", {"HOST": "localhost", "PORT": "8080"})
    assert report["name"] == "dev"


def test_inspect_set_counts_total_keys():
    env = {"A": "1", "B": "2", "C": "3"}
    report = inspect_set("x", env)
    assert report["total_keys"] == 3


def test_inspect_set_detects_empty_keys():
    env = {"PRESENT": "yes", "MISSING": ""}
    report = inspect_set("x", env)
    assert "MISSING" in report["empty_keys"]
    assert "PRESENT" not in report["empty_keys"]


def test_inspect_set_no_empty_keys():
    env = {"A": "1", "B": "2"}
    report = inspect_set("x", env)
    assert report["empty_keys"] == []


def test_inspect_set_detects_sensitive_keys():
    env = {"API_KEY": "secret123", "HOST": "localhost"}
    report = inspect_set("x", env)
    assert "API_KEY" in report["sensitive_keys"]


def test_inspect_set_has_score_and_grade():
    env = {"HOST": "localhost", "PORT": "8080"}
    report = inspect_set("x", env)
    assert isinstance(report["score"], (int, float))
    assert report["grade"] in {"A", "B", "C", "D", "F"}


def test_inspect_set_has_categories_list():
    env = {"DB_HOST": "localhost"}
    report = inspect_set("x", env)
    assert isinstance(report["categories"], list)


def test_inspect_set_has_risk_counts_dict():
    env = {"HOST": "localhost"}
    report = inspect_set("x", env)
    assert isinstance(report["risk_counts"], dict)


def test_inspect_set_empty_env():
    report = inspect_set("empty", {})
    assert report["total_keys"] == 0
    assert report["empty_keys"] == []
    assert report["sensitive_keys"] == []


# ---------------------------------------------------------------------------
# Unit tests for format_inspection_report
# ---------------------------------------------------------------------------

def test_format_report_contains_name():
    report = inspect_set("myenv", {"KEY": "val"})
    text = format_inspection_report(report)
    assert "myenv" in text


def test_format_report_shows_total_keys():
    report = inspect_set("x", {"A": "1", "B": "2"})
    text = format_inspection_report(report)
    assert "2" in text


def test_format_report_shows_none_for_empty_sensitive():
    report = inspect_set("x", {"HOST": "localhost"})
    text = format_inspection_report(report)
    assert "none" in text


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_store(tmp_path, monkeypatch):
    store = MagicMock()
    store.load.return_value = {"HOST": "localhost", "PORT": "5432"}
    store.list_sets.return_value = ["dev", "prod"]
    monkeypatch.setattr("envctl.cli_inspector.EnvStore", lambda *a, **kw: store)
    return store


def test_show_set_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = runner.invoke(inspect_group, ["show", "ghost"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_show_text_output(runner, mock_store):
    result = runner.invoke(inspect_group, ["show", "dev"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "Total keys" in result.output


def test_show_json_output(runner, mock_store):
    import json as _json
    result = runner.invoke(inspect_group, ["show", "dev", "--format", "json"])
    assert result.exit_code == 0
    data = _json.loads(result.output)
    assert data["name"] == "dev"
    assert "total_keys" in data


def test_inspect_all_iterates_sets(runner, mock_store):
    result = runner.invoke(inspect_group, ["all"])
    assert result.exit_code == 0
    assert mock_store.list_sets.called


def test_inspect_all_empty_store(runner, mock_store):
    mock_store.list_sets.return_value = []
    result = runner.invoke(inspect_group, ["all"])
    assert result.exit_code == 0
    assert "No env sets found" in result.output
