import pytest
from pathlib import Path
from envctl.pinner import pin_set, unpin_set, get_pin, list_pins


@pytest.fixture
def pins_file(tmp_path):
    return tmp_path / "pins.json"


def test_list_pins_empty_when_no_file(pins_file):
    result = list_pins(path=pins_file)
    assert result == {}


def test_pin_set_returns_entry(pins_file):
    entry = pin_set("production", "snap-abc123", path=pins_file)
    assert entry["set"] == "production"
    assert entry["snapshot_id"] == "snap-abc123"


def test_pin_set_persisted(pins_file):
    pin_set("staging", "snap-xyz", path=pins_file)
    pins = list_pins(path=pins_file)
    assert pins["staging"] == "snap-xyz"


def test_get_pin_existing(pins_file):
    pin_set("dev", "snap-001", path=pins_file)
    assert get_pin("dev", path=pins_file) == "snap-001"


def test_get_pin_nonexistent(pins_file):
    assert get_pin("missing", path=pins_file) is None


def test_pin_overwrite(pins_file):
    pin_set("production", "snap-old", path=pins_file)
    pin_set("production", "snap-new", path=pins_file)
    assert get_pin("production", path=pins_file) == "snap-new"


def test_unpin_existing(pins_file):
    pin_set("staging", "snap-abc", path=pins_file)
    result = unpin_set("staging", path=pins_file)
    assert result is True
    assert get_pin("staging", path=pins_file) is None


def test_unpin_nonexistent(pins_file):
    result = unpin_set("ghost", path=pins_file)
    assert result is False


def test_list_pins_multiple(pins_file):
    pin_set("a", "snap-1", path=pins_file)
    pin_set("b", "snap-2", path=pins_file)
    pins = list_pins(path=pins_file)
    assert pins == {"a": "snap-1", "b": "snap-2"}
