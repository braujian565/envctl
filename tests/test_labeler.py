"""Tests for envctl.labeler."""
from __future__ import annotations

import pytest

from envctl.labeler import (
    find_by_label,
    get_labels,
    list_all_labels,
    remove_label,
    set_label,
)


@pytest.fixture()
def labels_file(tmp_path):
    return tmp_path / "labels.json"


def test_get_labels_returns_empty_when_no_file(labels_file):
    assert get_labels("myapp", path=labels_file) == {}


def test_set_label_creates_entry(labels_file):
    result = set_label("myapp", "env", "production", path=labels_file)
    assert result == {"env": "production"}


def test_set_label_persisted(labels_file):
    set_label("myapp", "team", "backend", path=labels_file)
    assert get_labels("myapp", path=labels_file)["team"] == "backend"


def test_set_label_overwrites_existing(labels_file):
    set_label("myapp", "env", "staging", path=labels_file)
    set_label("myapp", "env", "production", path=labels_file)
    assert get_labels("myapp", path=labels_file)["env"] == "production"


def test_set_label_preserves_other_labels(labels_file):
    set_label("myapp", "env", "prod", path=labels_file)
    set_label("myapp", "team", "ops", path=labels_file)
    labels = get_labels("myapp", path=labels_file)
    assert labels["env"] == "prod"
    assert labels["team"] == "ops"


def test_remove_label_existing_returns_true(labels_file):
    set_label("myapp", "env", "prod", path=labels_file)
    assert remove_label("myapp", "env", path=labels_file) is True


def test_remove_label_removes_from_store(labels_file):
    set_label("myapp", "env", "prod", path=labels_file)
    remove_label("myapp", "env", path=labels_file)
    assert "env" not in get_labels("myapp", path=labels_file)


def test_remove_label_missing_returns_false(labels_file):
    assert remove_label("myapp", "nonexistent", path=labels_file) is False


def test_find_by_label_key_only(labels_file):
    set_label("app1", "env", "prod", path=labels_file)
    set_label("app2", "env", "staging", path=labels_file)
    set_label("app3", "team", "ops", path=labels_file)
    result = find_by_label("env", path=labels_file)
    assert set(result) == {"app1", "app2"}


def test_find_by_label_key_and_value(labels_file):
    set_label("app1", "env", "prod", path=labels_file)
    set_label("app2", "env", "staging", path=labels_file)
    result = find_by_label("env", "prod", path=labels_file)
    assert result == ["app1"]


def test_find_by_label_no_match_returns_empty(labels_file):
    assert find_by_label("missing", path=labels_file) == []


def test_list_all_labels_returns_all(labels_file):
    set_label("a", "x", "1", path=labels_file)
    set_label("b", "y", "2", path=labels_file)
    all_labels = list_all_labels(path=labels_file)
    assert "a" in all_labels
    assert "b" in all_labels


def test_list_all_labels_empty_when_no_file(labels_file):
    assert list_all_labels(path=labels_file) == {}
