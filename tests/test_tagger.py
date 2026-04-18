"""Tests for envctl.tagger."""

import pytest
from unittest.mock import MagicMock
from envctl import tagger


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.list_sets.return_value = ["dev", "prod", "staging"]
    store.load.return_value = {"KEY": "val"}
    store.load_meta.return_value = {}
    return store


def test_add_tag_new(mock_store):
    tagger.add_tag(mock_store, "dev", "backend")
    mock_store.save_meta.assert_called_once_with("dev", {"tags": ["backend"]})


def test_add_tag_preserves_existing(mock_store):
    mock_store.load_meta.return_value = {"tags": ["backend"]}
    tagger.add_tag(mock_store, "dev", "cloud")
    mock_store.save_meta.assert_called_once_with("dev", {"tags": ["backend", "cloud"]})


def test_add_tag_no_duplicate(mock_store):
    mock_store.load_meta.return_value = {"tags": ["backend"]}
    tagger.add_tag(mock_store, "dev", "backend")
    saved = mock_store.save_meta.call_args[0][1]
    assert saved["tags"].count("backend") == 1


def test_remove_tag_existing(mock_store):
    mock_store.load_meta.return_value = {"tags": ["backend", "cloud"]}
    result = tagger.remove_tag(mock_store, "dev", "backend")
    assert result is True
    mock_store.save_meta.assert_called_once_with("dev", {"tags": ["cloud"]})


def test_remove_tag_nonexistent(mock_store):
    mock_store.load_meta.return_value = {"tags": ["cloud"]}
    result = tagger.remove_tag(mock_store, "dev", "missing")
    assert result is False
    mock_store.save_meta.assert_not_called()


def test_remove_tag_last_tag_leaves_empty_list(mock_store):
    mock_store.load_meta.return_value = {"tags": ["backend"]}
    result = tagger.remove_tag(mock_store, "dev", "backend")
    assert result is True
    mock_store.save_meta.assert_called_once_with("dev", {"tags": []})


def test_get_tags_empty(mock_store):
    tags = tagger.get_tags(mock_store, "dev")
    assert tags == []


def test_get_tags_returns_list(mock_store):
    mock_store.load_meta.return_value = {"tags": ["a", "b"]}
    tags = tagger.get_tags(mock_store, "dev")
    assert tags == ["a", "b"]


def test_find_by_tag_matches(mock_store):
    def meta_side(name):
        return {"tags": ["backend"]} if name in ("dev", "staging") else {}
    mock_store.load_meta.side_effect = meta_side
    result = tagger.find_by_tag(mock_store, "backend")
    assert set(result) == {"dev", "staging"}


def test_find_by_tag_no_matches(mock_store):
    result = tagger.find_by_tag(mock_store, "nonexistent")
    assert result == []
