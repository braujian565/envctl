"""Tests for envctl.exporter module."""

import pytest
from envctl.exporter import (
    export_bash,
    export_dotenv,
    export_fish,
    export_env_set,
    SUPPORTED_FORMATS,
)

SAMPLE = {"DB_HOST": "localhost", "API_KEY": 'abc"123'}


def test_supported_formats_list():
    assert "bash" in SUPPORTED_FORMATS
    assert "dotenv" in SUPPORTED_FORMATS
    assert "fish" in SUPPORTED_FORMATS


def test_export_bash_contains_export():
    result = export_bash(SAMPLE)
    assert 'export DB_HOST="localhost"' in result
    assert result.startswith("#!/usr/bin/env bash")


def test_export_bash_escapes_quotes():
    result = export_bash(SAMPLE)
    assert 'export API_KEY="abc\\"123"' in result


def test_export_dotenv_format():
    result = export_dotenv(SAMPLE)
    assert 'DB_HOST="localhost"' in result
    assert "export" not in result
    assert "set -x" not in result


def test_export_fish_format():
    result = export_fish(SAMPLE)
    assert 'set -x DB_HOST "localhost"' in result


def test_export_env_set_bash():
    result = export_env_set(SAMPLE, "bash")
    assert result is not None
    assert "export" in result


def test_export_env_set_dotenv():
    result = export_env_set(SAMPLE, "dotenv")
    assert result is not None
    assert "DB_HOST" in result


def test_export_env_set_fish():
    result = export_env_set(SAMPLE, "fish")
    assert result is not None
    assert "set -x" in result


def test_export_env_set_unknown_format():
    result = export_env_set(SAMPLE, "powershell")
    assert result is None


def test_export_empty_vars():
    result = export_bash({})
    assert result.strip() == "#!/usr/bin/env bash"
