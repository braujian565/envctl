"""Tests for envctl.expirator."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envctl.expirator import (
    get_expiry,
    is_expired,
    list_expiries,
    remove_expiry,
    set_expiry,
)


@pytest.fixture()
def expiry_file(tmp_path: Path) -> Path:
    return tmp_path / "expiry.json"


def test_get_expiry_returns_none_when_no_file(expiry_file):
    assert get_expiry("prod", path=expiry_file) is None


def test_set_expiry_returns_entry(expiry_file):
    entry = set_expiry("prod", 3600, path=expiry_file)
    assert entry["set_name"] == "prod"
    assert entry["ttl_seconds"] == 3600
    assert "expires_at" in entry


def test_set_expiry_persisted(expiry_file):
    set_expiry("staging", 600, path=expiry_file)
    loaded = get_expiry("staging", path=expiry_file)
    assert loaded is not None
    assert loaded["ttl_seconds"] == 600


def test_get_expiry_returns_none_for_unknown(expiry_file):
    set_expiry("prod", 3600, path=expiry_file)
    assert get_expiry("dev", path=expiry_file) is None


def test_is_expired_false_for_future(expiry_file):
    set_expiry("prod", 9999, path=expiry_file)
    assert is_expired("prod", path=expiry_file) is False


def test_is_expired_true_for_past(expiry_file):
    set_expiry("old", 1, path=expiry_file)
    # Manually backdate the entry
    import json
    from datetime import datetime, timedelta, timezone
    data = json.loads(expiry_file.read_text())
    data["old"]["expires_at"] = (
        datetime.now(timezone.utc) - timedelta(seconds=10)
    ).isoformat()
    expiry_file.write_text(json.dumps(data))
    assert is_expired("old", path=expiry_file) is True


def test_is_expired_false_when_no_entry(expiry_file):
    assert is_expired("ghost", path=expiry_file) is False


def test_remove_expiry_existing(expiry_file):
    set_expiry("prod", 3600, path=expiry_file)
    result = remove_expiry("prod", path=expiry_file)
    assert result is True
    assert get_expiry("prod", path=expiry_file) is None


def test_remove_expiry_nonexistent(expiry_file):
    assert remove_expiry("ghost", path=expiry_file) is False


def test_list_expiries_empty(expiry_file):
    assert list_expiries(path=expiry_file) == []


def test_list_expiries_sorted_by_time(expiry_file):
    set_expiry("z_set", 7200, path=expiry_file)
    set_expiry("a_set", 60, path=expiry_file)
    entries = list_expiries(path=expiry_file)
    assert len(entries) == 2
    assert entries[0]["set_name"] == "a_set"  # shorter TTL expires first
