"""Tests for envctl.history module."""

import json
import pytest
from pathlib import Path
from envctl.history import record_switch, get_history, clear_history, MAX_HISTORY


@pytest.fixture
def history_file(tmp_path):
    return tmp_path / "history.json"


def test_get_history_empty_when_no_file(history_file):
    assert get_history(history_file=history_file) == []


def test_record_and_get_history(history_file):
    record_switch("prod", None, history_file=history_file)
    entries = get_history(history_file=history_file)
    assert len(entries) == 1
    assert entries[0]["to"] == "prod"
    assert entries[0]["from"] is None


def test_record_multiple_switches(history_file):
    record_switch("dev", None, history_file=history_file)
    record_switch("staging", "dev", history_file=history_file)
    record_switch("prod", "staging", history_file=history_file)
    entries = get_history(limit=10, history_file=history_file)
    assert len(entries) == 3
    assert entries[-1]["to"] == "prod"
    assert entries[-1]["from"] == "staging"


def test_get_history_respects_limit(history_file):
    for i in range(10):
        record_switch(f"set{i}", None, history_file=history_file)
    entries = get_history(limit=3, history_file=history_file)
    assert len(entries) == 3
    assert entries[-1]["to"] == "set9"


def test_history_capped_at_max(history_file):
    for i in range(MAX_HISTORY + 10):
        record_switch(f"set{i}", None, history_file=history_file)
    raw = json.loads(history_file.read_text())
    assert len(raw) == MAX_HISTORY


def test_clear_history(history_file):
    record_switch("dev", None, history_file=history_file)
    clear_history(history_file=history_file)
    assert get_history(history_file=history_file) == []


def test_history_entry_has_timestamp(history_file):
    record_switch("dev", None, history_file=history_file)
    entries = get_history(history_file=history_file)
    assert "timestamp" in entries[0]
    assert entries[0]["timestamp"]  # non-empty


def test_record_unset_switch(history_file):
    record_switch(None, "prod", history_file=history_file)
    entries = get_history(history_file=history_file)
    assert entries[0]["to"] is None
    assert entries[0]["from"] == "prod"
