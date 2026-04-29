"""Tests for envctl.caster."""
import pytest

from envctl.caster import (
    SUPPORTED_TYPES,
    cast_env_set,
    cast_value,
    format_cast_report,
    infer_type,
)


# ---------------------------------------------------------------------------
# cast_value
# ---------------------------------------------------------------------------

def test_cast_value_str_passthrough():
    assert cast_value("hello", "str") == "hello"


def test_cast_value_int_valid():
    assert cast_value("42", "int") == 42


def test_cast_value_int_invalid_raises():
    with pytest.raises(ValueError, match="Cannot cast"):
        cast_value("abc", "int")


def test_cast_value_float_valid():
    assert cast_value("3.14", "float") == pytest.approx(3.14)


def test_cast_value_float_invalid_raises():
    with pytest.raises(ValueError, match="Cannot cast"):
        cast_value("not_a_float", "float")


def test_cast_value_bool_true_variants():
    for v in ("1", "true", "True", "yes", "YES", "on"):
        assert cast_value(v, "bool") is True


def test_cast_value_bool_false_variants():
    for v in ("0", "false", "False", "no", "NO", "off"):
        assert cast_value(v, "bool") is False


def test_cast_value_bool_invalid_raises():
    with pytest.raises(ValueError, match="Cannot cast"):
        cast_value("maybe", "bool")


def test_cast_value_unsupported_type_raises():
    with pytest.raises(ValueError, match="Unsupported type"):
        cast_value("x", "list")


# ---------------------------------------------------------------------------
# infer_type
# ---------------------------------------------------------------------------

def test_infer_type_bool():
    assert infer_type("true") == "bool"
    assert infer_type("0") == "bool"


def test_infer_type_int():
    assert infer_type("100") == "int"


def test_infer_type_float():
    assert infer_type("2.718") == "float"


def test_infer_type_str_fallback():
    assert infer_type("postgres://localhost") == "str"


# ---------------------------------------------------------------------------
# cast_env_set
# ---------------------------------------------------------------------------

def test_cast_env_set_applies_type_map():
    env = {"PORT": "8080", "DEBUG": "true", "NAME": "myapp"}
    result = cast_env_set(env, {"PORT": "int", "DEBUG": "bool"})
    assert result["PORT"] == 8080
    assert result["DEBUG"] is True
    assert result["NAME"] == "myapp"


def test_cast_env_set_empty_env():
    assert cast_env_set({}, {"PORT": "int"}) == {}


def test_cast_env_set_unmapped_keys_remain_str():
    env = {"WORKERS": "4"}
    result = cast_env_set(env, {})
    assert result["WORKERS"] == "4"
    assert isinstance(result["WORKERS"], str)


# ---------------------------------------------------------------------------
# format_cast_report
# ---------------------------------------------------------------------------

def test_format_cast_report_empty():
    assert format_cast_report({}) == "No keys to inspect."


def test_format_cast_report_contains_inferred_type():
    report = format_cast_report({"PORT": "5432", "DEBUG": "false"})
    assert "int" in report
    assert "bool" in report


def test_supported_formats_list():
    assert "int" in SUPPORTED_TYPES
    assert "bool" in SUPPORTED_TYPES
    assert "float" in SUPPORTED_TYPES
    assert "str" in SUPPORTED_TYPES
