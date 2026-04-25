"""Tests for envctl.mapper."""
from __future__ import annotations

import pytest

from envctl.mapper import apply_mapping, invert_mapping, diff_mapping, map_env_set


# ---------------------------------------------------------------------------
# apply_mapping
# ---------------------------------------------------------------------------

def test_apply_mapping_renames_key():
    env = {"OLD_KEY": "value"}
    result = apply_mapping(env, {"OLD_KEY": "NEW_KEY"})
    assert result == {"NEW_KEY": "value"}


def test_apply_mapping_keeps_unmapped_by_default():
    env = {"A": "1", "B": "2"}
    result = apply_mapping(env, {"A": "ALPHA"})
    assert result == {"ALPHA": "1", "B": "2"}


def test_apply_mapping_drops_unmapped_when_flag_set():
    env = {"A": "1", "B": "2"}
    result = apply_mapping(env, {"A": "ALPHA"}, drop_unmapped=True)
    assert result == {"ALPHA": "1"}
    assert "B" not in result


def test_apply_mapping_empty_env():
    result = apply_mapping({}, {"A": "B"})
    assert result == {}


def test_apply_mapping_empty_mapping():
    env = {"X": "y"}
    result = apply_mapping(env, {})
    assert result == {"X": "y"}


# ---------------------------------------------------------------------------
# invert_mapping
# ---------------------------------------------------------------------------

def test_invert_mapping_basic():
    inv = invert_mapping({"OLD": "NEW"})
    assert inv == {"NEW": "OLD"}


def test_invert_mapping_multiple():
    inv = invert_mapping({"A": "X", "B": "Y"})
    assert inv == {"X": "A", "Y": "B"}


def test_invert_mapping_raises_on_duplicate_target():
    with pytest.raises(ValueError, match="Duplicate target key"):
        invert_mapping({"A": "SAME", "B": "SAME"})


# ---------------------------------------------------------------------------
# diff_mapping
# ---------------------------------------------------------------------------

def test_diff_mapping_all_present():
    report = diff_mapping({"A": "X", "B": "Y"}, {"A": "1", "B": "2"})
    assert set(report["present"]) == {"A", "B"}
    assert report["missing"] == []


def test_diff_mapping_some_missing():
    report = diff_mapping({"A": "X", "C": "Z"}, {"A": "1"})
    assert "A" in report["present"]
    assert "C" in report["missing"]


# ---------------------------------------------------------------------------
# map_env_set (integration with store)
# ---------------------------------------------------------------------------

class _FakeStore:
    def __init__(self, data):
        self._data = data

    def load(self, name):
        return self._data.get(name)


def test_map_env_set_returns_mapped_env():
    store = _FakeStore({"prod": {"DB_HOST": "localhost", "DB_PORT": "5432"}})
    result = map_env_set(store, "prod", {"DB_HOST": "DATABASE_HOST"})
    assert result["DATABASE_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"


def test_map_env_set_returns_none_when_missing():
    store = _FakeStore({})
    assert map_env_set(store, "ghost", {"A": "B"}) is None
