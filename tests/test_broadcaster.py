"""Tests for envctl.broadcaster."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envctl import broadcaster


@pytest.fixture(autouse=True)
def _patch_channels_file(tmp_path, monkeypatch):
    fake = tmp_path / "broadcast_channels.json"
    monkeypatch.setattr(broadcaster, "_CHANNELS_FILE", fake)
    yield fake


def test_list_channels_empty_when_no_file():
    assert broadcaster.list_channels() == []


def test_add_channel_stdout():
    entry = broadcaster.add_channel("stdout", "-")
    assert entry["type"] == "stdout"
    assert entry["target"] == "-"
    assert entry["enabled"] is True


def test_add_channel_persisted():
    broadcaster.add_channel("file", "/tmp/out.log")
    assert len(broadcaster.list_channels()) == 1


def test_add_channel_no_duplicate():
    broadcaster.add_channel("stdout", "-")
    broadcaster.add_channel("stdout", "-")
    assert len(broadcaster.list_channels()) == 1


def test_add_channel_invalid_type_raises():
    with pytest.raises(ValueError, match="Unknown channel type"):
        broadcaster.add_channel("sms", "555-1234")


def test_remove_channel_existing():
    broadcaster.add_channel("stdout", "-")
    result = broadcaster.remove_channel("stdout", "-")
    assert result is True
    assert broadcaster.list_channels() == []


def test_remove_channel_missing_returns_false():
    result = broadcaster.remove_channel("stdout", "-")
    assert result is False


def test_broadcast_stdout(capsys):
    broadcaster.add_channel("stdout", "-")
    reports = broadcaster.broadcast("switch", "prod")
    captured = capsys.readouterr()
    assert "switch" in captured.out
    assert "prod" in captured.out
    assert reports == ["stdout:ok"]


def test_broadcast_file(tmp_path):
    out_file = tmp_path / "events.log"
    broadcaster.add_channel("file", str(out_file))
    broadcaster.broadcast("save", "dev", {"key": "FOO"})
    content = out_file.read_text()
    data = json.loads(content.strip())
    assert data["event"] == "save"
    assert data["set"] == "dev"
    assert data["detail"] == {"key": "FOO"}


def test_broadcast_no_channels_returns_empty():
    reports = broadcaster.broadcast("delete", "staging")
    assert reports == []


def test_broadcast_error_captured(tmp_path):
    broadcaster.add_channel("file", "/nonexistent_dir/out.log")
    reports = broadcaster.broadcast("test", "dev")
    assert len(reports) == 1
    assert "error" in reports[0]
