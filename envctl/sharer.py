"""envctl.sharer — share env sets between users/teams via signed export tokens."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

_DEFAULT_TTL = 3600  # seconds


def _sign(payload: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def create_share_token(
    env: dict[str, str],
    set_name: str,
    secret: str,
    ttl: int = _DEFAULT_TTL,
    meta: dict[str, Any] | None = None,
) -> str:
    """Encode env set into a signed, base64 share token."""
    payload = {
        "set": set_name,
        "env": env,
        "iat": int(time.time()),
        "exp": int(time.time()) + ttl,
        "meta": meta or {},
    }
    raw = json.dumps(payload, separators=(",", ":")).encode()
    sig = _sign(raw, secret)
    bundle = json.dumps({"data": raw.decode(), "sig": sig}).encode()
    return base64.urlsafe_b64encode(bundle).decode()


def decode_share_token(
    token: str,
    secret: str,
    *,
    verify_expiry: bool = True,
) -> dict[str, Any]:
    """Decode and verify a share token.  Raises ValueError on any failure."""
    try:
        bundle = json.loads(base64.urlsafe_b64decode(token.encode()))
        raw: str = bundle["data"]
        sig: str = bundle["sig"]
    except Exception as exc:
        raise ValueError(f"Malformed share token: {exc}") from exc

    expected = _sign(raw.encode(), secret)
    if not hmac.compare_digest(expected, sig):
        raise ValueError("Share token signature is invalid.")

    payload: dict[str, Any] = json.loads(raw)
    if verify_expiry and int(time.time()) > payload.get("exp", 0):
        raise ValueError("Share token has expired.")

    return payload


def share_summary(payload: dict[str, Any]) -> str:
    """Return a human-readable summary of a decoded share token."""
    set_name = payload.get("set", "<unknown>")
    key_count = len(payload.get("env", {}))
    exp = payload.get("exp", 0)
    remaining = max(0, exp - int(time.time()))
    mins, secs = divmod(remaining, 60)
    return (
        f"Set: {set_name}  Keys: {key_count}  "
        f"Expires in: {mins}m {secs}s"
    )
