"""Tests for envctl.promoter."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from envctl.promoter import (
    _next_stage,
    _derive_target_name,
    promote_set,
    list_stages,
    DEFAULT_PIPELINE,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_store(sets: dict):
    store = MagicMock()
    store.load.side_effect = lambda name: dict(sets[name]) if name in sets else None
    store.save = MagicMock()
    return store


# ---------------------------------------------------------------------------
# _next_stage
# ---------------------------------------------------------------------------

def test_next_stage_dev_to_staging():
    assert _next_stage("dev") == "staging"


def test_next_stage_staging_to_prod():
    assert _next_stage("staging") == "prod"


def test_next_stage_prod_returns_none():
    assert _next_stage("prod") is None


def test_next_stage_unknown_returns_none():
    assert _next_stage("unknown") is None


def test_next_stage_custom_pipeline():
    assert _next_stage("alpha", ["alpha", "beta", "gamma"]) == "beta"


# ---------------------------------------------------------------------------
# _derive_target_name
# ---------------------------------------------------------------------------

def test_derive_target_name_replaces_stage_token():
    assert _derive_target_name("myapp-dev", "dev", "staging") == "myapp-staging"


def test_derive_target_name_appends_when_no_token():
    assert _derive_target_name("myapp", "dev", "staging") == "myapp-staging"


# ---------------------------------------------------------------------------
# promote_set
# ---------------------------------------------------------------------------

def test_promote_set_copies_vars():
    store = _make_store({"myapp-dev": {"HOST": "localhost", "PORT": "5432"}})
    result = promote_set(store, "myapp-dev", "dev")
    assert result["target"] == "myapp-staging"
    store.save.assert_called_once_with("myapp-staging", {"HOST": "localhost", "PORT": "5432"})


def test_promote_set_explicit_target_stage():
    store = _make_store({"myapp-dev": {"X": "1"}})
    result = promote_set(store, "myapp-dev", "dev", target_stage="prod")
    assert result["target"] == "myapp-prod"


def test_promote_set_raises_when_source_missing():
    store = _make_store({})
    with pytest.raises(KeyError, match="not found"):
        promote_set(store, "missing", "dev")


def test_promote_set_raises_at_last_stage():
    store = _make_store({"myapp-prod": {"X": "1"}})
    with pytest.raises(ValueError, match="last stage"):
        promote_set(store, "myapp-prod", "prod")


def test_promote_set_raises_if_target_exists_no_overwrite():
    store = _make_store({"myapp-dev": {"X": "1"}, "myapp-staging": {"X": "old"}})
    with pytest.raises(ValueError, match="already exists"):
        promote_set(store, "myapp-dev", "dev", overwrite=False)


def test_promote_set_overwrites_when_flag_set():
    store = _make_store({"myapp-dev": {"X": "new"}, "myapp-staging": {"X": "old"}})
    result = promote_set(store, "myapp-dev", "dev", overwrite=True)
    assert result["vars"] == {"X": "new"}


# ---------------------------------------------------------------------------
# list_stages
# ---------------------------------------------------------------------------

def test_list_stages_returns_default_pipeline():
    assert list_stages() == DEFAULT_PIPELINE


def test_list_stages_returns_custom_pipeline():
    custom = ["alpha", "beta"]
    assert list_stages(custom) == custom
