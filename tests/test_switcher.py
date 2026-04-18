"""Tests for envctl.switcher module."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from envctl.switcher import (
    apply_set,
    get_active,
    set_active,
    switch_set,
    unapply_set,
    ACTIVE_FILE,
)


@pytest.fixture(autouse=True)
def tmp_active_file(tmp_path, monkeypatch):
    active = tmp_path / ".active"
    monkeypatch.setattr("envctl.switcher.ACTIVE_FILE", active)
    return active


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.load.return_value = {"FOO": "bar", "BAZ": "qux"}
    return store


def test_get_active_none_when():
    assert get_active() is None


def test_set_and_get_active(tmp_active_file):
    set_active("myproject")
    assert get_active() == "myproject"


def test_set_active_none_clears(tmp_active_file):
    set_active("something")
    set_active(None)
    assert get_active() is None


def test_apply_set_returns_vars(mock_store):
    result = apply_set("dev", mock_store)
    assert result == {"FOO": "bar", "BAZ": "qux"}
    mock_store.load.assert_called_once_with("dev")


def test_apply_set_sets_active(mock_store):
    apply_set("dev", mock_store)
    assert get_active() == "dev"


def test_apply_set_raises_on_missing(mock_store):
    mock_store.load.return_value = None
    with pytest.raises(KeyError, match="not found"):
        apply_set("ghost", mock_store)


def test_apply_set_does_not_set_active_on_missing(mock_store):
    """Active set should not be updated when the target set does not exist."""
    mock_store.load.return_value = None
    with pytest.raises(KeyError):
        apply_set("ghost", mock_store)
    assert get_active() is None


def test_unapply_set_returns_name(mock_store):
    set_active("staging")
    name = unapply_set(mock_store)
    assert name == "staging"
    assert get_active() is None


def test_unapply_set_when_none_active(mock_store):
    """unapply_set should return None gracefully when no set is active."""
    result = unapply_set(mock_store)
    assert result is None


def test_switch_set_changes_active(mock_store):
    set_active("old")
    result = switch_set("new", mock_store)
    assert result == {"FOO": "bar", "BAZ": "qux"}
    assert get_active() == "new"
