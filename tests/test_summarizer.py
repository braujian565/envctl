"""Tests for envctl.summarizer."""

from unittest.mock import MagicMock

import pytest

from envctl.summarizer import summarize_set, summarize_all, format_summary


CLEAN_ENV = {
    "DATABASE_URL": "postgres://localhost/mydb",
    "API_KEY": "supersecretvalue123!",
    "LOG_LEVEL": "INFO",
    "PORT": "8080",
}


def test_summarize_set_returns_name():
    report = summarize_set("production", CLEAN_ENV)
    assert report["name"] == "production"


def test_summarize_set_counts_keys():
    report = summarize_set("production", CLEAN_ENV)
    assert report["total_keys"] == len(CLEAN_ENV)


def test_summarize_set_detects_sensitive():
    report = summarize_set("production", CLEAN_ENV)
    # API_KEY is sensitive
    assert report["sensitive_keys"] >= 1


def test_summarize_set_has_score_and_grade():
    report = summarize_set("production", CLEAN_ENV)
    assert isinstance(report["score"], (int, float))
    assert report["grade"] in {"A", "B", "C", "D", "F"}


def test_summarize_set_has_categories():
    report = summarize_set("production", CLEAN_ENV)
    assert isinstance(report["categories"], dict)


def test_summarize_set_empty_env():
    report = summarize_set("empty", {})
    assert report["total_keys"] == 0
    assert report["sensitive_keys"] == 0
    assert report["lint_findings"] == 0


def test_summarize_all_returns_sorted():
    mock_store = MagicMock()
    mock_store.list_sets.return_value = ["staging", "dev", "production"]
    mock_store.load.return_value = {"PORT": "8080"}

    results = summarize_all(mock_store)
    names = [r["name"] for r in results]
    assert names == sorted(names)


def test_summarize_all_handles_none_load():
    mock_store = MagicMock()
    mock_store.list_sets.return_value = ["ghost"]
    mock_store.load.return_value = None  # missing set

    results = summarize_all(mock_store)
    assert results[0]["total_keys"] == 0


def test_format_summary_contains_name():
    report = summarize_set("staging", CLEAN_ENV)
    output = format_summary(report)
    assert "staging" in output


def test_format_summary_contains_score():
    report = summarize_set("staging", CLEAN_ENV)
    output = format_summary(report)
    assert "Score" in output
    assert report["grade"] in output


def test_format_summary_empty_categories():
    report = summarize_set("bare", {})
    output = format_summary(report)
    assert "(none detected)" in output
