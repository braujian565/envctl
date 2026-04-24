"""Tests for envctl.classifier."""

import pytest

from envctl.classifier import (
    classify_key,
    classify_env_set,
    overall_risk,
    format_classification_report,
    LOW,
    MEDIUM,
    HIGH,
    CRITICAL,
)


def test_classify_key_low():
    assert classify_key("APP_NAME") == LOW


def test_classify_key_medium():
    assert classify_key("AUTH_URL") == MEDIUM


def test_classify_key_high():
    assert classify_key("DB_PASSWORD") == HIGH


def test_classify_key_critical():
    assert classify_key("PROD_HOST") == CRITICAL


def test_classify_key_api_key_is_high():
    assert classify_key("STRIPE_API_KEY") == HIGH


def test_classify_key_token_is_high():
    assert classify_key("ACCESS_TOKEN") == HIGH


def test_classify_env_set_returns_all_keys():
    env = {"APP_NAME": "myapp", "DB_PASSWORD": "secret", "PROD_URL": "https://x"}
    result = classify_env_set(env)
    assert set(result.keys()) == {"APP_NAME", "DB_PASSWORD", "PROD_URL"}


def test_classify_env_set_correct_levels():
    env = {"APP_NAME": "myapp", "DB_PASSWORD": "secret", "PROD_URL": "https://x"}
    result = classify_env_set(env)
    assert result["APP_NAME"] == LOW
    assert result["DB_PASSWORD"] == HIGH
    assert result["PROD_URL"] == CRITICAL


def test_overall_risk_empty_is_low():
    assert overall_risk({}) == LOW


def test_overall_risk_all_low():
    assert overall_risk({"APP_NAME": "x", "VERSION": "1"}) == LOW


def test_overall_risk_returns_highest():
    env = {"APP_NAME": "x", "DB_PASSWORD": "s", "PROD_URL": "u"}
    assert overall_risk(env) == CRITICAL


def test_overall_risk_high_without_critical():
    env = {"APP_NAME": "x", "ACCESS_TOKEN": "t"}
    assert overall_risk(env) == HIGH


def test_format_classification_report_contains_overall():
    env = {"APP_NAME": "x", "DB_PASSWORD": "s"}
    report = format_classification_report(env)
    assert "Overall risk:" in report
    assert "HIGH" in report


def test_format_classification_report_lists_keys():
    env = {"APP_NAME": "x", "DB_PASSWORD": "s"}
    report = format_classification_report(env)
    assert "APP_NAME" in report
    assert "DB_PASSWORD" in report


def test_format_classification_report_empty_env():
    report = format_classification_report({})
    assert "LOW" in report
