"""Tests for envctl.weigher."""

from __future__ import annotations

import pytest

from envctl.weigher import (
    weigh_env_set,
    weigh_all,
    format_weight_report,
    _count_prefixes,
)


# ---------------------------------------------------------------------------
# _count_prefixes
# ---------------------------------------------------------------------------

def test_count_prefixes_no_prefix():
    env = {"FOO": "1", "BAR": "2"}
    assert _count_prefixes(env) == 0


def test_count_prefixes_single():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert _count_prefixes(env) == 1


def test_count_prefixes_multiple():
    env = {"DB_HOST": "h", "APP_ENV": "prod", "AWS_KEY": "k"}
    assert _count_prefixes(env) == 3


def test_count_prefixes_deduplicates():
    env = {"APP_A": "1", "APP_B": "2", "DB_X": "3"}
    assert _count_prefixes(env) == 2


# ---------------------------------------------------------------------------
# weigh_env_set
# ---------------------------------------------------------------------------

def test_weigh_empty_env():
    report = weigh_env_set("empty", {})
    assert report["name"] == "empty"
    assert report["key_count"] == 0
    assert report["total_value_len"] == 0
    assert report["sensitive_count"] == 0
    assert report["prefix_count"] == 0
    assert report["weight"] == 0


def test_weigh_counts_keys():
    env = {"A": "1", "B": "2", "C": "3"}
    report = weigh_env_set("s", env)
    assert report["key_count"] == 3


def test_weigh_total_value_len():
    env = {"K": "hello"}  # len 5
    report = weigh_env_set("s", env)
    assert report["total_value_len"] == 5


def test_weigh_sensitive_counted():
    env = {"API_KEY": "secret123", "HOST": "localhost"}
    report = weigh_env_set("s", env)
    assert report["sensitive_count"] >= 1


def test_weigh_composite_weight_increases_with_more_keys():
    small = weigh_env_set("s", {"A": "1"})
    large = weigh_env_set("l", {"A": "1", "B": "2", "C": "3"})
    assert large["weight"] > small["weight"]


# ---------------------------------------------------------------------------
# weigh_all
# ---------------------------------------------------------------------------

class _FakeStore:
    def __init__(self, data):
        self._data = data

    def list_sets(self):
        return list(self._data.keys())

    def load(self, name):
        return self._data.get(name, {})


def test_weigh_all_returns_all_sets():
    store = _FakeStore({"dev": {"A": "1"}, "prod": {"A": "1", "B": "2"}})
    reports = weigh_all(store)
    names = {r["name"] for r in reports}
    assert names == {"dev", "prod"}


def test_weigh_all_sorted_heaviest_first():
    store = _FakeStore({
        "light": {"X": "1"},
        "heavy": {"A": "1", "B": "2", "C": "3", "D": "4"},
    })
    reports = weigh_all(store)
    assert reports[0]["name"] == "heavy"


# ---------------------------------------------------------------------------
# format_weight_report
# ---------------------------------------------------------------------------

def test_format_weight_report_contains_name():
    report = weigh_env_set("myenv", {"K": "v"})
    text = format_weight_report(report)
    assert "myenv" in text


def test_format_weight_report_contains_weight_label():
    report = weigh_env_set("x", {})
    text = format_weight_report(report)
    assert "Weight score" in text
