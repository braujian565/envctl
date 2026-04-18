"""Tests for envctl.validator module."""

import pytest
from envctl.validator import validate_key, validate_env_set, validate_set_name


# --- validate_key ---

def test_validate_key_simple():
    assert validate_key("MY_VAR") is True

def test_validate_key_with_numbers():
    assert validate_key("VAR_123") is True

def test_validate_key_leading_underscore():
    assert validate_key("_PRIVATE") is True

def test_validate_key_rejects_leading_digit():
    assert validate_key("1VAR") is False

def test_validate_key_rejects_hyphen():
    assert validate_key("MY-VAR") is False

def test_validate_key_rejects_empty():
    assert validate_key("") is False

def test_validate_key_rejects_space():
    assert validate_key("MY VAR") is False


# --- validate_env_set ---

def test_validate_env_set_valid():
    env = {"DB_HOST": "localhost", "PORT": "5432"}
    errors = validate_env_set(env)
    assert errors == []

def test_validate_env_set_invalid_key():
    env = {"1BAD": "value"}
    errors = validate_env_set(env)
    assert len(errors) == 1
    assert errors[0][0] == "1BAD"

def test_validate_env_set_non_string_value():
    env = {"PORT": 5432}  # type: ignore
    errors = validate_env_set(env)
    assert any("PORT" in key for key, _ in errors)

def test_validate_env_set_null_byte_in_value():
    env = {"SECRET": "val\x00ue"}
    errors = validate_env_set(env)
    assert any("SECRET" in key for key, _ in errors)

def test_validate_env_set_multiple_errors():
    env = {"BAD KEY": "ok", "GOOD": 123}  # type: ignore
    errors = validate_env_set(env)
    assert len(errors) == 2


# --- validate_set_name ---

def test_validate_set_name_valid():
    ok, msg = validate_set_name("production")
    assert ok is True
    assert msg == ""

def test_validate_set_name_with_dashes_and_dots():
    ok, _ = validate_set_name("my-env.v2")
    assert ok is True

def test_validate_set_name_empty():
    ok, msg = validate_set_name("")
    assert ok is False
    assert "empty" in msg

def test_validate_set_name_whitespace():
    ok, msg = validate_set_name("   ")
    assert ok is False

def test_validate_set_name_invalid_chars():
    ok, msg = validate_set_name("bad name!")
    assert ok is False
    assert "invalid characters" in msg

def test_validate_set_name_too_long():
    ok, msg = validate_set_name("a" * 65)
    assert ok is False
    assert "exceeds" in msg
