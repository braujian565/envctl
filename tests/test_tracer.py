"""Tests for envctl.tracer."""

import json
import pytest
from pathlib import Path
from envctl import tracer


@pytest.fixture(autouse=True)
def tmp_trace(tmp_path, monkeypatch):
    trace_file = tmp_path / "trace.json"
    monkeypatch.setenv("ENVCTL_TRACE_FILE", str(trace_file))
    yield trace_file


def test_get_trace_empty_when_no_file(tmp_trace):
    assert get_trace_result := tracer.get_trace() == []
    assert get_trace_result == []


def test_record_access_returns_entry():
    entry = tracer.record_access("prod", action="read")
    assert entry["set"] == "prod"
    assert entry["action"] == "read"
    assert "timestamp" in entry


def test_record_access_persisted(tmp_trace):
    tracer.record_access("staging", action="export")
    data = json.loads(tmp_trace.read_text())
    assert len(data) == 1
    assert data[0]["set"] == "staging"


def test_record_access_with_detail():
    entry = tracer.record_access("dev", action="switch", detail="from prod")
    assert entry["detail"] == "from prod"


def test_get_trace_filtered_by_set():
    tracer.record_access("prod")
    tracer.record_access("dev")
    tracer.record_access("prod")
    results = tracer.get_trace(set_name="prod")
    assert len(results) == 2
    assert all(e["set"] == "prod" for e in results)


def test_get_trace_respects_limit():
    for _ in range(10):
        tracer.record_access("prod")
    results = tracer.get_trace(limit=3)
    assert len(results) == 3


def test_clear_trace_all():
    tracer.record_access("prod")
    tracer.record_access("dev")
    removed = tracer.clear_trace()
    assert removed == 2
    assert tracer.get_trace() == []


def test_clear_trace_by_set():
    tracer.record_access("prod")
    tracer.record_access("dev")
    tracer.record_access("prod")
    removed = tracer.clear_trace(set_name="prod")
    assert removed == 2
    remaining = tracer.get_trace()
    assert len(remaining) == 1
    assert remaining[0]["set"] == "dev"


def test_most_accessed_order():
    for _ in range(3):
        tracer.record_access("prod")
    for _ in range(5):
        tracer.record_access("dev")
    tracer.record_access("staging")
    top = tracer.most_accessed(limit=3)
    assert top[0] == ("dev", 5)
    assert top[1] == ("prod", 3)
    assert top[2] == ("staging", 1)


def test_most_accessed_empty():
    assert tracer.most_accessed() == []
