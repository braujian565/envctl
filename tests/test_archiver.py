"""Tests for envctl.archiver."""
import json
import os
import pytest
from unittest.mock import MagicMock

from envctl.archiver import export_archive, import_archive, list_archive


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.list_sets.return_value = ["dev", "prod"]
    store.load_set.side_effect = lambda name: {"KEY": name.upper()} if name in ("dev", "prod") else None
    return store


def test_export_archive_all_sets(mock_store, tmp_path):
    out = tmp_path / "archive.json"
    bundle = export_archive(mock_store, str(out))
    assert set(bundle["sets"].keys()) == {"dev", "prod"}
    assert out.exists()


def test_export_archive_file_content(mock_store, tmp_path):
    out = tmp_path / "archive.json"
    export_archive(mock_store, str(out))
    data = json.loads(out.read_text())
    assert data["version"] == 1
    assert "created_at" in data
    assert data["sets"]["dev"] == {"KEY": "DEV"}


def test_export_archive_subset(mock_store, tmp_path):
    out = tmp_path / "archive.json"
    bundle = export_archive(mock_store, str(out), sets=["dev"])
    assert list(bundle["sets"].keys()) == ["dev"]


def test_export_archive_missing_set_raises(mock_store, tmp_path):
    out = tmp_path / "archive.json"
    with pytest.raises(KeyError, match="ghost"):
        export_archive(mock_store, str(out), sets=["ghost"])


def test_import_archive_basic(mock_store, tmp_path):
    arc = tmp_path / "archive.json"
    arc.write_text(json.dumps({"version": 1, "created_at": "x", "sets": {"staging": {"A": "1"}}}))
    mock_store.load_set.side_effect = lambda name: None
    imported = import_archive(mock_store, str(arc))
    assert imported == ["staging"]
    mock_store.save_set.assert_called_once_with("staging", {"A": "1"})


def test_import_archive_overwrite_false_raises(mock_store, tmp_path):
    arc = tmp_path / "archive.json"
    arc.write_text(json.dumps({"version": 1, "created_at": "x", "sets": {"dev": {"A": "1"}}}))
    mock_store.load_set.side_effect = lambda name: {"existing": "val"}
    with pytest.raises(ValueError, match="already exists"):
        import_archive(mock_store, str(arc), overwrite=False)


def test_import_archive_with_prefix(mock_store, tmp_path):
    arc = tmp_path / "archive.json"
    arc.write_text(json.dumps({"version": 1, "created_at": "x", "sets": {"dev": {"X": "1"}}}))
    mock_store.load_set.side_effect = lambda name: None
    imported = import_archive(mock_store, str(arc), prefix="bak_")
    assert imported == ["bak_dev"]
    mock_store.save_set.assert_called_once_with("bak_dev", {"X": "1"})


def test_import_archive_file_not_found(mock_store):
    with pytest.raises(FileNotFoundError):
        import_archive(mock_store, "/no/such/file.json")


def test_list_archive(tmp_path):
    arc = tmp_path / "archive.json"
    arc.write_text(json.dumps({"version": 1, "created_at": "2024-01-01", "sets": {"a": {}, "b": {}}}))
    info = list_archive(str(arc))
    assert info["version"] == 1
    assert set(info["sets"]) == {"a", "b"}


def test_list_archive_missing_file():
    with pytest.raises(FileNotFoundError):
        list_archive("/no/such/archive.json")
