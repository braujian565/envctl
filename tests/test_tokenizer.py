"""Tests for envctl.tokenizer."""

import pytest
from envctl.tokenizer import (
    tokenize_value,
    tokenize_env_set,
    token_frequency,
    find_shared_tokens,
    format_token_report,
)


# ---------------------------------------------------------------------------
# tokenize_value
# ---------------------------------------------------------------------------

def test_tokenize_value_empty_string():
    assert tokenize_value("") == []


def test_tokenize_value_single_word():
    assert tokenize_value("hello") == ["hello"]


def test_tokenize_value_space_delimited():
    assert tokenize_value("hello world") == ["hello", "world"]


def test_tokenize_value_comma_delimited():
    assert tokenize_value("a,b,c") == ["a", "b", "c"]


def test_tokenize_value_mixed_delimiters():
    result = tokenize_value("host:5432/mydb")
    assert "host" in result
    assert "5432" in result
    assert "mydb" in result


def test_tokenize_value_strips_empty_segments():
    result = tokenize_value("a,,b")
    assert "" not in result
    assert result == ["a", "b"]


# ---------------------------------------------------------------------------
# tokenize_env_set
# ---------------------------------------------------------------------------

def test_tokenize_env_set_returns_all_keys():
    env = {"DB_URL": "localhost:5432", "APP_NAME": "myapp"}
    result = tokenize_env_set(env)
    assert set(result.keys()) == {"DB_URL", "APP_NAME"}


def test_tokenize_env_set_empty_value_gives_empty_list():
    env = {"EMPTY": ""}
    assert tokenize_env_set(env)["EMPTY"] == []


# ---------------------------------------------------------------------------
# token_frequency
# ---------------------------------------------------------------------------

def test_token_frequency_counts_correctly():
    env = {"A": "foo bar", "B": "foo baz"}
    freq = token_frequency(env)
    assert freq["foo"] == 2
    assert freq["bar"] == 1
    assert freq["baz"] == 1


def test_token_frequency_sorted_descending():
    env = {"A": "x x x y y z"}
    freq = token_frequency(env)
    counts = list(freq.values())
    assert counts == sorted(counts, reverse=True)


def test_token_frequency_empty_env():
    assert token_frequency({}) == {}


# ---------------------------------------------------------------------------
# find_shared_tokens
# ---------------------------------------------------------------------------

def test_find_shared_tokens_detects_shared():
    envs = {
        "dev": {"DB_HOST": "localhost"},
        "prod": {"DB_HOST": "localhost"},
    }
    shared = find_shared_tokens(envs)
    assert "localhost" in shared
    assert set(shared["localhost"]) == {"dev", "prod"}


def test_find_shared_tokens_no_overlap():
    envs = {
        "dev": {"KEY": "alpha"},
        "prod": {"KEY": "beta"},
    }
    shared = find_shared_tokens(envs)
    assert "alpha" not in shared
    assert "beta" not in shared


# ---------------------------------------------------------------------------
# format_token_report
# ---------------------------------------------------------------------------

def test_format_token_report_contains_set_name():
    report = format_token_report({"A": "hello"}, set_name="myenv")
    assert "myenv" in report


def test_format_token_report_contains_tokens():
    report = format_token_report({"A": "hello world"}, set_name="test")
    assert "hello" in report
    assert "world" in report


def test_format_token_report_empty_env():
    report = format_token_report({})
    assert "no tokens" in report
