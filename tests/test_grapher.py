"""Tests for envctl.grapher."""
from __future__ import annotations

import pytest

from envctl.grapher import build_graph, find_dependents, topological_sort, format_graph_report


class _FakeStore:
    def __init__(self, sets: dict):
        self._sets = sets

    def list_sets(self):
        return list(self._sets.keys())

    def load(self, name):
        return self._sets.get(name)


# ---------------------------------------------------------------------------
# build_graph
# ---------------------------------------------------------------------------

def test_build_graph_no_deps():
    store = _FakeStore({"dev": {"A": "hello", "B": "world"}})
    graph = build_graph(store)
    assert graph == {"dev": set()}


def test_build_graph_detects_cross_ref():
    store = _FakeStore({
        "dev": {"URL": "{{prod:BASE_URL}}/api"},
        "prod": {"BASE_URL": "https://example.com"},
    })
    graph = build_graph(store)
    assert "prod" in graph["dev"]
    assert graph["prod"] == set()


def test_build_graph_ignores_self_ref():
    store = _FakeStore({"dev": {"A": "{{dev:OTHER}}"}})
    graph = build_graph(store)
    assert graph["dev"] == set()


def test_build_graph_multiple_deps():
    store = _FakeStore({
        "ci": {"X": "{{dev:X}}", "Y": "{{staging:Y}}"},
        "dev": {"X": "1"},
        "staging": {"Y": "2"},
    })
    graph = build_graph(store)
    assert graph["ci"] == {"dev", "staging"}


# ---------------------------------------------------------------------------
# find_dependents
# ---------------------------------------------------------------------------

def test_find_dependents_returns_correct_sets():
    graph = {"a": {"b"}, "c": {"b", "d"}, "b": set()}
    result = find_dependents(graph, "b")
    assert sorted(result) == ["a", "c"]


def test_find_dependents_none():
    graph = {"a": set(), "b": set()}
    assert find_dependents(graph, "a") == []


# ---------------------------------------------------------------------------
# topological_sort
# ---------------------------------------------------------------------------

def test_topological_sort_simple_order():
    graph = {"app": {"base"}, "base": set()}
    order = topological_sort(graph)
    assert order.index("base") < order.index("app")


def test_topological_sort_no_deps():
    graph = {"a": set(), "b": set(), "c": set()}
    order = topological_sort(graph)
    assert set(order) == {"a", "b", "c"}


def test_topological_sort_cycle_raises():
    graph = {"a": {"b"}, "b": {"a"}}
    with pytest.raises(ValueError, match="Cyclic"):
        topological_sort(graph)


# ---------------------------------------------------------------------------
# format_graph_report
# ---------------------------------------------------------------------------

def test_format_graph_report_empty():
    assert "No env sets" in format_graph_report({})


def test_format_graph_report_contains_set_names():
    graph = {"dev": {"base"}, "base": set()}
    report = format_graph_report(graph)
    assert "dev" in report
    assert "base" in report


def test_format_graph_report_none_marker():
    graph = {"solo": set()}
    report = format_graph_report(graph)
    assert "(none)" in report
