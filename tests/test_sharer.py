"""Tests for envctl.sharer."""
from __future__ import annotations

import time

import pytest

from envctl.sharer import (
    create_share_token,
    decode_share_token,
    share_summary,
)

SECRET = "test-secret-key"
ENV = {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_create_returns_string():
    token = create_share_token(ENV, "prod", SECRET)
    assert isinstance(token, str)
    assert len(token) > 0


def test_roundtrip_preserves_env():
    token = create_share_token(ENV, "prod", SECRET)
    payload = decode_share_token(token, SECRET)
    assert payload["env"] == ENV


def test_roundtrip_preserves_set_name():
    token = create_share_token(ENV, "staging", SECRET)
    payload = decode_share_token(token, SECRET)
    assert payload["set"] == "staging"


def test_roundtrip_preserves_meta():
    token = create_share_token(ENV, "dev", SECRET, meta={"note": "hello"})
    payload = decode_share_token(token, SECRET)
    assert payload["meta"]["note"] == "hello"


def test_wrong_secret_raises():
    token = create_share_token(ENV, "prod", SECRET)
    with pytest.raises(ValueError, match="signature is invalid"):
        decode_share_token(token, "wrong-secret")


def test_expired_token_raises():
    token = create_share_token(ENV, "prod", SECRET, ttl=-1)
    with pytest.raises(ValueError, match="expired"):
        decode_share_token(token, SECRET, verify_expiry=True)


def test_expired_token_skip_verify():
    token = create_share_token(ENV, "prod", SECRET, ttl=-1)
    payload = decode_share_token(token, SECRET, verify_expiry=False)
    assert payload["env"] == ENV


def test_malformed_token_raises():
    with pytest.raises(ValueError, match="Malformed"):
        decode_share_token("not-a-valid-token!!", SECRET)


def test_share_summary_contains_set_name():
    token = create_share_token(ENV, "prod", SECRET, ttl=120)
    payload = decode_share_token(token, SECRET)
    summary = share_summary(payload)
    assert "prod" in summary


def test_share_summary_contains_key_count():
    token = create_share_token(ENV, "prod", SECRET)
    payload = decode_share_token(token, SECRET)
    summary = share_summary(payload)
    assert str(len(ENV)) in summary


def test_iat_is_recent():
    before = int(time.time())
    token = create_share_token(ENV, "prod", SECRET)
    after = int(time.time())
    payload = decode_share_token(token, SECRET)
    assert before <= payload["iat"] <= after
