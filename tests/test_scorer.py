import pytest
from envctl.scorer import score_env_set, format_score_report, _grade


def test_empty_env_scores_zero():
    report = score_env_set({})
    assert report["score"] == 0
    assert report["grade"] == "F"
    assert "Empty env set" in report["issues"][0]


def test_clean_env_scores_high():
    env = {"DATABASE_URL": "postgres://localhost/db", "APP_ENV": "production"}
    report = score_env_set(env)
    assert report["score"] >= 90
    assert report["grade"] == "A"
    assert report["issues"] == []


def test_empty_value_penalises_completeness():
    env = {"APP_ENV": ""}
    report = score_env_set(env)
    assert report["breakdown"]["completeness"] < 100
    assert any("Empty values" in i for i in report["issues"])


def test_lowercase_key_penalises_consistency():
    env = {"app_env": "prod"}
    report = score_env_set(env)
    assert report["breakdown"]["consistency"] < 100
    assert any("Non-uppercase" in i for i in report["issues"])


def test_weak_secret_penalises_security():
    env = {"SECRET_KEY": "short"}
    report = score_env_set(env)
    assert report["breakdown"]["security"] < 100
    assert any("Weak secret" in i for i in report["issues"])


def test_strong_secret_no_security_penalty():
    env = {"SECRET_KEY": "a-very-long-and-secure-secret-value-123"}
    report = score_env_set(env)
    assert report["breakdown"]["security"] == 100


def test_grade_boundaries():
    assert _grade(95) == "A"
    assert _grade(80) == "B"
    assert _grade(65) == "C"
    assert _grade(45) == "D"
    assert _grade(20) == "F"


def test_format_score_report_contains_score():
    env = {"APP": "val"}
    report = score_env_set(env)
    text = format_score_report(report)
    assert "Score" in text
    assert "Grade" in text
    assert "completeness" in text
