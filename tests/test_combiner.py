"""Tests for envctl.combiner."""
import pytest

from envctl.combiner import (
    combine_sets,
    combine_from_store,
    format_combine_report,
)


# ---------------------------------------------------------------------------
# combine_sets – union
# ---------------------------------------------------------------------------

def test_combine_union_merges_all_keys():
    a = {"FOO": "1", "BAR": "2"}
    b = {"BAZ": "3"}
    result = combine_sets([a, b], strategy="union")
    assert result == {"FOO": "1", "BAR": "2", "BAZ": "3"}


def test_combine_union_later_wins_by_default():
    a = {"KEY": "old"}
    b = {"KEY": "new"}
    result = combine_sets([a, b], strategy="union")
    assert result["KEY"] == "new"


def test_combine_union_no_overwrite_first_wins():
    a = {"KEY": "first"}
    b = {"KEY": "second"}
    result = combine_sets([a, b], strategy="union", overwrite=False)
    assert result["KEY"] == "first"


def test_combine_union_empty_list_returns_empty():
    assert combine_sets([], strategy="union") == {}


# ---------------------------------------------------------------------------
# combine_sets – intersection
# ---------------------------------------------------------------------------

def test_combine_intersection_keeps_common_keys_only():
    a = {"FOO": "1", "SHARED": "a"}
    b = {"BAR": "2", "SHARED": "b"}
    result = combine_sets([a, b], strategy="intersection")
    assert set(result.keys()) == {"SHARED"}


def test_combine_intersection_later_wins():
    a = {"SHARED": "first"}
    b = {"SHARED": "second"}
    result = combine_sets([a, b], strategy="intersection", overwrite=True)
    assert result["SHARED"] == "second"


def test_combine_intersection_no_common_keys_returns_empty():
    a = {"FOO": "1"}
    b = {"BAR": "2"}
    result = combine_sets([a, b], strategy="intersection")
    assert result == {}


def test_combine_intersection_three_sets():
    a = {"X": "1", "Y": "2"}
    b = {"X": "3", "Y": "4", "Z": "5"}
    c = {"X": "6", "Z": "7"}
    result = combine_sets([a, b, c], strategy="intersection")
    assert set(result.keys()) == {"X"}


# ---------------------------------------------------------------------------
# combine_from_store
# ---------------------------------------------------------------------------

class _FakeStore:
    def __init__(self, data):
        self._data = data

    def load(self, name):
        return self._data.get(name)

    def list_sets(self):
        return list(self._data.keys())


def test_combine_from_store_loads_and_merges():
    store = _FakeStore({"dev": {"A": "1"}, "prod": {"B": "2"}})
    result = combine_from_store(store, ["dev", "prod"])
    assert result == {"A": "1", "B": "2"}


def test_combine_from_store_missing_set_raises():
    store = _FakeStore({"dev": {"A": "1"}})
    with pytest.raises(KeyError, match="missing"):
        combine_from_store(store, ["dev", "missing"])


# ---------------------------------------------------------------------------
# format_combine_report
# ---------------------------------------------------------------------------

def test_format_combine_report_contains_strategy():
    report = format_combine_report({"FOO": "bar"}, ["a", "b"], "union")
    assert "union" in report


def test_format_combine_report_contains_key_count():
    result = {"A": "1", "B": "2"}
    report = format_combine_report(result, ["x"], "intersection")
    assert "2 key" in report


def test_format_combine_report_lists_keys():
    result = {"MY_KEY": "hello"}
    report = format_combine_report(result, ["s"], "union")
    assert "MY_KEY=hello" in report
