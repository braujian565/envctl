"""Tests for envctl.normalizer."""

import pytest
from envctl.normalizer import (
    uppercase_keys,
    strip_value_whitespace,
    remove_quote_wrapping,
    normalize_env_set,
    format_normalize_report,
)


# ---------------------------------------------------------------------------
# uppercase_keys
# ---------------------------------------------------------------------------

def test_uppercase_keys_already_upper():
    env = {"HOST": "localhost", "PORT": "5432"}
    result, changed = uppercase_keys(env)
    assert result == env
    assert changed == []


def test_uppercase_keys_converts_lower():
    env = {"host": "localhost", "Port": "5432"}
    result, changed = uppercase_keys(env)
    assert "HOST" in result
    assert "PORT" in result
    assert set(changed) == {"host", "Port"}


def test_uppercase_keys_preserves_values():
    env = {"db_name": "MyDatabase"}
    result, _ = uppercase_keys(env)
    assert result["DB_NAME"] == "MyDatabase"


# ---------------------------------------------------------------------------
# strip_value_whitespace
# ---------------------------------------------------------------------------

def test_strip_value_whitespace_clean():
    env = {"HOST": "localhost"}
    result, changed = strip_value_whitespace(env)
    assert result == env
    assert changed == []


def test_strip_value_whitespace_strips():
    env = {"HOST": "  localhost  ", "PORT": "5432"}
    result, changed = strip_value_whitespace(env)
    assert result["HOST"] == "localhost"
    assert result["PORT"] == "5432"
    assert changed == ["HOST"]


# ---------------------------------------------------------------------------
# remove_quote_wrapping
# ---------------------------------------------------------------------------

def test_remove_quote_wrapping_double_quotes():
    env = {"NAME": '"hello"'}
    result, changed = remove_quote_wrapping(env)
    assert result["NAME"] == "hello"
    assert "NAME" in changed


def test_remove_quote_wrapping_single_quotes():
    env = {"NAME": "'world'"}
    result, changed = remove_quote_wrapping(env)
    assert result["NAME"] == "world"


def test_remove_quote_wrapping_mismatched_quotes():
    env = {"NAME": "'hello\""}
    result, changed = remove_quote_wrapping(env)
    assert result["NAME"] == "'hello\""
    assert changed == []


def test_remove_quote_wrapping_short_value():
    env = {"X": "'"}
    result, changed = remove_quote_wrapping(env)
    assert result["X"] == "'"
    assert changed == []


# ---------------------------------------------------------------------------
# normalize_env_set
# ---------------------------------------------------------------------------

def test_normalize_env_set_all_rules():
    env = {"host": "  '  localhost  '  "}
    result, report = normalize_env_set(env)
    # key uppercased
    assert "HOST" in result
    # whitespace stripped from value
    assert not result["HOST"].startswith(" ")
    assert set(report.keys()) == {"uppercase_keys", "strip_value_whitespace", "remove_quote_wrapping"}


def test_normalize_env_set_subset_of_rules():
    env = {"host": "  localhost  "}
    result, report = normalize_env_set(env, rules=["strip_value_whitespace"])
    # key NOT uppercased because rule not included
    assert "host" in result
    assert result["host"] == "localhost"
    assert "uppercase_keys" not in report


def test_normalize_env_set_no_changes():
    env = {"HOST": "localhost", "PORT": "5432"}
    result, report = normalize_env_set(env)
    assert result == env
    for changed in report.values():
        assert changed == []


# ---------------------------------------------------------------------------
# format_normalize_report
# ---------------------------------------------------------------------------

def test_format_normalize_report_with_changes():
    report = {"uppercase_keys": ["host"], "strip_value_whitespace": []}
    output = format_normalize_report(report)
    assert "uppercase_keys" in output
    assert "host" in output
    assert "no changes" in output


def test_format_normalize_report_empty():
    output = format_normalize_report({})
    assert output == "No normalization rules applied."
