"""Tests for envctl.pinecone."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envctl.pinecone import (
    add_required_key,
    check_required_keys,
    list_required_keys,
    missing_keys,
    remove_required_key,
)


@pytest.fixture()
def req_file(tmp_path: Path) -> Path:
    return tmp_path / "required_keys.json"


def test_list_required_keys_empty_when_no_file(req_file: Path) -> None:
    assert list_required_keys(req_file) == []


def test_add_required_key_returns_sorted_list(req_file: Path) -> None:
    result = add_required_key("DATABASE_URL", req_file)
    assert "DATABASE_URL" in result


def test_add_required_key_persisted(req_file: Path) -> None:
    add_required_key("SECRET_KEY", req_file)
    assert "SECRET_KEY" in list_required_keys(req_file)


def test_add_required_key_no_duplicate(req_file: Path) -> None:
    add_required_key("API_KEY", req_file)
    add_required_key("API_KEY", req_file)
    assert list_required_keys(req_file).count("API_KEY") == 1


def test_remove_required_key_existing(req_file: Path) -> None:
    add_required_key("TOKEN", req_file)
    removed = remove_required_key("TOKEN", req_file)
    assert removed is True
    assert "TOKEN" not in list_required_keys(req_file)


def test_remove_required_key_nonexistent(req_file: Path) -> None:
    removed = remove_required_key("MISSING", req_file)
    assert removed is False


def test_check_required_keys_all_present(req_file: Path) -> None:
    add_required_key("A", req_file)
    add_required_key("B", req_file)
    result = check_required_keys({"A": "1", "B": "2", "C": "3"}, req_file)
    assert result == {"A": True, "B": True}


def test_check_required_keys_some_missing(req_file: Path) -> None:
    add_required_key("A", req_file)
    add_required_key("B", req_file)
    result = check_required_keys({"A": "1"}, req_file)
    assert result["A"] is True
    assert result["B"] is False


def test_missing_keys_returns_absent(req_file: Path) -> None:
    add_required_key("X", req_file)
    add_required_key("Y", req_file)
    assert missing_keys({"X": "hello"}, req_file) == ["Y"]


def test_missing_keys_empty_when_all_present(req_file: Path) -> None:
    add_required_key("Z", req_file)
    assert missing_keys({"Z": "ok"}, req_file) == []
