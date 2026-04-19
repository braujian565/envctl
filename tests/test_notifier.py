"""Tests for envctl.notifier."""
import pytest
from unittest.mock import patch
from envctl.notifier import add_hook, remove_hook, list_hooks, fire_hooks, HOOK_EVENTS


@pytest.fixture(autouse=True)
def mock_hooks_file(tmp_path, monkeypatch):
    hooks_file = tmp_path / "hooks.json"
    import envctl.notifier as notifier_mod
    monkeypatch.setattr(notifier_mod, "_HOOKS_FILE", hooks_file)


def test_hook_events_list():
    assert "switch" in HOOK_EVENTS
    assert "save" in HOOK_EVENTS


def test_add_hook_returns_entry():
    entry = add_hook("switch", "echo switched")
    assert entry["event"] == "switch"
    assert entry["command"] == "echo switched"


def test_add_hook_persisted():
    add_hook("save", "echo saved")
    hooks = list_hooks("save")
    assert "echo saved" in hooks["save"]


def test_add_hook_no_duplicate():
    add_hook("delete", "echo del")
    add_hook("delete", "echo del")
    hooks = list_hooks("delete")
    assert hooks["delete"].count("echo del") == 1


def test_add_hook_invalid_event():
    with pytest.raises(ValueError):
        add_hook("nonexistent_event", "echo x")


def test_remove_hook_existing():
    add_hook("switch", "echo hi")
    result = remove_hook("switch", "echo hi")
    assert result is True
    hooks = list_hooks("switch")
    assert "echo hi" not in hooks["switch"]


def test_remove_hook_missing():
    result = remove_hook("switch", "not there")
    assert result is False


def test_list_hooks_all_events():
    add_hook("switch", "cmd1")
    hooks = list_hooks()
    assert set(hooks.keys()) == set(HOOK_EVENTS)


def test_list_hooks_filter_event():
    add_hook("import", "cmd_import")
    hooks = list_hooks("import")
    assert list(hooks.keys()) == ["import"]


def test_fire_hooks_returns_commands():
    add_hook("snapshot", "backup.sh")
    cmds = fire_hooks("snapshot")
    assert any("backup.sh" in c for c in cmds)


def test_fire_hooks_with_context():
    add_hook("switch", "notify.sh")
    cmds = fire_hooks("switch", {"SET": "production"})
    assert any("SET=production" in c for c in cmds)


def test_fire_hooks_empty_when_none_registered():
    cmds = fire_hooks("delete")
    assert cmds == []
