"""Tests for envctl.migrator."""

import pytest

from envctl.migrator import (
    apply_migration,
    apply_migrations,
    list_migrations,
    migrate_store_set,
    register_migration,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

class _FakeStore:
    def __init__(self, data):
        self._data = dict(data)
        self.saved = {}

    def load(self, name):
        return dict(self._data[name]) if name in self._data else None

    def save(self, name, env):
        self.saved[name] = dict(env)


@pytest.fixture(autouse=True)
def _clean_registry():
    """Remove test-only migrations after each test."""
    from envctl import migrator
    before = set(migrator._REGISTRY.keys())
    yield
    for key in list(migrator._REGISTRY.keys()):
        if key not in before:
            del migrator._REGISTRY[key]


# ---------------------------------------------------------------------------
# list_migrations
# ---------------------------------------------------------------------------

def test_list_migrations_includes_builtins():
    names = list_migrations()
    assert "uppercase_keys" in names
    assert "strip_value_whitespace" in names


def test_register_and_list():
    register_migration("noop", lambda e: e)
    assert "noop" in list_migrations()


# ---------------------------------------------------------------------------
# apply_migration
# ---------------------------------------------------------------------------

def test_apply_migration_uppercase_keys():
    result = apply_migration("uppercase_keys", {"foo": "bar", "baz": "qux"})
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_apply_migration_strip_whitespace():
    result = apply_migration("strip_value_whitespace", {"KEY": "  hello  "})
    assert result == {"KEY": "hello"}


def test_apply_migration_unknown_raises():
    with pytest.raises(KeyError, match="unknown_migration"):
        apply_migration("unknown_migration", {})


def test_apply_migration_does_not_mutate_original():
    original = {"key": "  value  "}
    apply_migration("strip_value_whitespace", original)
    assert original == {"key": "  value  "}


# ---------------------------------------------------------------------------
# apply_migrations
# ---------------------------------------------------------------------------

def test_apply_migrations_chain():
    env = {"db_host": "  localhost  "}
    result, applied = apply_migrations(
        ["strip_value_whitespace", "uppercase_keys"], env
    )
    assert result == {"DB_HOST": "localhost"}
    assert applied == ["strip_value_whitespace", "uppercase_keys"]


def test_apply_migrations_unknown_raises_before_applying():
    register_migration("tracker", lambda e: {**e, "_ran": "yes"})
    with pytest.raises(KeyError):
        apply_migrations(["tracker", "does_not_exist"], {"X": "1"})


def test_apply_migrations_empty_list_returns_copy():
    env = {"A": "1"}
    result, applied = apply_migrations([], env)
    assert result == env
    assert applied == []


# ---------------------------------------------------------------------------
# migrate_store_set
# ---------------------------------------------------------------------------

def test_migrate_store_set_saves_result():
    store = _FakeStore({"prod": {"db_url": "  postgres://localhost  "}})
    result, applied = migrate_store_set(store, "prod", ["strip_value_whitespace"])
    assert result == {"db_url": "postgres://localhost"}
    assert store.saved["prod"] == result


def test_migrate_store_set_dry_run_does_not_save():
    store = _FakeStore({"prod": {"key": "value"}})
    migrate_store_set(store, "prod", ["uppercase_keys"], dry_run=True)
    assert "prod" not in store.saved


def test_migrate_store_set_missing_set_raises():
    store = _FakeStore({})
    with pytest.raises(ValueError, match="not found"):
        migrate_store_set(store, "ghost", ["uppercase_keys"])
