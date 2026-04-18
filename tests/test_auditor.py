"""Tests for envctl.auditor."""

import os
import pytest
from envctl.auditor import record_event, get_audit_log, clear_audit_log


@pytest.fixture(autouse=True)
def audit_file(tmp_path, monkeypatch):
    path = str(tmp_path / "audit.jsonl")
    monkeypatch.setenv("ENVCTL_AUDIT_FILE", path)
    yield path


def test_get_audit_log_empty_when_no_file():
    assert get_audit_log() == []


def test_record_and_get_event():
    record_event("save", "prod")
    events = get_audit_log()
    assert len(events) == 1
    assert events[0]["action"] == "save"
    assert events[0]["set"] == "prod"
    assert "ts" in events[0]


def test_record_with_detail():
    record_event("delete", "staging", detail="removed by user")
    events = get_audit_log()
    assert events[0]["detail"] == "removed by user"


def test_record_multiple_events():
    for name in ["a", "b", "c"]:
        record_event("save", name)
    events = get_audit_log()
    assert len(events) == 3
    assert [e["set"] for e in events] == ["a", "b", "c"]


def test_get_audit_log_respects_limit():
    for i in range(10):
        record_event("save", f"set{i}")
    events = get_audit_log(limit=3)
    assert len(events) == 3
    assert events[-1]["set"] == "set9"


def test_clear_audit_log(audit_file):
    record_event("save", "prod")
    clear_audit_log()
    assert not os.path.exists(audit_file)
    assert get_audit_log() == []
