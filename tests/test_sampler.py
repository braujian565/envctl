"""Tests for envctl.sampler."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from envctl.sampler import (
    sample_keys,
    sample_set,
    sample_all,
    format_sample_report,
)


ENV = {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"}


def _mock_store(sets: dict):
    store = MagicMock()
    store.list_sets.return_value = list(sets.keys())
    store.load.side_effect = lambda name: sets.get(name)
    return store


def test_sample_keys_returns_requested_count():
    result = sample_keys(ENV, 3, seed=0)
    assert len(result) == 3


def test_sample_keys_all_keys_are_valid():
    result = sample_keys(ENV, 3, seed=42)
    for k in result:
        assert k in ENV


def test_sample_keys_values_match_original():
    result = sample_keys(ENV, 3, seed=7)
    for k, v in result.items():
        assert ENV[k] == v


def test_sample_keys_n_exceeds_size_returns_all():
    result = sample_keys(ENV, 100, seed=0)
    assert result == ENV


def test_sample_keys_zero_returns_empty():
    result = sample_keys(ENV, 0)
    assert result == {}


def test_sample_keys_deterministic_with_seed():
    r1 = sample_keys(ENV, 3, seed=99)
    r2 = sample_keys(ENV, 3, seed=99)
    assert r1 == r2


def test_sample_keys_different_seeds_may_differ():
    r1 = sample_keys(ENV, 2, seed=1)
    r2 = sample_keys(ENV, 2, seed=2)
    # Not guaranteed but extremely likely with 5 keys
    # Just ensure both are valid subsets
    assert set(r1).issubset(ENV)
    assert set(r2).issubset(ENV)


def test_sample_set_returns_correct_keys():
    store = _mock_store({"prod": ENV})
    result = sample_set(store, "prod", 2, seed=0)
    assert len(result) == 2
    assert all(k in ENV for k in result)


def test_sample_set_missing_raises():
    store = _mock_store({})
    store.load.return_value = None
    with pytest.raises(KeyError, match="not found"):
        sample_set(store, "ghost", 2)


def test_sample_all_covers_all_sets():
    store = _mock_store({"dev": {"X": "1"}, "prod": {"Y": "2"}})
    result = sample_all(store, 1, seed=0)
    assert set(result.keys()) == {"dev", "prod"}


def test_sample_all_respects_n():
    store = _mock_store({"dev": ENV, "prod": ENV})
    result = sample_all(store, 2, seed=0)
    for samples in result.values():
        assert len(samples) <= 2


def test_format_sample_report_contains_set_name():
    report = format_sample_report({"A": "1"}, "staging")
    assert "staging" in report


def test_format_sample_report_contains_keys():
    report = format_sample_report({"FOO": "bar"}, "dev")
    assert "FOO=bar" in report


def test_format_sample_report_empty():
    report = format_sample_report({}, "dev")
    assert "no keys sampled" in report
