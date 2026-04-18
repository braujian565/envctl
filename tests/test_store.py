"""Tests for EnvStore."""

import json
import pytest
from pathlib import Path
from envctl.store import EnvStore


@pytest.fixture
def store(tmp_path):
    return EnvStore(store_path=tmp_path / "envsets.json")


def test_store_creates_file(tmp_path):
    path = tmp_path / "sub" / "envsets.json"
    EnvStore(store_path=path)
    assert path.exists()


def test_save_and_load_set(store):
    store.save_set("dev", {"DEBUG": "true", "PORT": "8080"})
    result = store.load_set("dev")
    assert result == {"DEBUG": "true", "PORT": "8080"}


def test_load_nonexistent_returns_none(store):
    assert store.load_set("nonexistent") is None


def test_list_sets_empty(store):
    assert store.list_sets() == []


def test_list_sets_after_save(store):
    store.save_set("dev", {"A": "1"})
    store.save_set("prod", {"A": "2"})
    names = store.list_sets()
    assert "dev" in names
    assert "prod" in names
    assert len(names) == 2


def test_delete_existing_set(store):
    store.save_set("staging", {"X": "y"})
    assert store.delete_set("staging") is True
    assert store.load_set("staging") is None


def test_delete_nonexistent_set(store):
    assert store.delete_set("ghost") is False


def test_overwrite_set(store):
    store.save_set("dev", {"A": "1"})
    store.save_set("dev", {"A": "2", "B": "3"})
    result = store.load_set("dev")
    assert result == {"A": "2", "B": "3"}
