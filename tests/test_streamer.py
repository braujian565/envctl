"""Tests for envctl.streamer."""
from __future__ import annotations

import json
import pytest

from envctl.streamer import (
    SUPPORTED_FORMATS,
    stream_csv,
    stream_env_set,
    stream_jsonl,
)

SAMPLE = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev"}


def test_supported_formats_list():
    assert "jsonl" in SUPPORTED_FORMATS
    assert "csv" in SUPPORTED_FORMATS


def test_stream_jsonl_yields_one_line_per_key():
    lines = list(stream_jsonl(SAMPLE))
    assert len(lines) == len(SAMPLE)


def test_stream_jsonl_valid_json():
    for line in stream_jsonl(SAMPLE):
        obj = json.loads(line)
        assert "key" in obj
        assert "value" in obj


def test_stream_jsonl_includes_set_name():
    lines = list(stream_jsonl(SAMPLE, set_name="prod"))
    for line in lines:
        obj = json.loads(line)
        assert obj["set"] == "prod"


def test_stream_jsonl_no_set_name_omits_field():
    lines = list(stream_jsonl(SAMPLE))
    for line in lines:
        obj = json.loads(line)
        assert "set" not in obj


def test_stream_jsonl_sorted_keys():
    lines = list(stream_jsonl(SAMPLE))
    keys = [json.loads(l)["key"] for l in lines]
    assert keys == sorted(keys)


def test_stream_csv_first_line_is_header():
    lines = list(stream_csv(SAMPLE))
    assert lines[0].startswith("key,value")


def test_stream_csv_includes_set_column_when_named():
    lines = list(stream_csv(SAMPLE, set_name="staging"))
    assert lines[0].startswith("set,key,value")


def test_stream_csv_row_count():
    lines = list(stream_csv(SAMPLE))
    # header + one row per key
    assert len(lines) == len(SAMPLE) + 1


def test_stream_env_set_dispatches_jsonl():
    lines = list(stream_env_set(SAMPLE, fmt="jsonl"))
    assert len(lines) == len(SAMPLE)
    json.loads(lines[0])  # must be valid JSON


def test_stream_env_set_dispatches_csv():
    lines = list(stream_env_set(SAMPLE, fmt="csv"))
    assert lines[0].startswith("key,value")


def test_stream_env_set_unknown_format_raises():
    with pytest.raises(ValueError, match="Unsupported stream format"):
        list(stream_env_set(SAMPLE, fmt="xml"))  # type: ignore[arg-type]


def test_stream_empty_env():
    lines = list(stream_jsonl({}))
    assert lines == []
