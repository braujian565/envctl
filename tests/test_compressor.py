"""Tests for envctl.compressor."""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from envctl.compressor import (
    compress_env_set,
    compression_ratio,
    decompress_env_set,
    export_compressed,
    import_compressed,
)


SAMPLE_ENV = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "s3cr3t", "DEBUG": "false"}


def test_compress_returns_string():
    blob = compress_env_set(SAMPLE_ENV)
    assert isinstance(blob, str)
    assert len(blob) > 0


def test_compress_decompress_roundtrip():
    blob = compress_env_set(SAMPLE_ENV)
    restored = decompress_env_set(blob)
    assert restored == SAMPLE_ENV


def test_compress_empty_env():
    blob = compress_env_set({})
    restored = decompress_env_set(blob)
    assert restored == {}


def test_decompress_invalid_blob_raises():
    with pytest.raises(Exception):
        decompress_env_set("not-valid-base64!!")


def test_compression_ratio_between_zero_and_one():
    # For a repetitive env the ratio should be well below 1.0
    big_env = {f"KEY_{i}": "x" * 80 for i in range(20)}
    ratio = compression_ratio(big_env)
    assert 0.0 < ratio < 1.0


def test_compression_ratio_empty_env():
    ratio = compression_ratio({})
    # empty json "{}" compresses to something; ratio is defined
    assert isinstance(ratio, float)


def _make_store(env=None):
    store = MagicMock()
    store.load.return_value = env
    return store


def test_export_compressed_returns_blob():
    store = _make_store(SAMPLE_ENV)
    blob = export_compressed(store, "prod")
    assert blob is not None
    assert decompress_env_set(blob) == SAMPLE_ENV


def test_export_compressed_missing_set_returns_none():
    store = _make_store(None)
    result = export_compressed(store, "missing")
    assert result is None


def test_import_compressed_saves_and_returns_env():
    store = _make_store()
    blob = compress_env_set(SAMPLE_ENV)
    result = import_compressed(store, "prod", blob)
    assert result == SAMPLE_ENV
    store.save.assert_called_once_with("prod", SAMPLE_ENV)
