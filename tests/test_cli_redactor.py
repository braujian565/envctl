"""Tests for envctl.cli_redactor."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from envctl.cli_redactor import redact_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_store(tmp_path, monkeypatch):
    store = MagicMock()
    monkeypatch.setattr("envctl.cli_redactor.EnvStore", lambda *a, **kw: store)
    return store


def invoke(runner, *args):
    return runner.invoke(redact_group, list(args), catch_exceptions=False)


class TestShowCommand:
    def test_show_set_not_found(self, runner, mock_store):
        mock_store.load.return_value = None
        result = invoke(runner, "show", "missing")
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_show_masks_password(self, runner, mock_store):
        mock_store.load.return_value = {"DB_PASSWORD": "secret", "APP": "web"}
        result = invoke(runner, "show", "prod")
        assert result.exit_code == 0
        assert "secret" not in result.output
        assert "REDACTED" in result.output
        assert "web" in result.output

    def test_show_partial_flag(self, runner, mock_store):
        mock_store.load.return_value = {"API_TOKEN": "abcdefghij"}
        result = invoke(runner, "show", "prod", "--partial")
        assert result.exit_code == 0
        assert "ghij" in result.output


class TestKeysCommand:
    def test_keys_no_sensitive(self, runner, mock_store):
        mock_store.load.return_value = {"APP": "web", "PORT": "8080"}
        result = invoke(runner, "keys", "dev")
        assert result.exit_code == 0
        assert "No sensitive" in result.output

    def test_keys_lists_sensitive(self, runner, mock_store):
        mock_store.load.return_value = {"DB_PASSWORD": "x", "APP": "y"}
        result = invoke(runner, "keys", "dev")
        assert result.exit_code == 0
        assert "DB_PASSWORD" in result.output
        assert "APP" not in result.output

    def test_keys_set_not_found(self, runner, mock_store):
        mock_store.load.return_value = None
        result = invoke(runner, "keys", "ghost")
        assert result.exit_code == 1


class TestExportCommand:
    def test_export_dotenv_format(self, runner, mock_store):
        mock_store.load.return_value = {"APP": "web", "DB_PASSWORD": "s3cr3t"}
        result = invoke(runner, "export", "prod")
        assert result.exit_code == 0
        assert "APP=web" in result.output
        assert "s3cr3t" not in result.output

    def test_export_set_not_found(self, runner, mock_store):
        mock_store.load.return_value = None
        result = invoke(runner, "export", "nope")
        assert result.exit_code == 1
