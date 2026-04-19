"""Tests for envctl.encryptor module."""

import os
import pytest

pytest.importorskip("cryptography", reason="cryptography package not installed")

from envctl.encryptor import (
    generate_key,
    encrypt_value,
    decrypt_value,
    encrypt_env_set,
    decrypt_env_set,
    ENV_KEY_VAR,
)


@pytest.fixture
def key():
    return generate_key()


def test_generate_key_returns_string():
    k = generate_key()
    assert isinstance(k, str)
    assert len(k) > 0


def test_encrypt_decrypt_roundtrip(key):
    original = "super_secret_value"
    token = encrypt_value(original, key=key)
    assert token != original
    assert decrypt_value(token, key=key) == original


def test_encrypt_produces_different_tokens_each_time(key):
    val = "hello"
    t1 = encrypt_value(val, key=key)
    t2 = encrypt_value(val, key=key)
    # Fernet uses random IV, so tokens differ
    assert t1 != t2


def test_decrypt_wrong_key_raises(key):
    other_key = generate_key()
    token = encrypt_value("value", key=key)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_value(token, key=other_key)


def test_no_key_raises_value_error(monkeypatch):
    monkeypatch.delenv(ENV_KEY_VAR, raising=False)
    with pytest.raises(ValueError, match="No encryption key"):
        encrypt_value("test", key=None)


def test_key_from_env_var(monkeypatch):
    k = generate_key()
    monkeypatch.setenv(ENV_KEY_VAR, k)
    token = encrypt_value("from_env", key=None)
    assert decrypt_value(token, key=None) == "from_env"


def test_encrypt_env_set(key):
    env = {"FOO": "bar", "BAZ": "qux"}
    encrypted = encrypt_env_set(env, key=key)
    assert set(encrypted.keys()) == {"FOO", "BAZ"}
    assert encrypted["FOO"] != "bar"
    assert encrypted["BAZ"] != "qux"


def test_decrypt_env_set_roundtrip(key):
    env = {"API_KEY": "abc123", "DB_PASS": "s3cr3t"}
    encrypted = encrypt_env_set(env, key=key)
    decrypted = decrypt_env_set(encrypted, key=key)
    assert decrypted == env


def test_encrypt_empty_string(key):
    token = encrypt_value("", key=key)
    assert decrypt_value(token, key=key) == ""
