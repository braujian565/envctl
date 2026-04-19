"""Tests for envctl.templater."""
import pytest
from envctl.templater import render_value, render_env_set, find_placeholders


def test_render_value_no_placeholders():
    assert render_value("hello", {}) == "hello"


def test_render_value_single_placeholder():
    assert render_value("{{HOST}}", {"HOST": "localhost"}) == "localhost"


def test_render_value_multiple_placeholders():
    result = render_value("{{SCHEME}}://{{HOST}}:{{PORT}}", {
        "SCHEME": "https", "HOST": "example.com", "PORT": "443"
    })
    assert result == "https://example.com:443"


def test_render_value_whitespace_in_placeholder():
    assert render_value("{{ KEY }}", {"KEY": "val"}) == "val"


def test_render_value_missing_key_raises():
    with pytest.raises(KeyError, match="MISSING"):
        render_value("{{MISSING}}", {})


def test_render_env_set_with_explicit_context():
    env = {"URL": "{{SCHEME}}://{{HOST}}"}
    ctx = {"SCHEME": "http", "HOST": "localhost"}
    result = render_env_set(env, ctx)
    assert result["URL"] == "http://localhost"


def test_render_env_set_self_context():
    env = {"HOST": "localhost", "URL": "http://{{HOST}}"}
    result = render_env_set(env, None)
    assert result["URL"] == "http://localhost"


def test_render_env_set_self_context_order_matters():
    # URL comes before HOST so HOST not yet resolved when using self-ctx
    env = {"URL": "http://{{HOST}}", "HOST": "localhost"}
    with pytest.raises(KeyError):
        render_env_set(env, None)


def test_render_env_set_empty():
    assert render_env_set({}, {}) == {}


def test_find_placeholders_detects_vars():
    env = {"A": "{{X}}", "B": "plain", "C": "{{Y}}-{{Z}}"}
    found = find_placeholders(env)
    assert "A" in found
    assert found["A"] == ["X"]
    assert "B" not in found
    assert set(found["C"]) == {"Y", "Z"}


def test_find_placeholders_empty_env():
    assert find_placeholders({}) == {}


def test_find_placeholders_no_placeholders():
    assert find_placeholders({"KEY": "value"}) == {}
