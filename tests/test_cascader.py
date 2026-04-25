"""Tests for envctl.cascader."""
import pytest
from envctl.cascader import (
    cascade_sets,
    cascade_from_store,
    explain_cascade,
    format_cascade_report,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _FakeStore:
    def __init__(self, data):
        self._data = data

    def load(self, name):
        return self._data.get(name)


# ---------------------------------------------------------------------------
# cascade_sets
# ---------------------------------------------------------------------------

def test_cascade_sets_later_wins():
    base = ("base", {"A": "1", "B": "2"})
    override = ("override", {"B": "99", "C": "3"})
    result = cascade_sets([base, override])
    assert result == {"A": "1", "B": "99", "C": "3"}


def test_cascade_sets_no_overwrite_first_wins():
    base = ("base", {"A": "1", "B": "2"})
    override = ("override", {"B": "99", "C": "3"})
    result = cascade_sets([base, override], overwrite=False)
    assert result["B"] == "2"  # first definition wins
    assert result["C"] == "3"


def test_cascade_sets_empty_list():
    assert cascade_sets([]) == {}


def test_cascade_sets_single_set():
    result = cascade_sets([("only", {"X": "hello"})])
    assert result == {"X": "hello"}


# ---------------------------------------------------------------------------
# cascade_from_store
# ---------------------------------------------------------------------------

def test_cascade_from_store_merges_correctly():
    store = _FakeStore({"dev": {"DB": "dev-db"}, "local": {"DB": "local-db", "PORT": "5432"}})
    result = cascade_from_store(store, ["dev", "local"])
    assert result["DB"] == "local-db"
    assert result["PORT"] == "5432"


def test_cascade_from_store_missing_set_raises():
    store = _FakeStore({})
    with pytest.raises(KeyError, match="missing"):
        cascade_from_store(store, ["missing"])


# ---------------------------------------------------------------------------
# explain_cascade
# ---------------------------------------------------------------------------

def test_explain_cascade_attributes_source():
    layers = [("base", {"A": "1"}), ("top", {"A": "2", "B": "3"})]
    exp = explain_cascade(layers)
    assert exp["A"] == ("top", "2")
    assert exp["B"] == ("top", "3")


def test_explain_cascade_no_overwrite():
    layers = [("base", {"A": "1"}), ("top", {"A": "2"})]
    exp = explain_cascade(layers, overwrite=False)
    assert exp["A"] == ("base", "1")


# ---------------------------------------------------------------------------
# format_cascade_report
# ---------------------------------------------------------------------------

def test_format_cascade_report_empty():
    assert format_cascade_report({}) == "(no keys)"


def test_format_cascade_report_contains_key_and_source():
    exp = {"DB_URL": ("prod", "postgres://localhost/mydb")}
    report = format_cascade_report(exp)
    assert "DB_URL" in report
    assert "prod" in report
