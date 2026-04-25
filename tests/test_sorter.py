"""Tests for envctl.sorter."""
import pytest

from envctl.sorter import (
    format_sort_report,
    sort_env_set,
    sort_keys_alpha,
    sort_keys_by_value_alpha,
    sort_keys_by_value_length,
    sort_sets_by_name,
    sort_sets_by_size,
)


ENV = {"ZEBRA": "last", "ALPHA": "first", "MIDDLE": "mid"}


def test_sort_keys_alpha_ascending():
    result = sort_keys_alpha(ENV)
    assert list(result.keys()) == ["ALPHA", "MIDDLE", "ZEBRA"]


def test_sort_keys_alpha_descending():
    result = sort_keys_alpha(ENV, reverse=True)
    assert list(result.keys()) == ["ZEBRA", "MIDDLE", "ALPHA"]


def test_sort_keys_by_value_length_ascending():
    env = {"A": "hi", "B": "hello world", "C": "hey"}
    result = sort_keys_by_value_length(env)
    assert list(result.keys()) == ["A", "C", "B"]


def test_sort_keys_by_value_length_descending():
    env = {"A": "hi", "B": "hello world", "C": "hey"}
    result = sort_keys_by_value_length(env, reverse=True)
    assert list(result.keys())[0] == "B"


def test_sort_keys_by_value_alpha():
    env = {"X": "zebra", "Y": "apple", "Z": "mango"}
    result = sort_keys_by_value_alpha(env)
    assert list(result.keys()) == ["Y", "Z", "X"]


def test_sort_env_set_alpha():
    result = sort_env_set(ENV, method="alpha")
    assert list(result.keys()) == ["ALPHA", "MIDDLE", "ZEBRA"]


def test_sort_env_set_value_length():
    env = {"A": "hi", "B": "hello world", "C": "hey"}
    result = sort_env_set(env, method="value-length")
    assert list(result.keys()) == ["A", "C", "B"]


def test_sort_env_set_value_alpha():
    env = {"X": "zebra", "Y": "apple", "Z": "mango"}
    result = sort_env_set(env, method="value-alpha")
    assert list(result.keys()) == ["Y", "Z", "X"]


def test_sort_env_set_unknown_method_raises():
    with pytest.raises(ValueError, match="Unknown sort method"):
        sort_env_set(ENV, method="nonexistent")


def test_sort_env_set_preserves_values():
    result = sort_env_set(ENV, method="alpha")
    assert result["ALPHA"] == "first"
    assert result["ZEBRA"] == "last"


def test_sort_sets_by_size_ascending():
    sets = {"big": {"A": "1", "B": "2", "C": "3"}, "small": {"X": "1"}, "mid": {"P": "1", "Q": "2"}}
    result = sort_sets_by_size(sets)
    assert [name for name, _ in result] == ["small", "mid", "big"]


def test_sort_sets_by_size_descending():
    sets = {"big": {"A": "1", "B": "2"}, "small": {"X": "1"}}
    result = sort_sets_by_size(sets, reverse=True)
    assert result[0][0] == "big"


def test_sort_sets_by_name():
    sets = {"prod": {}, "dev": {}, "staging": {}}
    result = sort_sets_by_name(sets)
    assert result == ["dev", "prod", "staging"]


def test_format_sort_report_contains_keys():
    env = {"B": "val", "A": "other"}
    sorted_env = sort_keys_alpha(env)
    report = format_sort_report(env, sorted_env)
    assert "A" in report
    assert "B" in report


def test_format_sort_report_marks_moved_keys():
    env = {"B": "val", "A": "other"}
    sorted_env = sort_keys_alpha(env)
    report = format_sort_report(env, sorted_env)
    assert "was #" in report
