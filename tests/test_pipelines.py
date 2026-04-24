"""Tests for envctl.pipelines."""
from __future__ import annotations

import pytest

import envctl.pipelines as pipelines
from envctl.pipelines import (
    apply_pipeline_to_set,
    build_pipeline,
    list_steps,
    register_step,
    run_pipeline,
)


@pytest.fixture(autouse=True)
def _clean_registry():
    """Isolate the step registry between tests."""
    original = dict(pipelines._STEPS)
    pipelines._STEPS.clear()
    yield
    pipelines._STEPS.clear()
    pipelines._STEPS.update(original)


def _upper_keys(env):
    return {k.upper(): v for k, v in env.items()}


def _prefix_values(env):
    return {k: "prefix_" + v for k, v in env.items()}


def test_list_steps_empty_initially():
    assert list_steps() == []


def test_register_and_list_step():
    register_step("upper", _upper_keys)
    assert "upper" in list_steps()


def test_register_duplicate_raises():
    register_step("upper", _upper_keys)
    with pytest.raises(ValueError, match="already registered"):
        register_step("upper", _upper_keys)


def test_build_pipeline_unknown_step_raises():
    with pytest.raises(KeyError, match="Unknown pipeline step"):
        build_pipeline(["nonexistent"])


def test_run_pipeline_single_step():
    register_step("upper", _upper_keys)
    result = run_pipeline({"foo": "bar"}, ["upper"])
    assert result == {"FOO": "bar"}


def test_run_pipeline_multiple_steps_ordered():
    register_step("upper", _upper_keys)
    register_step("prefix", _prefix_values)
    result = run_pipeline({"key": "val"}, ["upper", "prefix"])
    assert result == {"KEY": "prefix_val"}


def test_run_pipeline_empty_steps_returns_copy():
    env = {"A": "1"}
    result = run_pipeline(env, [])
    assert result == env
    assert result is not env


def test_apply_pipeline_to_set_overwrites(tmp_path):
    from envctl.store import EnvStore

    store = EnvStore(str(tmp_path / "store.json"))
    store.save("dev", {"name": "alice"})
    register_step("upper", _upper_keys)
    result = apply_pipeline_to_set(store, "dev", ["upper"])
    assert result == {"NAME": "alice"}
    assert store.load("dev") == {"NAME": "alice"}


def test_apply_pipeline_to_set_saves_to_target(tmp_path):
    from envctl.store import EnvStore

    store = EnvStore(str(tmp_path / "store.json"))
    store.save("dev", {"x": "1"})
    register_step("prefix", _prefix_values)
    apply_pipeline_to_set(store, "dev", ["prefix"], target_name="dev-processed")
    assert store.load("dev-processed") == {"x": "prefix_1"}
    # original unchanged
    assert store.load("dev") == {"x": "1"}


def test_apply_pipeline_missing_set_raises(tmp_path):
    from envctl.store import EnvStore

    store = EnvStore(str(tmp_path / "store.json"))
    with pytest.raises(KeyError, match="not found"):
        apply_pipeline_to_set(store, "ghost", [])
