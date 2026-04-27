"""Tests for envctl.quoter."""
from __future__ import annotations

import pytest

from envctl.quoter import (
    format_quote_report,
    quote_env_set,
    quote_value,
    unquote_env_set,
    unquote_value,
)


# ---------------------------------------------------------------------------
# quote_value
# ---------------------------------------------------------------------------

def test_quote_value_shell_simple():
    assert quote_value("hello") == "hello"


def test_quote_value_shell_with_space():
    result = quote_value("hello world")
    assert "hello world" in result
    assert result.startswith("'")


def test_quote_value_shell_with_single_quote():
    result = quote_value("it's")
    # shlex.quote should handle embedded single quotes
    assert "it" in result and "s" in result


def test_quote_value_double_style():
    result = quote_value("hello", style="double")
    assert result == '"hello"'


def test_quote_value_double_escapes_inner_double_quote():
    result = quote_value('say "hi"', style="double")
    assert '\\"' in result


def test_quote_value_auto_safe_unchanged():
    assert quote_value("safe123", style="auto") == "safe123"


def test_quote_value_auto_unsafe_quoted():
    result = quote_value("needs quoting!", style="auto")
    assert result != "needs quoting!"


def test_quote_value_unknown_style_raises():
    with pytest.raises(ValueError, match="Unknown quote style"):
        quote_value("x", style="xml")


# ---------------------------------------------------------------------------
# unquote_value
# ---------------------------------------------------------------------------

def test_unquote_value_single_quotes():
    assert unquote_value("'hello'") == "hello"


def test_unquote_value_double_quotes():
    assert unquote_value('"hello"') == "hello"


def test_unquote_value_no_quotes_unchanged():
    assert unquote_value("hello") == "hello"


def test_unquote_value_escaped_double_quote():
    assert unquote_value('"say \\"hi\\""') == 'say "hi"'


# ---------------------------------------------------------------------------
# quote_env_set / unquote_env_set
# ---------------------------------------------------------------------------

def test_quote_env_set_applies_to_all_values():
    env = {"A": "hello world", "B": "safe"}
    result = quote_env_set(env, style="shell")
    assert "hello world" in result["A"]
    assert result["B"] == "safe"


def test_unquote_env_set_strips_all():
    env = {"A": "'hello'", "B": '"world"'}
    result = unquote_env_set(env)
    assert result == {"A": "hello", "B": "world"}


# ---------------------------------------------------------------------------
# format_quote_report
# ---------------------------------------------------------------------------

def test_format_quote_report_no_changes():
    env = {"A": "safe"}
    report = format_quote_report(env, env.copy())
    assert "already" in report


def test_format_quote_report_lists_changed_keys():
    original = {"A": "hello world"}
    quoted = quote_env_set(original, style="shell")
    report = format_quote_report(original, quoted)
    assert "A" in report
    assert "1 value" in report
