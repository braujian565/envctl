"""Tests for envctl.fingerprinter."""

import pytest
from unittest.mock import MagicMock
from envctl.fingerprinter import (
    fingerprint_env_set,
    fingerprint_all,
    find_identical_sets,
    format_fingerprint_report,
)


def _make_store(sets: dict):
    store = MagicMock()
    store.list_sets.return_value = list(sets.keys())
    store.load.side_effect = lambda name: sets.get(name)
    return store


def test_fingerprint_returns_string():
    fp = fingerprint_env_set({"KEY": "value"})
    assert isinstance(fp, str)
    assert len(fp) == 64  # sha256 hex


def test_fingerprint_deterministic():
    env = {"A": "1", "B": "2"}
    assert fingerprint_env_set(env) == fingerprint_env_set(env)


def test_fingerprint_order_independent():
    fp1 = fingerprint_env_set({"A": "1", "B": "2"})
    fp2 = fingerprint_env_set({"B": "2", "A": "1"})
    assert fp1 == fp2


def test_fingerprint_different_envs_differ():
    fp1 = fingerprint_env_set({"A": "1"})
    fp2 = fingerprint_env_set({"A": "2"})
    assert fp1 != fp2


def test_fingerprint_md5_length():
    fp = fingerprint_env_set({"X": "y"}, algorithm="md5")
    assert len(fp) == 32


def test_fingerprint_sha1_length():
    fp = fingerprint_env_set({"X": "y"}, algorithm="sha1")
    assert len(fp) == 40


def test_fingerprint_invalid_algorithm_raises():
    with pytest.raises(ValueError, match="Unsupported algorithm"):
        fingerprint_env_set({"A": "1"}, algorithm="crc32")


def test_fingerprint_all_returns_all_sets():
    store = _make_store({"dev": {"A": "1"}, "prod": {"A": "2"}})
    fps = fingerprint_all(store)
    assert set(fps.keys()) == {"dev", "prod"}


def test_fingerprint_all_empty_store():
    store = _make_store({})
    assert fingerprint_all(store) == {}


def test_find_identical_sets_detects_duplicates():
    env = {"A": "1"}
    store = _make_store({"dev": env, "staging": env, "prod": {"A": "2"}})
    groups = find_identical_sets(store)
    assert len(groups) == 1
    assert set(groups[0]) == {"dev", "staging"}


def test_find_identical_sets_no_duplicates():
    store = _make_store({"dev": {"A": "1"}, "prod": {"A": "2"}})
    assert find_identical_sets(store) == []


def test_format_fingerprint_report_empty():
    result = format_fingerprint_report({})
    assert "No environment sets" in result


def test_format_fingerprint_report_contains_names():
    fps = {"dev": "abc123", "prod": "def456"}
    report = format_fingerprint_report(fps)
    assert "dev" in report
    assert "prod" in report
    assert "abc123" in report
