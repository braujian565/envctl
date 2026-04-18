import pytest
from unittest.mock import MagicMock
from envctl.merger import merge_sets, preview_merge


@pytest.fixture
def mock_store():
    store = MagicMock()
    _data = {}

    def _save(name, vars):
        _data[name] = dict(vars)

    def _load(name):
        return _data.get(name)

    store.save.side_effect = _save
    store.load.side_effect = _load
    store._data = _data
    return store


def test_merge_two_sets(mock_store):
    mock_store._data["base"] = {"A": "1", "B": "2"}
    mock_store._data["override"] = {"B": "99", "C": "3"}
    result = merge_sets(mock_store, ["base", "override"], "merged")
    assert result == {"A": "1", "B": "99", "C": "3"}
    assert mock_store._data["merged"] == result


def test_merge_no_overwrite(mock_store):
    mock_store._data["base"] = {"A": "1", "B": "2"}
    mock_store._data["extra"] = {"B": "99", "C": "3"}
    result = merge_sets(mock_store, ["base", "extra"], "merged", overwrite=False)
    assert result["B"] == "2"  # first definition wins
    assert result["C"] == "3"


def test_merge_missing_set_raises(mock_store):
    mock_store._data["base"] = {"A": "1"}
    with pytest.raises(KeyError, match="ghost"):
        merge_sets(mock_store, ["base", "ghost"], "merged")


def test_merge_empty_list_raises(mock_store):
    with pytest.raises(ValueError):
        merge_sets(mock_store, [], "merged")


def test_preview_does_not_save(mock_store):
    mock_store._data["a"] = {"X": "1"}
    mock_store._data["b"] = {"Y": "2"}
    result = preview_merge(mock_store, ["a", "b"])
    assert result == {"X": "1", "Y": "2"}
    mock_store.save.assert_not_called()


def test_preview_overwrite_true(mock_store):
    mock_store._data["a"] = {"K": "old"}
    mock_store._data["b"] = {"K": "new"}
    result = preview_merge(mock_store, ["a", "b"], overwrite=True)
    assert result["K"] == "new"


def test_preview_overwrite_false(mock_store):
    mock_store._data["a"] = {"K": "old"}
    mock_store._data["b"] = {"K": "new"}
    result = preview_merge(mock_store, ["a", "b"], overwrite=False)
    assert result["K"] == "old"
