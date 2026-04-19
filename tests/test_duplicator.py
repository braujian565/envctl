import pytest
from envctl.duplicator import (
    find_duplicate_values,
    find_duplicate_keys,
    format_duplicate_values_report,
    format_duplicate_keys_report,
)

SETS = {
    "dev": {"DB_URL": "postgres://localhost", "SECRET": "abc123", "PORT": "8080"},
    "staging": {"DB_URL": "postgres://staging", "SECRET": "abc123", "PORT": "9090"},
    "prod": {"DB_URL": "postgres://prod", "SECRET": "xyz999", "PORT": "8080"},
}


def test_find_duplicate_values_detects_shared_value():
    dupes = find_duplicate_values(SETS)
    assert "abc123" in dupes
    locations = dupes["abc123"]
    set_names = [s for s, _ in locations]
    assert "dev" in set_names
    assert "staging" in set_names


def test_find_duplicate_values_detects_port():
    dupes = find_duplicate_values(SETS)
    assert "8080" in dupes
    set_names = [s for s, _ in dupes["8080"]]
    assert "dev" in set_names
    assert "prod" in set_names


def test_find_duplicate_values_no_dupes():
    sets = {"a": {"X": "1"}, "b": {"Y": "2"}}
    assert find_duplicate_values(sets) == {}


def test_find_duplicate_values_ignores_empty():
    sets = {"a": {"X": ""}, "b": {"Y": ""}}
    assert find_duplicate_values(sets) == {}


def test_find_duplicate_keys_basic():
    dupes = find_duplicate_keys(SETS)
    assert "DB_URL" in dupes
    assert set(dupes["DB_URL"]) == {"dev", "staging", "prod"}


def test_find_duplicate_keys_no_dupes():
    sets = {"a": {"ONLY_A": "1"}, "b": {"ONLY_B": "2"}}
    assert find_duplicate_keys(sets) == {}


def test_format_duplicate_values_empty():
    result = format_duplicate_values_report({})
    assert "No duplicate values" in result


def test_format_duplicate_values_shows_sets():
    dupes = find_duplicate_values(SETS)
    report = format_duplicate_values_report(dupes)
    assert "abc123" in report
    assert "dev" in report
    assert "staging" in report


def test_format_duplicate_keys_empty():
    result = format_duplicate_keys_report({})
    assert "No duplicate keys" in result


def test_format_duplicate_keys_shows_key():
    dupes = find_duplicate_keys(SETS)
    report = format_duplicate_keys_report(dupes)
    assert "DB_URL" in report
    assert "dev" in report
