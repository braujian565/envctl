import pytest
from unittest.mock import patch, MagicMock
from envctl.comparator import _compare_dicts, compare_sets, compare_with_snapshot, format_comparison


@pytest.fixture
def mock_store():
    store = MagicMock()
    return store


def test_compare_dicts_same():
    result = _compare_dicts({"A": "1"}, {"A": "1"})
    assert result["same"] == {"A": "1"}
    assert result["changed"] == {}
    assert result["only_a"] == {}
    assert result["only_b"] == {}


def test_compare_dicts_only_a():
    result = _compare_dicts({"X": "1"}, {})
    assert result["only_a"] == {"X": "1"}


def test_compare_dicts_only_b():
    result = _compare_dicts({}, {"Y": "2"})
    assert result["only_b"] == {"Y": "2"}


def test_compare_dicts_changed():
    result = _compare_dicts({"K": "old"}, {"K": "new"})
    assert result["changed"] == {"K": {"a": "old", "b": "new"}}


def test_compare_sets_success(mock_store):
    mock_store.load.side_effect = lambda name: {"A": "1"} if name == "dev" else {"A": "2"}
    result = compare_sets(mock_store, "dev", "prod")
    assert "changed" in result
    assert result["changed"]["A"] == {"a": "1", "b": "2"}


def test_compare_sets_missing_a(mock_store):
    mock_store.load.return_value = None
    with pytest.raises(KeyError, match="dev"):
        compare_sets(mock_store, "dev", "prod")


def test_compare_sets_missing_b(mock_store):
    mock_store.load.side_effect = lambda name: {"A": "1"} if name == "dev" else None
    with pytest.raises(KeyError, match="prod"):
        compare_sets(mock_store, "dev", "prod")


def test_compare_with_snapshot_success(mock_store):
    mock_store.load.return_value = {"KEY": "val"}
    with patch("envctl.comparator.load_snapshot", return_value={"vars": {"KEY": "other"}}):
        result = compare_with_snapshot(mock_store, "dev", "snap123")
    assert result["changed"]["KEY"] == {"a": "val", "b": "other"}


def test_compare_with_snapshot_missing_set(mock_store):
    mock_store.load.return_value = None
    with pytest.raises(KeyError, match="dev"):
        compare_with_snapshot(mock_store, "dev", "snap123")


def test_compare_with_snapshot_missing_snapshot(mock_store):
    mock_store.load.return_value = {"K": "v"}
    with patch("envctl.comparator.load_snapshot", return_value=None):
        with pytest.raises(KeyError, match="snap999"):
            compare_with_snapshot(mock_store, "dev", "snap999")


def test_format_comparison_no_diff():
    result = {"same": {"A": "1"}, "changed": {}, "only_a": {}, "only_b": {}}
    assert format_comparison(result) == "No differences found."


def test_format_comparison_with_diff():
    result = {"same": {}, "changed": {"K": {"a": "x", "b": "y"}}, "only_a": {"M": "1"}, "only_b": {}}
    out = format_comparison(result, label_a="dev", label_b="prod")
    assert "only in dev: M=1" in out
    assert "changed: K" in out
