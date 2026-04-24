"""Tests for envctl.flattener."""
from __future__ import annotations

import pytest

from envctl.flattener import flatten_sets, unflatten_set, format_flat_report


class _FakeStore:
    """Minimal store stub for testing."""

    def __init__(self, data: dict[str, dict[str, str]]):
        self._data = data

    def load(self, name: str):
        return self._data.get(name)


@pytest.fixture()
def store():
    return _FakeStore(
        {
            "dev": {"DB_HOST": "localhost", "DB_PORT": "5432"},
            "prod": {"DB_HOST": "prod.db", "API_KEY": "secret"},
        }
    )


# ---------------------------------------------------------------------------
# flatten_sets
# ---------------------------------------------------------------------------

def test_flatten_sets_prefixes_keys(store):
    result = flatten_sets(store, ["dev"], prefix_with_name=True)
    assert "DEV_DB_HOST" in result
    assert result["DEV_DB_HOST"] == "localhost"


def test_flatten_sets_multiple_sets(store):
    result = flatten_sets(store, ["dev", "prod"], prefix_with_name=True)
    assert "DEV_DB_HOST" in result
    assert "PROD_DB_HOST" in result
    assert "PROD_API_KEY" in result


def test_flatten_sets_no_prefix_later_wins(store):
    result = flatten_sets(store, ["dev", "prod"], prefix_with_name=False)
    # prod is loaded second, so its DB_HOST wins
    assert result["DB_HOST"] == "prod.db"
    assert result["API_KEY"] == "secret"


def test_flatten_sets_missing_set_raises(store):
    with pytest.raises(KeyError, match="nonexistent"):
        flatten_sets(store, ["nonexistent"])


def test_flatten_sets_custom_separator(store):
    result = flatten_sets(store, ["dev"], separator="__", prefix_with_name=True)
    assert "DEV__DB_HOST" in result


def test_flatten_sets_empty_list(store):
    result = flatten_sets(store, [])
    assert result == {}


# ---------------------------------------------------------------------------
# unflatten_set
# ---------------------------------------------------------------------------

def test_unflatten_set_splits_by_prefix():
    flat = {"DEV_DB_HOST": "localhost", "PROD_DB_HOST": "prod.db"}
    groups = unflatten_set(flat, known_prefixes=["dev", "prod"])
    assert groups["dev"]["DB_HOST"] == "localhost"
    assert groups["prod"]["DB_HOST"] == "prod.db"


def test_unflatten_set_unknown_keys_go_to_root():
    flat = {"ORPHAN_KEY": "value"}
    groups = unflatten_set(flat, known_prefixes=["dev"])
    assert "__root__" in groups
    assert groups["__root__"]["ORPHAN_KEY"] == "value"


def test_unflatten_set_no_prefixes_all_root():
    flat = {"FOO": "bar", "BAZ": "qux"}
    groups = unflatten_set(flat)
    assert groups["__root__"] == {"FOO": "bar", "BAZ": "qux"}


# ---------------------------------------------------------------------------
# format_flat_report
# ---------------------------------------------------------------------------

def test_format_flat_report_empty():
    assert format_flat_report({}) == "(empty)"


def test_format_flat_report_sorted():
    flat = {"Z_KEY": "z", "A_KEY": "a"}
    report = format_flat_report(flat)
    lines = report.splitlines()
    assert lines[0].startswith("A_KEY")
    assert lines[1].startswith("Z_KEY")


def test_format_flat_report_format():
    flat = {"DB_HOST": "localhost"}
    assert format_flat_report(flat) == "DB_HOST=localhost"
