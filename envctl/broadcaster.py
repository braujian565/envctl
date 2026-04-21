"""Broadcast env set changes to registered channels (stdout, file, webhook)."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any

_CHANNELS_FILE = Path.home() / ".envctl" / "broadcast_channels.json"

CHANNEL_TYPES = ["stdout", "file", "webhook"]


def _load() -> list[dict]:
    if not _CHANNELS_FILE.exists():
        return []
    return json.loads(_CHANNELS_FILE.read_text())


def _save(channels: list[dict]) -> None:
    _CHANNELS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CHANNELS_FILE.write_text(json.dumps(channels, indent=2))


def add_channel(channel_type: str, target: str) -> dict:
    """Register a broadcast channel. target is a file path or URL."""
    if channel_type not in CHANNEL_TYPES:
        raise ValueError(f"Unknown channel type '{channel_type}'. Choose from {CHANNEL_TYPES}")
    channels = _load()
    for ch in channels:
        if ch["type"] == channel_type and ch["target"] == target:
            return ch
    entry = {"type": channel_type, "target": target, "enabled": True}
    channels.append(entry)
    _save(channels)
    return entry


def remove_channel(channel_type: str, target: str) -> bool:
    channels = _load()
    new = [c for c in channels if not (c["type"] == channel_type and c["target"] == target)]
    if len(new) == len(channels):
        return False
    _save(new)
    return True


def list_channels() -> list[dict]:
    return _load()


def _build_payload(event: str, set_name: str, detail: dict[str, Any] | None) -> dict:
    return {"event": event, "set": set_name, "detail": detail or {}}


def broadcast(event: str, set_name: str, detail: dict[str, Any] | None = None) -> list[str]:
    """Broadcast an event to all enabled channels. Returns list of delivery reports."""
    payload = _build_payload(event, set_name, detail)
    message = json.dumps(payload)
    reports: list[str] = []
    for ch in _load():
        if not ch.get("enabled", True):
            continue
        ctype, target = ch["type"], ch["target"]
        try:
            if ctype == "stdout":
                print(f"[broadcast] {message}")
                reports.append(f"stdout:ok")
            elif ctype == "file":
                with open(target, "a") as fh:
                    fh.write(message + "\n")
                reports.append(f"file:{target}:ok")
            elif ctype == "webhook":
                req = urllib.request.Request(
                    target,
                    data=message.encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    reports.append(f"webhook:{target}:{resp.status}")
        except Exception as exc:  # noqa: BLE001
            reports.append(f"{ctype}:{target}:error:{exc}")
    return reports
