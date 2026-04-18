"""Tests for envctl.linter."""

import pytest
from envctl.linter import lint_env_set, format_findings


def test_no_findings_for_clean_env():
    env = {"HOST": "localhost", "PORT": "8080", "DEBUG": "true"}
    assert lint_env_set(env) == []


def test_empty_value_warning():
    env = {"HOST": ""}
    findings = lint_env_set(env)
    codes = [f["code"] for f in findings]
    assert "EMPTY_VALUE" in codes


def test_long_value_warning():
    env = {"DATA": "x" * 300}
    findings = lint_env_set(env)
    codes = [f["code"] for f in findings]
    assert "LONG_VALUE" in codes


def test_weak_secret_warning():
    env = {"API_KEY": "abc"}
    findings = lint_env_set(env)
    codes = [f["code"] for f in findings]
    assert "WEAK_SECRET" in codes


def test_strong_secret_no_warning():
    env = {"API_KEY": "supersecretvalue123"}
    findings = lint_env_set(env)
    codes = [f["code"] for f in findings]
    assert "WEAK_SECRET" not in codes


def test_empty_secret_no_weak_secret_but_empty_value():
    env = {"SECRET": ""}
    findings = lint_env_set(env)
    codes = [f["code"] for f in findings]
    assert "EMPTY_VALUE" in codes
    assert "WEAK_SECRET" not in codes


def test_multiple_findings():
    env = {"TOKEN": "abc", "HOST": "", "DATA": "z" * 300}
    findings = lint_env_set(env)
    assert len(findings) >= 3


def test_format_findings_no_issues():
    assert format_findings([]) == "No issues found."


def test_format_findings_contains_code():
    findings = [{"key": "X", "level": "warning", "code": "EMPTY_VALUE", "message": "X has an empty value."}]
    result = format_findings(findings)
    assert "EMPTY_VALUE" in result
    assert "WARNING" in result


def test_finding_level_is_warning():
    env = {"PASSWORD": "ab"}
    findings = lint_env_set(env)
    for f in findings:
        assert f["level"] == "warning"
