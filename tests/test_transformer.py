"""Tests for envctl.transformer."""
import pytest
from envctl.transformer import (
    register_transform,
    list_transforms,
    apply_transform,
    transform_env_set,
    format_transform_report,
)


def test_list_transforms_includes_builtins():
    names = list_transforms()
    assert "uppercase_values" in names
    assert "lowercase_values" in names
    assert "strip_whitespace" in names
    assert "remove_quotes" in names


def test_register_custom_transform():
    register_transform("double", lambda v: v * 2)
    assert "double" in list_transforms()
    assert apply_transform("double", "ab") == "abab"


def test_apply_transform_uppercase():
    assert apply_transform("uppercase_values", "hello") == "HELLO"


def test_apply_transform_lowercase():
    assert apply_transform("lowercase_values", "WORLD") == "world"


def test_apply_transform_strip_whitespace():
    assert apply_transform("strip_whitespace", "  hi  ") == "hi"


def test_apply_transform_remove_quotes():
    assert apply_transform("remove_quotes", "'value'") == "value"
    assert apply_transform("remove_quotes", '"value"') == "value"


def test_apply_transform_unknown_raises():
    with pytest.raises(KeyError, match="no_such_transform"):
        apply_transform("no_such_transform", "x")


def test_transform_env_set_all_keys():
    env = {"A": "hello", "B": "world"}
    result = transform_env_set(env, ["uppercase_values"])
    assert result == {"A": "HELLO", "B": "WORLD"}


def test_transform_env_set_limited_keys():
    env = {"A": "hello", "B": "world"}
    result = transform_env_set(env, ["uppercase_values"], keys=["A"])
    assert result["A"] == "HELLO"
    assert result["B"] == "world"


def test_transform_env_set_chained():
    env = {"KEY": "  'spaced'  "}
    result = transform_env_set(env, ["strip_whitespace", "remove_quotes"])
    assert result["KEY"] == "spaced"


def test_transform_env_set_does_not_mutate_original():
    env = {"X": "abc"}
    transform_env_set(env, ["uppercase_values"])
    assert env["X"] == "abc"


def test_format_transform_report_no_changes():
    env = {"A": "same"}
    report = format_transform_report(env, {"A": "same"})
    assert report == "No changes."


def test_format_transform_report_shows_diff():
    original = {"A": "hello"}
    transformed = {"A": "HELLO"}
    report = format_transform_report(original, transformed)
    assert "A" in report
    assert "hello" in report
    assert "HELLO" in report
