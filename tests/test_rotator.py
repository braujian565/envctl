"""Tests for envctl.rotator."""

from __future__ import annotations

import json
import pathlib
import pytest

from envctl.store import EnvStore
from envctl.rotator import rotate_key, rotation_report


@pytest.fixture()
def store(tmp_path: pathlib.Path) -> EnvStore:
    s = EnvStore(str(tmp_path / "store.json"))
    s.save("dev", {"DB_PASS": "old", "API_KEY": "abc"})
    s.save("prod", {"DB_PASS": "old_prod", "OTHER": "x"})
    s.save("empty", {})
    return s


def test_rotate_key_single_set(store: EnvStore) -> None:
    results = rotate_key(store, "DB_PASS", "new_secret", set_name="dev")
    assert results == {"dev": True}
    assert store.load("dev")["DB_PASS"] == "new_secret"


def test_rotate_key_all_sets(store: EnvStore) -> None:
    results = rotate_key(store, "DB_PASS", "rotated")
    assert results["dev"] is True
    assert results["prod"] is True
    assert results["empty"] is False  # key not present


def test_rotate_key_missing_key_returns_false(store: EnvStore) -> None:
    results = rotate_key(store, "NONEXISTENT", "value", set_name="dev")
    assert results["dev"] is False


def test_rotate_key_does_not_touch_other_keys(store: EnvStore) -> None:
    rotate_key(store, "DB_PASS", "new", set_name="dev")
    env = store.load("dev")
    assert env["API_KEY"] == "abc"


def test_rotate_key_missing_set_returns_false(store: EnvStore) -> None:
    results = rotate_key(store, "DB_PASS", "v", set_name="ghost")
    assert results["ghost"] is False


def test_rotation_report_shows_updated(store: EnvStore) -> None:
    results = {"dev": True, "prod": False}
    report = rotation_report(results, "DB_PASS")
    assert "dev" in report
    assert "prod" in report
    assert "DB_PASS" in report


def test_rotation_report_none_updated() -> None:
    report = rotation_report({"a": False, "b": False}, "SECRET")
    assert "(none)" in report
