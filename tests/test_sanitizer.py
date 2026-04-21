"""Tests for envctl.sanitizer."""

import pytest
from envctl.sanitizer import (
    is_sensitive_key,
    sanitize_env_set,
    sanitize_all,
    format_sanitize_report,
    REDACT_PLACEHOLDER,
)


def test_is_sensitive_key_password():
    assert is_sensitive_key("DB_PASSWORD") is True


def test_is_sensitive_key_token():
    assert is_sensitive_key("GITHUB_TOKEN") is True


def test_is_sensitive_key_api_key():
    assert is_sensitive_key("STRIPE_API_KEY") is True


def test_is_sensitive_key_secret():
    assert is_sensitive_key("APP_SECRET") is True


def test_is_sensitive_key_safe():
    assert is_sensitive_key("APP_HOST") is False
    assert is_sensitive_key("PORT") is False
    assert is_sensitive_key("LOG_LEVEL") is False


def test_sanitize_env_set_redacts_sensitive():
    env = {"DB_PASSWORD": "hunter2", "HOST": "localhost"}
    sanitized, redacted = sanitize_env_set(env)
    assert sanitized["DB_PASSWORD"] == REDACT_PLACEHOLDER
    assert sanitized["HOST"] == "localhost"
    assert "DB_PASSWORD" in redacted
    assert "HOST" not in redacted


def test_sanitize_env_set_no_sensitive_keys():
    env = {"HOST": "localhost", "PORT": "5432"}
    sanitized, redacted = sanitize_env_set(env)
    assert sanitized == env
    assert redacted == []


def test_sanitize_env_set_all_sensitive():
    env = {"SECRET": "abc", "TOKEN": "xyz"}
    sanitized, redacted = sanitize_env_set(env)
    assert all(v == REDACT_PLACEHOLDER for v in sanitized.values())
    assert set(redacted) == {"SECRET", "TOKEN"}


def test_sanitize_all_multiple_sets():
    sets = {
        "prod": {"DB_PASSWORD": "s3cr3t", "HOST": "db.prod"},
        "dev": {"HOST": "localhost"},
    }
    results = sanitize_all(sets)
    assert results["prod"][1] == ["DB_PASSWORD"]
    assert results["dev"][1] == []


def test_format_sanitize_report_with_redacted():
    report = format_sanitize_report("prod", ["DB_PASSWORD", "TOKEN"])
    assert "prod" in report
    assert "2" in report
    assert "DB_PASSWORD" in report


def test_format_sanitize_report_no_redacted():
    report = format_sanitize_report("dev", [])
    assert "no sensitive" in report.lower()
