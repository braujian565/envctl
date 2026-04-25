"""Tests for envctl.stamper."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envctl.stamper import (
    get_stamp,
    list_all_stamps,
    list_stamps,
    remove_stamp,
    stamp_set,
)


@pytest.fixture()
def stamps_file(tmp_path: Path) -> Path:
    return tmp_path / "stamps.json"


def test_stamp_set_returns_entry(stamps_file: Path) -> None:
    entry = stamp_set("prod", "deployed", stamps_file=stamps_file)
    assert entry["set"] == "prod"
    assert entry["label"] == "deployed"
    assert "T" in entry["timestamp"]  # ISO format contains 'T'


def test_stamp_set_persisted(stamps_file: Path) -> None:
    stamp_set("dev", "updated", stamps_file=stamps_file)
    raw = json.loads(stamps_file.read_text())
    assert "dev" in raw
    assert "updated" in raw["dev"]


def test_get_stamp_returns_none_when_missing(stamps_file: Path) -> None:
    result = get_stamp("nonexistent", "updated", stamps_file=stamps_file)
    assert result is None


def test_get_stamp_returns_timestamp(stamps_file: Path) -> None:
    stamp_set("staging", "created", stamps_file=stamps_file)
    ts = get_stamp("staging", "created", stamps_file=stamps_file)
    assert ts is not None
    assert ts.endswith("+00:00") or ts.endswith("Z") or "T" in ts


def test_multiple_labels_on_same_set(stamps_file: Path) -> None:
    stamp_set("prod", "created", stamps_file=stamps_file)
    stamp_set("prod", "deployed", stamps_file=stamps_file)
    stamps = list_stamps("prod", stamps_file=stamps_file)
    assert "created" in stamps
    assert "deployed" in stamps


def test_list_stamps_empty_for_unknown_set(stamps_file: Path) -> None:
    stamps = list_stamps("ghost", stamps_file=stamps_file)
    assert stamps == {}


def test_remove_stamp_existing(stamps_file: Path) -> None:
    stamp_set("dev", "updated", stamps_file=stamps_file)
    removed = remove_stamp("dev", "updated", stamps_file=stamps_file)
    assert removed is True
    assert get_stamp("dev", "updated", stamps_file=stamps_file) is None


def test_remove_stamp_nonexistent_returns_false(stamps_file: Path) -> None:
    removed = remove_stamp("dev", "never_set", stamps_file=stamps_file)
    assert removed is False


def test_remove_last_label_removes_set_entry(stamps_file: Path) -> None:
    stamp_set("dev", "only", stamps_file=stamps_file)
    remove_stamp("dev", "only", stamps_file=stamps_file)
    raw = json.loads(stamps_file.read_text())
    assert "dev" not in raw


def test_list_all_stamps_aggregates(stamps_file: Path) -> None:
    stamp_set("dev", "created", stamps_file=stamps_file)
    stamp_set("prod", "deployed", stamps_file=stamps_file)
    rows = list_all_stamps(stamps_file=stamps_file)
    sets = {r["set"] for r in rows}
    assert {"dev", "prod"} == sets


def test_list_all_stamps_empty_when_no_file(stamps_file: Path) -> None:
    rows = list_all_stamps(stamps_file=stamps_file)
    assert rows == []
