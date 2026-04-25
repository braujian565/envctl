"""Tests for envctl.linker."""
from __future__ import annotations

import pytest

from envctl.linker import add_link, find_links_to, list_links, remove_link, resolve_link


@pytest.fixture()
def links_file(tmp_path):
    return tmp_path / "links.json"


def test_list_links_empty_when_no_file(links_file):
    assert list_links(path=links_file) == []


def test_add_link_returns_entry(links_file):
    entry = add_link("current", "prod-2024", path=links_file)
    assert entry == {"name": "current", "target": "prod-2024"}


def test_add_link_persisted(links_file):
    add_link("current", "prod-2024", path=links_file)
    assert resolve_link("current", path=links_file) == "prod-2024"


def test_add_link_overwrites_existing(links_file):
    add_link("current", "prod-2024", path=links_file)
    add_link("current", "prod-2025", path=links_file)
    assert resolve_link("current", path=links_file) == "prod-2025"


def test_add_link_empty_name_raises(links_file):
    with pytest.raises(ValueError):
        add_link("", "prod-2024", path=links_file)


def test_add_link_empty_target_raises(links_file):
    with pytest.raises(ValueError):
        add_link("current", "", path=links_file)


def test_resolve_link_returns_none_when_missing(links_file):
    assert resolve_link("ghost", path=links_file) is None


def test_remove_link_returns_true_when_found(links_file):
    add_link("current", "prod-2024", path=links_file)
    assert remove_link("current", path=links_file) is True


def test_remove_link_returns_false_when_missing(links_file):
    assert remove_link("ghost", path=links_file) is False


def test_remove_link_deletes_entry(links_file):
    add_link("current", "prod-2024", path=links_file)
    remove_link("current", path=links_file)
    assert resolve_link("current", path=links_file) is None


def test_list_links_sorted(links_file):
    add_link("z-link", "set-z", path=links_file)
    add_link("a-link", "set-a", path=links_file)
    names = [lnk["name"] for lnk in list_links(path=links_file)]
    assert names == ["a-link", "z-link"]


def test_find_links_to_returns_matching(links_file):
    add_link("current", "prod-2024", path=links_file)
    add_link("stable", "prod-2024", path=links_file)
    add_link("dev", "dev-latest", path=links_file)
    result = find_links_to("prod-2024", path=links_file)
    assert sorted(result) == ["current", "stable"]


def test_find_links_to_returns_empty_when_none(links_file):
    add_link("current", "prod-2024", path=links_file)
    assert find_links_to("staging", path=links_file) == []
