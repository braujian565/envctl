"""Tests for envctl.differ module."""
import pytest
from unittest.mock import MagicMock
from envctl.differ import diff_sets, format_diff


@pytest.fixture
def mock_store():
    store = MagicMock()
    return store


def _make_store(a_vars, b_vars):
    store = MagicMock()
    store.load.side_effect = lambda name: {"set_a": a_vars, "set_b": b_vars}.get(name)
    return store


def test_diff_added():
    store = _make_store({"FOO": "1"}, {"FOO": "1", "BAR": "2"})
    diff = diff_sets(store, "set_a", "set_b")
    assert diff["added"] == {"BAR": "2"}
    assert diff["removed"] == {}
    assert diff["changed"] == {}


def test_diff_removed():
    store = _make_store({"FOO": "1", "BAR": "2"}, {"FOO": "1"})
    diff = diff_sets(store, "set_a", "set_b")
    assert diff["removed"] == {"BAR": "2"}
    assert diff["added"] == {}


def test_diff_changed():
    store = _make_store({"FOO": "old"}, {"FOO": "new"})
    diff = diff_sets(store, "set_a", "set_b")
    assert diff["changed"] == {"FOO": {"from": "old", "to": "new"}}


def test_diff_unchanged():
    store = _make_store({"FOO": "same"}, {"FOO": "same"})
    diff = diff_sets(store, "set_a", "set_b")
    assert diff["unchanged"] == {"FOO": "same"}
    assert diff["added"] == {}
    assert diff["removed"] == {}
    assert diff["changed"] == {}


def test_diff_empty_sets():
    store = _make_store({}, {})
    diff = diff_sets(store, "set_a", "set_b")
    assert all(len(v) == 0 for v in diff.values())


def test_diff_nonexistent_set_treated_as_empty():
    store = MagicMock()
    store.load.return_value = None
    diff = diff_sets(store, "missing_a", "missing_b")
    assert diff["added"] == {}


def test_format_diff_no_color_added():
    diff = {"added": {"X": "1"}, "removed": {}, "changed": {}, "unchanged": {}}
    out = format_diff(diff, color=False)
    assert "+ X=1" in out


def test_format_diff_no_color_removed():
    diff = {"added": {}, "removed": {"Y": "2"}, "changed": {}, "unchanged": {}}
    out = format_diff(diff, color=False)
    assert "- Y=2" in out


def test_format_diff_no_differences():
    diff = {"added": {}, "removed": {}, "changed": {}, "unchanged": {"A": "1"}}
    out = format_diff(diff, color=False)
    assert out == "No differences found."
