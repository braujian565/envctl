"""Tests for envctl.importer module."""

import pytest
from pathlib import Path
from envctl.importer import parse_dotenv, parse_bash, import_env_set, SUPPORTED_FORMATS


def test_supported_formats_list():
    assert "dotenv" in SUPPORTED_FORMATS
    assert "bash" in SUPPORTED_FORMATS


def test_parse_dotenv_basic():
    text = "KEY=value\nFOO=bar\n"
    result = parse_dotenv(text)
    assert result == {"KEY": "value", "FOO": "bar"}


def test_parse_dotenv_ignores_comments():
    text = "# comment\nKEY=value\n"
    result = parse_dotenv(text)
    assert "KEY" in result
    assert len(result) == 1


def test_parse_dotenv_strips_quotes():
    text = 'KEY="hello world"\nFOO=\'bar\'\n'
    result = parse_dotenv(text)
    assert result["KEY"] == "hello world"
    assert result["FOO"] == "bar"


def test_parse_dotenv_ignores_blank_lines():
    text = "\nKEY=value\n\n"
    result = parse_dotenv(text)
    assert result == {"KEY": "value"}


def test_parse_bash_basic():
    text = 'export KEY="value"\nexport FOO=bar\n'
    result = parse_bash(text)
    assert result["KEY"] == "value"
    assert result["FOO"] == "bar"


def test_parse_bash_ignores_non_export_lines():
    text = "# comment\nexport KEY=val\necho hello\n"
    result = parse_bash(text)
    assert list(result.keys()) == ["KEY"]


def test_parse_bash_handles_quoted_values():
    text = "export MSG=\"hello world\"\n"
    result = parse_bash(text)
    assert result["MSG"] == "hello world"


def test_import_env_set_dotenv(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB=postgres\nPORT=5432\n")
    result = import_env_set(str(env_file), "dotenv")
    assert result == {"DB": "postgres", "PORT": "5432"}


def test_import_env_set_bash(tmp_path):
    env_file = tmp_path / "env.sh"
    env_file.write_text('export DB="postgres"\nexport PORT=5432\n')
    result = import_env_set(str(env_file), "bash")
    assert result["DB"] == "postgres"
    assert result["PORT"] == "5432"


def test_import_env_set_unsupported_format(tmp_path):
    env_file = tmp_path / "env.json"
    env_file.write_text('{"KEY": "val"}')
    with pytest.raises(ValueError, match="Unsupported format"):
        import_env_set(str(env_file), "json")
