import pytest
from pathlib import Path
from envctl.annotator import set_note, get_note, remove_note, list_notes


@pytest.fixture
def ann_file(tmp_path):
    return tmp_path / "annotations.json"


def test_get_note_returns_none_when_no_file(ann_file):
    assert get_note("prod", path=ann_file) is None


def test_set_and_get_note(ann_file):
    set_note("prod", "Production environment", path=ann_file)
    assert get_note("prod", path=ann_file) == "Production environment"


def test_set_note_overwrites(ann_file):
    set_note("prod", "Old note", path=ann_file)
    set_note("prod", "New note", path=ann_file)
    assert get_note("prod", path=ann_file) == "New note"


def test_remove_note_existing(ann_file):
    set_note("staging", "Staging env", path=ann_file)
    result = remove_note("staging", path=ann_file)
    assert result is True
    assert get_note("staging", path=ann_file) is None


def test_remove_note_nonexistent(ann_file):
    result = remove_note("ghost", path=ann_file)
    assert result is False


def test_list_notes_empty(ann_file):
    assert list_notes(path=ann_file) == {}


def test_list_notes_multiple(ann_file):
    set_note("prod", "Production", path=ann_file)
    set_note("dev", "Development", path=ann_file)
    notes = list_notes(path=ann_file)
    assert notes == {"prod": "Production", "dev": "Development"}


def test_set_note_persisted(ann_file):
    set_note("ci", "CI environment", path=ann_file)
    assert ann_file.exists()
    note = get_note("ci", path=ann_file)
    assert note == "CI environment"
