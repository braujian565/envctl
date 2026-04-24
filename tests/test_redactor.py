"""Tests for envctl.redactor."""

from __future__ import annotations

import pytest

from envctl.redactor import (
    format_redact_report,
    list_sensitive_keys,
    redact_env_set,
    redact_value,
)


class TestRedactValue:
    def test_safe_key_unchanged(self):
        assert redact_value("APP_NAME", "myapp") == "myapp"

    def test_sensitive_key_masked(self):
        result = redact_value("DB_PASSWORD", "s3cr3t")
        assert result == "***REDACTED***"

    def test_token_key_masked(self):
        assert redact_value("API_TOKEN", "abc123") == "***REDACTED***"

    def test_empty_value_not_masked(self):
        assert redact_value("DB_PASSWORD", "") == ""

    def test_partial_reveals_last_chars(self):
        result = redact_value("SECRET_KEY", "abcdefgh", partial=True)
        assert result.endswith("efgh")
        assert result.startswith("****")

    def test_partial_short_value_fully_masked(self):
        result = redact_value("SECRET_KEY", "ab", partial=True)
        assert result == "***REDACTED***"


class TestRedactEnvSet:
    def test_masks_sensitive_leaves_safe(self):
        env = {"APP_NAME": "web", "DB_PASSWORD": "hunter2", "PORT": "8080"}
        result = redact_env_set(env)
        assert result["APP_NAME"] == "web"
        assert result["PORT"] == "8080"
        assert result["DB_PASSWORD"] == "***REDACTED***"

    def test_forced_keys_always_redacted(self):
        env = {"MY_CUSTOM": "visible", "OTHER": "also_visible"}
        result = redact_env_set(env, keys=["MY_CUSTOM"])
        assert result["MY_CUSTOM"] == "***REDACTED***"
        assert result["OTHER"] == "also_visible"

    def test_partial_mode_propagated(self):
        env = {"API_SECRET": "abcdefghij"}
        result = redact_env_set(env, partial=True)
        assert result["API_SECRET"].endswith("ghij")

    def test_returns_copy_not_mutated(self):
        env = {"DB_PASSWORD": "secret"}
        result = redact_env_set(env)
        assert env["DB_PASSWORD"] == "secret"
        assert result["DB_PASSWORD"] != "secret"


class TestListSensitiveKeys:
    def test_detects_password(self):
        env = {"DB_PASSWORD": "x", "HOST": "localhost"}
        assert "DB_PASSWORD" in list_sensitive_keys(env)
        assert "HOST" not in list_sensitive_keys(env)

    def test_empty_env_returns_empty(self):
        assert list_sensitive_keys({}) == []

    def test_all_safe_returns_empty(self):
        env = {"APP": "1", "PORT": "3000"}
        assert list_sensitive_keys(env) == []


class TestFormatRedactReport:
    def test_contains_key_header(self):
        report = format_redact_report({"APP": "web"})
        assert "KEY" in report

    def test_safe_value_visible(self):
        report = format_redact_report({"APP_NAME": "myapp"})
        assert "myapp" in report

    def test_sensitive_value_masked(self):
        report = format_redact_report({"DB_PASSWORD": "s3cr3t"})
        assert "s3cr3t" not in report
        assert "REDACTED" in report
