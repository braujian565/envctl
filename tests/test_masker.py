"""Tests for envctl.masker."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envctl.masker import (
    format_mask_report,
    list_masked_keys,
    mask_env_set,
    mask_value,
)
from envctl.cli_masker import mask_group


# ---------------------------------------------------------------------------
# mask_value
# ---------------------------------------------------------------------------

def test_mask_value_empty_string_unchanged():
    assert mask_value("") == ""


def test_mask_value_short_value_fully_masked():
    # values shorter than _MIN_LEN_FOR_PARTIAL (8) get fully masked
    result = mask_value("abc")
    assert result == "***"


def test_mask_value_long_value_partial_mask():
    result = mask_value("supersecretvalue")
    assert result.startswith("sup")
    assert result.endswith("lue")
    assert "*" in result


def test_mask_value_full_flag_masks_everything():
    value = "supersecretvalue"
    result = mask_value(value, full=True)
    assert result == "*" * len(value)


def test_mask_value_preserves_length():
    value = "mypassword123"
    assert len(mask_value(value)) == len(value)


# ---------------------------------------------------------------------------
# mask_env_set
# ---------------------------------------------------------------------------

def test_mask_env_set_masks_sensitive_keys():
    env = {"DB_PASSWORD": "secret123", "APP_NAME": "myapp"}
    result = mask_env_set(env)
    assert result["APP_NAME"] == "myapp"  # not sensitive
    assert "*" in result["DB_PASSWORD"]


def test_mask_env_set_explicit_keys_only():
    env = {"DB_PASSWORD": "secret123", "APP_NAME": "myapp"}
    result = mask_env_set(env, keys=["APP_NAME"])
    assert "*" in result["APP_NAME"]
    assert result["DB_PASSWORD"] == "secret123"  # not in explicit list


def test_mask_env_set_full_mode():
    env = {"API_KEY": "longapikey9999"}
    result = mask_env_set(env, full=True)
    assert result["API_KEY"] == "*" * len("longapikey9999")


def test_mask_env_set_no_sensitive_keys_unchanged():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = mask_env_set(env)
    assert result == env


# ---------------------------------------------------------------------------
# list_masked_keys
# ---------------------------------------------------------------------------

def test_list_masked_keys_returns_sensitive():
    env = {"DB_PASSWORD": "x", "TOKEN": "y", "HOST": "z"}
    keys = list_masked_keys(env)
    assert "DB_PASSWORD" in keys
    assert "TOKEN" in keys
    assert "HOST" not in keys


def test_list_masked_keys_empty_env():
    assert list_masked_keys({}) == []


# ---------------------------------------------------------------------------
# format_mask_report
# ---------------------------------------------------------------------------

def test_format_mask_report_no_changes():
    env = {"HOST": "localhost"}
    report = format_mask_report(env, env)
    assert "No values were masked" in report


def test_format_mask_report_shows_changed_key():
    original = {"API_KEY": "plainvalue123456"}
    masked = mask_env_set(original)
    report = format_mask_report(original, masked)
    assert "API_KEY" in report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_store(tmp_path, monkeypatch):
    import envctl.cli_masker as cm
    import envctl.store as store_mod

    def fake_init(self, path=None):
        self._path = tmp_path / "store.json"
        store_mod.EnvStore._ensure_store(self)

    monkeypatch.setattr(store_mod.EnvStore, "__init__", fake_init)
    store = store_mod.EnvStore()
    store.save("prod", {"API_KEY": "supersecretkey99", "HOST": "example.com"})
    return store


def invoke(runner, *args):
    return runner.invoke(mask_group, list(args), catch_exceptions=False)


def test_cli_show_masks_sensitive(runner, mock_store):
    result = invoke(runner, "show", "prod")
    assert result.exit_code == 0
    assert "HOST=example.com" in result.output
    assert "supersecretkey99" not in result.output


def test_cli_show_set_not_found(runner, mock_store):
    result = runner.invoke(mask_group, ["show", "nonexistent"])
    assert result.exit_code != 0


def test_cli_keys_lists_sensitive(runner, mock_store):
    result = invoke(runner, "keys", "prod")
    assert result.exit_code == 0
    assert "API_KEY" in result.output


def test_cli_report_shows_table(runner, mock_store):
    result = invoke(runner, "report", "prod")
    assert result.exit_code == 0
    assert "API_KEY" in result.output
