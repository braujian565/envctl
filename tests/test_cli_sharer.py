"""Tests for envctl.cli_sharer."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from envctl.cli_sharer import share_group

SECRET = "test-secret-key"
ENV = {"API_KEY": "abc123", "HOST": "localhost"}


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_store():
    store = MagicMock()
    store.load.return_value = ENV
    store.save.return_value = None
    with patch("envctl.cli_sharer.EnvStore", return_value=store):
        yield store


def invoke(runner, *args, secret=SECRET, **kwargs):
    env_vars = {"ENVCTL_SHARE_SECRET": secret}
    return runner.invoke(share_group, list(args), env=env_vars, **kwargs)


def test_create_outputs_token(runner, mock_store):
    result = invoke(runner, "create", "prod")
    assert result.exit_code == 0
    assert len(result.output.strip()) > 20


def test_create_set_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "create", "missing")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_create_no_secret(runner, mock_store):
    result = runner.invoke(share_group, ["create", "prod"], env={})
    assert result.exit_code != 0
    assert "ENVCTL_SHARE_SECRET" in result.output


def test_inspect_valid_token(runner, mock_store):
    create_result = invoke(runner, "create", "prod", "--ttl", "3600")
    token = create_result.output.strip()
    result = invoke(runner, "inspect", token)
    assert result.exit_code == 0
    assert "prod" in result.output


def test_inspect_invalid_token(runner, mock_store):
    result = invoke(runner, "inspect", "garbage-token")
    assert result.exit_code != 0
    assert "Malformed" in result.output or "Error" in result.output


def test_import_saves_set(runner, mock_store):
    create_result = invoke(runner, "create", "prod")
    token = create_result.output.strip()
    result = invoke(runner, "import", token)
    assert result.exit_code == 0
    mock_store.save.assert_called_once()
    assert "prod" in result.output


def test_import_with_override_name(runner, mock_store):
    create_result = invoke(runner, "create", "prod")
    token = create_result.output.strip()
    result = invoke(runner, "import", token, "--as", "my-prod")
    assert result.exit_code == 0
    saved_name = mock_store.save.call_args[0][0]
    assert saved_name == "my-prod"
