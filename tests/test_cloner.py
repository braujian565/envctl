import pytest
from unittest.mock import MagicMock
from envctl.cloner import clone_set, rename_set


@pytest.fixture
def mock_store():
    store = MagicMock()
    _data = {}

    def _save(name, data):
        _data[name] = dict(data)

    def _load(name):
        return _data.get(name)

    def _delete(name):
        _data.pop(name, None)

    store.save.side_effect = _save
    store.load.side_effect = _load
    store.delete.side_effect = _delete
    store._data = _data
    return store


def test_clone_copies_vars(mock_store):
    mock_store._data["prod"] = {"DB": "prod-db", "KEY": "abc"}
    result = clone_set(mock_store, "prod", "staging")
    assert result == {"DB": "prod-db", "KEY": "abc"}
    assert mock_store._data["staging"] == {"DB": "prod-db", "KEY": "abc"}


def test_clone_source_not_found_raises(mock_store):
    with pytest.raises(KeyError, match="not found"):
        clone_set(mock_store, "ghost", "copy")


def test_clone_dest_exists_raises_without_overwrite(mock_store):
    mock_store._data["prod"] = {"A": "1"}
    mock_store._data["staging"] = {"B": "2"}
    with pytest.raises(ValueError, match="already exists"):
        clone_set(mock_store, "prod", "staging")


def test_clone_dest_exists_overwrite(mock_store):
    mock_store._data["prod"] = {"A": "1"}
    mock_store._data["staging"] = {"B": "2"}
    result = clone_set(mock_store, "prod", "staging", overwrite=True)
    assert result == {"A": "1"}
    assert mock_store._data["staging"] == {"A": "1"}


def test_clone_does_not_mutate_source(mock_store):
    mock_store._data["prod"] = {"X": "original"}
    result = clone_set(mock_store, "prod", "copy")
    result["X"] = "mutated"
    assert mock_store._data["prod"]["X"] == "original"


def test_rename_moves_set(mock_store):
    mock_store._data["old"] = {"ENV": "val"}
    result = rename_set(mock_store, "old", "new")
    assert result == {"ENV": "val"}
    assert "new" in mock_store._data
    assert "old" not in mock_store._data


def test_rename_source_not_found_raises(mock_store):
    with pytest.raises(KeyError):
        rename_set(mock_store, "missing", "dest")
