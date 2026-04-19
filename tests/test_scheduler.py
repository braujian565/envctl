import pytest
from unittest.mock import patch, mock_open, MagicMock
import json
from envctl import scheduler


@pytest.fixture(autouse=True)
def tmp_schedule(tmp_path, monkeypatch):
    schedule_file = tmp_path / "schedules.json"
    monkeypatch.setattr(scheduler, "_SCHEDULE_FILE", schedule_file)
    return schedule_file


def test_list_schedules_empty():
    assert scheduler.list_schedules() == {}


def test_add_schedule_returns_entry():
    entry = scheduler.add_schedule("nightly", "prod", "0 2 * * *")
    assert entry["env_set"] == "prod"
    assert entry["cron"] == "0 2 * * *"
    assert entry["shell"] == "bash"
    assert entry["enabled"] is True


def test_add_schedule_persisted():
    scheduler.add_schedule("nightly", "prod", "0 2 * * *")
    schedules = scheduler.list_schedules()
    assert "nightly" in schedules


def test_get_schedule_existing():
    scheduler.add_schedule("nightly", "prod", "0 2 * * *")
    entry = scheduler.get_schedule("nightly")
    assert entry is not None
    assert entry["env_set"] == "prod"


def test_get_schedule_nonexistent():
    assert scheduler.get_schedule("ghost") is None


def test_remove_schedule_existing():
    scheduler.add_schedule("nightly", "prod", "0 2 * * *")
    result = scheduler.remove_schedule("nightly")
    assert result is True
    assert scheduler.get_schedule("nightly") is None


def test_remove_schedule_nonexistent():
    assert scheduler.remove_schedule("ghost") is False


def test_set_enabled_false():
    scheduler.add_schedule("nightly", "prod", "0 2 * * *")
    result = scheduler.set_enabled("nightly", False)
    assert result is True
    assert scheduler.get_schedule("nightly")["enabled"] is False


def test_set_enabled_nonexistent():
    assert scheduler.set_enabled("ghost", True) is False


def test_add_multiple_schedules():
    scheduler.add_schedule("a", "dev", "0 8 * * 1-5")
    scheduler.add_schedule("b", "prod", "0 20 * * *")
    schedules = scheduler.list_schedules()
    assert len(schedules) == 2
    assert "a" in schedules and "b" in schedules
