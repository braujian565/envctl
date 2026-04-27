"""Tests for envctl.stenciler."""
import pytest
from envctl.stenciler import (
    apply_stencil,
    check_conformance,
    is_conformant,
    format_conformance_report,
    STENCIL_MISSING,
    STENCIL_EXTRA,
)


STENCIL = ["HOST", "PORT", "DB_NAME"]


# ---------------------------------------------------------------------------
# apply_stencil
# ---------------------------------------------------------------------------

def test_apply_stencil_fills_missing_with_default():
    env = {"HOST": "localhost"}
    result = apply_stencil(env, STENCIL)
    assert result["PORT"] == ""
    assert result["DB_NAME"] == ""


def test_apply_stencil_custom_default():
    env = {}
    result = apply_stencil(env, STENCIL, default="UNSET")
    assert all(v == "UNSET" for v in result.values())


def test_apply_stencil_drops_extra_by_default():
    env = {"HOST": "h", "PORT": "5432", "DB_NAME": "mydb", "SECRET": "x"}
    result = apply_stencil(env, STENCIL)
    assert "SECRET" not in result


def test_apply_stencil_keeps_extra_when_flag_false():
    env = {"HOST": "h", "PORT": "5432", "DB_NAME": "mydb", "SECRET": "x"}
    result = apply_stencil(env, STENCIL, drop_extra=False)
    assert "SECRET" in result


def test_apply_stencil_preserves_existing_values():
    env = {"HOST": "prod.example.com", "PORT": "5432", "DB_NAME": "prod"}
    result = apply_stencil(env, STENCIL)
    assert result["HOST"] == "prod.example.com"


def test_apply_stencil_key_order_follows_stencil():
    env = {"DB_NAME": "d", "PORT": "p", "HOST": "h"}
    result = apply_stencil(env, STENCIL)
    assert list(result.keys()) == STENCIL


def test_apply_stencil_empty_env():
    result = apply_stencil({}, STENCIL)
    assert list(result.keys()) == STENCIL
    assert all(v == "" for v in result.values())


# ---------------------------------------------------------------------------
# check_conformance
# ---------------------------------------------------------------------------

def test_check_conformance_fully_conformant():
    env = {"HOST": "h", "PORT": "p", "DB_NAME": "d"}
    report = check_conformance(env, STENCIL)
    assert report[STENCIL_MISSING] == []
    assert report[STENCIL_EXTRA] == []


def test_check_conformance_detects_missing():
    env = {"HOST": "h"}
    report = check_conformance(env, STENCIL)
    assert "PORT" in report[STENCIL_MISSING]
    assert "DB_NAME" in report[STENCIL_MISSING]


def test_check_conformance_detects_extra():
    env = {"HOST": "h", "PORT": "p", "DB_NAME": "d", "EXTRA_KEY": "e"}
    report = check_conformance(env, STENCIL)
    assert "EXTRA_KEY" in report[STENCIL_EXTRA]


def test_check_conformance_missing_sorted():
    env = {}
    report = check_conformance(env, ["Z", "A", "M"])
    assert report[STENCIL_MISSING] == ["A", "M", "Z"]


# ---------------------------------------------------------------------------
# is_conformant
# ---------------------------------------------------------------------------

def test_is_conformant_true_when_exact_match():
    env = {"HOST": "h", "PORT": "p", "DB_NAME": "d"}
    assert is_conformant(env, STENCIL) is True


def test_is_conformant_false_when_missing():
    assert is_conformant({"HOST": "h"}, STENCIL) is False


def test_is_conformant_false_when_extra():
    env = {"HOST": "h", "PORT": "p", "DB_NAME": "d", "EXTRA": "x"}
    assert is_conformant(env, STENCIL) is False


# ---------------------------------------------------------------------------
# format_conformance_report
# ---------------------------------------------------------------------------

def test_format_conformance_report_conformant():
    report = {STENCIL_MISSING: [], STENCIL_EXTRA: []}
    text = format_conformance_report("prod", report)
    assert "fully conformant" in text
    assert "prod" in text


def test_format_conformance_report_shows_missing():
    report = {STENCIL_MISSING: ["PORT"], STENCIL_EXTRA: []}
    text = format_conformance_report("dev", report)
    assert "MISSING" in text
    assert "PORT" in text


def test_format_conformance_report_shows_extra():
    report = {STENCIL_MISSING: [], STENCIL_EXTRA: ["DEBUG"]}
    text = format_conformance_report("dev", report)
    assert "EXTRA" in text
    assert "DEBUG" in text
