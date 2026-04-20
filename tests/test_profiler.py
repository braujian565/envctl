import pytest
from pathlib import Path
from envctl import profiler


@pytest.fixture
def tmp_profile(tmp_path):
    p = tmp_path / "profiles.json"
    return p


def test_list_profiles_empty(tmp_profile):
    assert profiler.list_profiles(tmp_profile) == []


def test_create_profile(tmp_profile):
    result = profiler.create_profile("dev", ["base", "local"], tmp_profile)
    assert result["sets"] == ["base", "local"]


def test_create_profile_persisted(tmp_profile):
    profiler.create_profile("prod", ["prod-vars"], tmp_profile)
    assert "prod" in profiler.list_profiles(tmp_profile)


def test_create_duplicate_profile_raises(tmp_profile):
    profiler.create_profile("dev", ["base"], tmp_profile)
    with pytest.raises(KeyError):
        profiler.create_profile("dev", ["other"], tmp_profile)


def test_get_profile_existing(tmp_profile):
    profiler.create_profile("staging", ["staging-db"], tmp_profile)
    p = profiler.get_profile("staging", tmp_profile)
    assert p is not None
    assert p["sets"] == ["staging-db"]


def test_get_profile_nonexistent(tmp_profile):
    assert profiler.get_profile("ghost", tmp_profile) is None


def test_list_profiles_sorted(tmp_profile):
    profiler.create_profile("z-profile", [], tmp_profile)
    profiler.create_profile("a-profile", [], tmp_profile)
    assert profiler.list_profiles(tmp_profile) == ["a-profile", "z-profile"]


def test_delete_profile_existing(tmp_profile):
    profiler.create_profile("temp", ["x"], tmp_profile)
    assert profiler.delete_profile("temp", tmp_profile) is True
    assert profiler.get_profile("temp", tmp_profile) is None


def test_delete_profile_nonexistent(tmp_profile):
    assert profiler.delete_profile("nope", tmp_profile) is False


def test_add_set_to_profile(tmp_profile):
    profiler.create_profile("dev", ["base"], tmp_profile)
    profiler.add_set_to_profile("dev", "extra", tmp_profile)
    p = profiler.get_profile("dev", tmp_profile)
    assert "extra" in p["sets"]


def test_add_set_no_duplicate(tmp_profile):
    profiler.create_profile("dev", ["base"], tmp_profile)
    profiler.add_set_to_profile("dev", "base", tmp_profile)
    p = profiler.get_profile("dev", tmp_profile)
    assert p["sets"].count("base") == 1


def test_add_set_to_missing_profile_raises(tmp_profile):
    with pytest.raises(KeyError):
        profiler.add_set_to_profile("missing", "x", tmp_profile)


def test_remove_set_from_profile(tmp_profile):
    profiler.create_profile("dev", ["base", "local"], tmp_profile)
    profiler.remove_set_from_profile("dev", "local", tmp_profile)
    p = profiler.get_profile("dev", tmp_profile)
    assert "local" not in p["sets"]


def test_remove_set_from_missing_profile_raises(tmp_profile):
    with pytest.raises(KeyError):
        profiler.remove_set_from_profile("missing", "x", tmp_profile)
