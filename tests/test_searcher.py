"""Tests for envctl.searcher."""
import pytest
from unittest.mock import MagicMock
from envctl.searcher import search_by_key, search_by_value, find_key_across_sets


@pytest.fixture
def mock_store():
    store = MagicMock()
    data = {
        "prod": {"DB_HOST": "prod.db", "DB_PORT": "5432", "SECRET_KEY": "abc123"},
        "staging": {"DB_HOST": "staging.db", "API_URL": "https://staging.example.com"},
        "dev": {"DEBUG": "true", "API_URL": "http://localhost:8000"},
    }
    store.list_sets.return_value = list(data.keys())
    store.load_set.side_effect = lambda name: data.get(name)
    return store


def test_search_by_key_exact_glob(mock_store):
    results = search_by_key(mock_store, "DB_HOST")
    assert "prod" in results
    assert "staging" in results
    assert results["prod"]["DB_HOST"] == "prod.db"


def test_search_by_key_wildcard(mock_store):
    results = search_by_key(mock_store, "DB_*")
    assert "prod" in results
    assert set(results["prod"].keys()) == {"DB_HOST", "DB_PORT"}
    assert "staging" in results
    assert "dev" not in results


def test_search_by_key_no_match(mock_store):
    results = search_by_key(mock_store, "NONEXISTENT_*")
    assert results == {}


def test_search_by_key_limited_sets(mock_store):
    results = search_by_key(mock_store, "DB_*", set_names=["dev"])
    assert results == {}


def test_search_by_value_glob(mock_store):
    results = search_by_value(mock_store, "*.db")
    assert "prod" in results
    assert "staging" in results
    assert "dev" not in results


def test_search_by_value_exact(mock_store):
    results = search_by_value(mock_store, "true")
    assert "dev" in results
    assert results["dev"]["DEBUG"] == "true"


def test_search_by_value_no_match(mock_store):
    results = search_by_value(mock_store, "zzz*")
    assert results == {}


def test_find_key_across_sets(mock_store):
    hits = find_key_across_sets(mock_store, "API_URL")
    names = [h[0] for h in hits]
    assert "staging" in names
    assert "dev" in names
    assert "prod" not in names


def test_find_key_not_present(mock_store):
    hits = find_key_across_sets(mock_store, "MISSING_KEY")
    assert hits == []


def test_find_key_returns_correct_values(mock_store):
    hits = dict(find_key_across_sets(mock_store, "DB_HOST"))
    assert hits["prod"] == "prod.db"
    assert hits["staging"] == "staging.db"
