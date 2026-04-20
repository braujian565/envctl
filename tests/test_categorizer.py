"""Tests for envctl.categorizer."""

import pytest
from envctl.categorizer import (
    categorize_key,
    categorize_env_set,
    summarize_categories,
    format_category_report,
)


def test_categorize_key_database():
    assert categorize_key("DB_HOST") == "database"
    assert categorize_key("DATABASE_URL") == "database"
    assert categorize_key("POSTGRES_USER") == "database"


def test_categorize_key_auth():
    assert categorize_key("JWT_SECRET") == "auth"
    assert categorize_key("API_KEY") == "auth"
    assert categorize_key("AUTH_TOKEN") == "auth"


def test_categorize_key_infra():
    assert categorize_key("APP_HOST") == "infra"
    assert categorize_key("SERVER_PORT") == "infra"
    assert categorize_key("SERVICE_URL") == "infra"


def test_categorize_key_cloud():
    assert categorize_key("AWS_ACCESS_KEY_ID") == "cloud"
    assert categorize_key("GCP_PROJECT") == "cloud"
    assert categorize_key("S3_BUCKET") == "cloud"


def test_categorize_key_logging():
    assert categorize_key("LOG_LEVEL") == "logging"
    assert categorize_key("DEBUG") == "logging"


def test_categorize_key_feature():
    assert categorize_key("FEATURE_DARK_MODE") == "feature"
    assert categorize_key("ENABLE_CACHE") == "feature"


def test_categorize_key_other():
    assert categorize_key("APP_NAME") == "other"
    assert categorize_key("ENVIRONMENT") == "other"


def test_categorize_env_set_groups_correctly():
    env = {
        "DB_HOST": "localhost",
        "JWT_SECRET": "s3cr3t",
        "APP_NAME": "myapp",
    }
    result = categorize_env_set(env)
    assert "DB_HOST" in result["database"]
    assert "JWT_SECRET" in result["auth"]
    assert "APP_NAME" in result["other"]


def test_categorize_env_set_empty():
    assert categorize_env_set({}) == {}


def test_summarize_categories_sorted_by_count():
    env = {
        "DB_HOST": "h",
        "DB_PORT": "5432",
        "JWT_SECRET": "x",
    }
    rows = summarize_categories(env)
    assert rows[0][0] == "database"
    assert rows[0][1] == 2


def test_format_category_report_contains_keys():
    env = {"DB_HOST": "localhost", "APP_NAME": "myapp"}
    report = format_category_report(env)
    assert "DB_HOST" in report
    assert "APP_NAME" in report
    assert "[database]" in report
    assert "[other]" in report


def test_format_category_report_empty():
    assert format_category_report({}) == "No variables found."
