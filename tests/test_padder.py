"""Tests for envctl.padder."""
import pytest
from envctl.padder import (
    align_pairs,
    format_padded_report,
    pad_keys,
    pad_values,
    truncate_values,
)


# ---------------------------------------------------------------------------
# pad_keys
# ---------------------------------------------------------------------------

def test_pad_keys_empty_returns_empty():
    assert pad_keys({}) == {}


def test_pad_keys_aligns_to_longest_key():
    env = {"A": "1", "LONG_KEY": "2"}
    result = pad_keys(env)
    width = len("LONG_KEY")
    for k in result:
        assert len(k) == width


def test_pad_keys_values_unchanged():
    env = {"X": "hello", "YYYY": "world"}
    result = pad_keys(env)
    values = list(result.values())
    assert "hello" in values
    assert "world" in values


# ---------------------------------------------------------------------------
# pad_values
# ---------------------------------------------------------------------------

def test_pad_values_empty_returns_empty():
    assert pad_values({}) == {}


def test_pad_values_aligns_to_longest_value():
    env = {"A": "short", "B": "much_longer_value"}
    result = pad_values(env)
    width = len("much_longer_value")
    for v in result.values():
        assert len(v) == width


# ---------------------------------------------------------------------------
# align_pairs
# ---------------------------------------------------------------------------

def test_align_pairs_empty_returns_empty():
    assert align_pairs({}) == []


def test_align_pairs_sorted_alphabetically():
    env = {"Z": "last", "A": "first", "M": "mid"}
    keys = [k.strip() for k, _ in align_pairs(env)]
    assert keys == sorted(keys)


def test_align_pairs_keys_same_width():
    env = {"SHORT": "x", "MUCH_LONGER": "y"}
    widths = {len(k) for k, _ in align_pairs(env)}
    assert len(widths) == 1


# ---------------------------------------------------------------------------
# format_padded_report
# ---------------------------------------------------------------------------

def test_format_padded_report_empty():
    assert format_padded_report({}) == "(empty)"


def test_format_padded_report_contains_separator():
    report = format_padded_report({"KEY": "val"}, separator=" = ")
    assert " = " in report


def test_format_padded_report_all_keys_present():
    env = {"ALPHA": "1", "BETA": "2", "GAMMA": "3"}
    report = format_padded_report(env)
    for k in env:
        assert k in report
    for v in env.values():
        assert v in report


def test_format_padded_report_custom_separator():
    report = format_padded_report({"K": "V"}, separator="->")
    assert "->" in report


# ---------------------------------------------------------------------------
# truncate_values
# ---------------------------------------------------------------------------

def test_truncate_values_short_values_unchanged():
    env = {"A": "hello"}
    assert truncate_values(env, max_len=20) == {"A": "hello"}


def test_truncate_values_long_value_truncated():
    env = {"A": "x" * 100}
    result = truncate_values(env, max_len=10)
    assert len(result["A"]) == 10
    assert result["A"].endswith("...")


def test_truncate_values_exact_length_unchanged():
    env = {"A": "1234567890"}
    result = truncate_values(env, max_len=10)
    assert result["A"] == "1234567890"


def test_truncate_values_invalid_max_len_raises():
    with pytest.raises(ValueError):
        truncate_values({"A": "hello"}, max_len=2, ellipsis="...")
