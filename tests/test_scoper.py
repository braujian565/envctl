"""Tests for envctl.scoper."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envctl.scoper import (
    SCOPES,
    find_by_scope,
    get_scope,
    list_scopes,
    remove_scope,
    resolve_scope_priority,
    set_scope,
)


@pytest.fixture()
def scope_file(tmp_path: Path) -> Path:
    return tmp_path / "scopes.json"


def test_list_scopes_empty_when_no_file(scope_file: Path) -> None:
    assert list_scopes(scope_file) == {}


def test_set_scope_returns_mapping(scope_file: Path) -> None:
    result = set_scope("prod", "global", scope_file)
    assert result == {"prod": "global"}


def test_set_scope_persisted(scope_file: Path) -> None:
    set_scope("staging", "team", scope_file)
    data = json.loads(scope_file.read_text())
    assert data["staging"] == "team"


def test_set_scope_invalid_raises(scope_file: Path) -> None:
    with pytest.raises(ValueError, match="Invalid scope"):
        set_scope("dev", "unknown", scope_file)


def test_get_scope_returns_assigned(scope_file: Path) -> None:
    set_scope("dev", "local", scope_file)
    assert get_scope("dev", scope_file) == "local"


def test_get_scope_returns_none_when_missing(scope_file: Path) -> None:
    assert get_scope("nonexistent", scope_file) is None


def test_remove_scope_existing(scope_file: Path) -> None:
    set_scope("dev", "project", scope_file)
    removed = remove_scope("dev", scope_file)
    assert removed is True
    assert get_scope("dev", scope_file) is None


def test_remove_scope_missing_returns_false(scope_file: Path) -> None:
    assert remove_scope("ghost", scope_file) is False


def test_find_by_scope_returns_matching(scope_file: Path) -> None:
    set_scope("a", "local", scope_file)
    set_scope("b", "global", scope_file)
    set_scope("c", "local", scope_file)
    result = find_by_scope("local", scope_file)
    assert sorted(result) == ["a", "c"]


def test_find_by_scope_invalid_raises(scope_file: Path) -> None:
    with pytest.raises(ValueError):
        find_by_scope("invalid", scope_file)


def test_resolve_scope_priority_orders_correctly(scope_file: Path) -> None:
    set_scope("g", "global", scope_file)
    set_scope("t", "team", scope_file)
    set_scope("l", "local", scope_file)
    ordered = resolve_scope_priority(["g", "t", "l"], scope_file)
    assert ordered == ["l", "t", "g"]


def test_resolve_scope_priority_unscoped_last(scope_file: Path) -> None:
    set_scope("scoped", "project", scope_file)
    ordered = resolve_scope_priority(["unscoped", "scoped"], scope_file)
    assert ordered[0] == "scoped"
    assert ordered[-1] == "unscoped"
