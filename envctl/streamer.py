"""Stream env set keys/values as newline-delimited JSON or CSV records."""
from __future__ import annotations

import csv
import io
import json
from typing import Dict, Iterator, Literal

StreamFormat = Literal["jsonl", "csv"]

SUPPORTED_FORMATS: list[str] = ["jsonl", "csv"]


def _iter_pairs(env: Dict[str, str]) -> Iterator[tuple[str, str]]:
    for key, value in sorted(env.items()):
        yield key, value


def stream_jsonl(env: Dict[str, str], set_name: str = "") -> Iterator[str]:
    """Yield one JSON line per key/value pair."""
    for key, value in _iter_pairs(env):
        record: dict = {"key": key, "value": value}
        if set_name:
            record["set"] = set_name
        yield json.dumps(record)


def stream_csv(env: Dict[str, str], set_name: str = "") -> Iterator[str]:
    """Yield CSV rows (header first, then one row per key/value pair)."""
    buf = io.StringIO()
    fieldnames = ["set", "key", "value"] if set_name else ["key", "value"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    yield buf.getvalue().rstrip("\n")
    for key, value in _iter_pairs(env):
        buf = io.StringIO()
        row: dict = {"key": key, "value": value}
        if set_name:
            row["set"] = set_name
        writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
        writer.writerow(row)
        yield buf.getvalue().rstrip("\n")


def stream_env_set(
    env: Dict[str, str],
    fmt: StreamFormat = "jsonl",
    set_name: str = "",
) -> Iterator[str]:
    """Dispatch to the correct streamer based on *fmt*."""
    if fmt == "jsonl":
        yield from stream_jsonl(env, set_name=set_name)
    elif fmt == "csv":
        yield from stream_csv(env, set_name=set_name)
    else:
        raise ValueError(f"Unsupported stream format: {fmt!r}. Choose from {SUPPORTED_FORMATS}")
