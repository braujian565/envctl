"""Tests for envctl.renamer."""
import pytest
from unittest.mock import MagicMock
from envctl.renamer import rename_key, bulk_rename_key


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.list_sets.return_value = ["dev", "prod"]
    return store


def _setup(store, sets):
    def load(name):
        return dict(sets.get(name, {}))
    store.load_set.side_effect = load


def test_rename_key_single_set(mock_store):
    _setup(mock_store, {"dev": {"OLD_KEY": "value", "OTHER": "x"}})
    results = rename_key(mock_store, "OLD_KEY", "NEW_KEY", set_name="dev")
    assert results["dev"] == ["renamed"]
    mock_store.save_set.assert_called_once_with("dev", {"NEW_KEY": "value", "OTHER": "x"})


def test_rename_key_not_found(mock_store):
    _setup(mock_store, {"dev": {"OTHER": "x"}})
    results = rename_key(mock_store, "MISSING", "NEW_KEY", set_name="dev")
    assert results["dev"] == []
    mock_store.save_set.assert_not_called()


def test_rename_key_all_sets(mock_store):
    _setup(mock_store, {"dev": {"FOO": "1"}, "prod": {"FOO": "2", "BAR": "3"}})
    results = rename_key(mock_store, "FOO", "BAZ")
    assert results["dev"] == ["renamed"]
    assert results["prod"] == ["renamed"]
    assert mock_store.save_set.call_count == 2


def test_rename_key_set_none_returns_empty(mock_store):
    mock_store.load_set.return_value = None
    results = rename_key(mock_store, "FOO", "BAR", set_name="ghost")
    assert results["ghost"] == []


def test_bulk_rename_applies_all(mock_store):
    _setup(mock_store, {"dev": {"A": "1", "B": "2", "C": "3"}})
    results = bulk_rename_key(mock_store, {"A": "X", "B": "Y"}, set_name="dev")
    assert set(results["dev"]) == {"A", "B"}
    saved = mock_store.save_set.call_args[0][1]
    assert "X" in saved and "Y" in saved and "C" in saved


def test_bulk_rename_skips_missing_keys(mock_store):
    _setup(mock_store, {"dev": {"A": "1"}})
    results = bulk_rename_key(mock_store, {"A": "X", "NOPE": "Y"}, set_name="dev")
    assert results["dev"] == ["A"]


def test_bulk_rename_no_match_skips_save(mock_store):
    _setup(mock_store, {"dev": {"A": "1"}})
    bulk_rename_key(mock_store, {"MISSING": "X"}, set_name="dev")
    mock_store.save_set.assert_not_called()
