"""Simple encryption/decryption for env set values using Fernet symmetric encryption."""

from __future__ import annotations

import base64
import os
from typing import Dict

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore


ENV_KEY_VAR = "ENVCTL_SECRET_KEY"


def _require_fernet() -> None:
    if Fernet is None:
        raise RuntimeError(
            "cryptography package is required for encryption. "
            "Install it with: pip install cryptography"
        )


def generate_key() -> str:
    """Generate a new Fernet key and return it as a string."""
    _require_fernet()
    return Fernet.generate_key().decode()


def _get_fernet(key: str | None = None) -> "Fernet":
    _require_fernet()
    if key is None:
        key = os.environ.get(ENV_KEY_VAR)
    if not key:
        raise ValueError(
            f"No encryption key provided. Set {ENV_KEY_VAR} or pass key explicitly."
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_value(value: str, key: str | None = None) -> str:
    """Encrypt a single string value, returning a base64 token string."""
    f = _get_fernet(key)
    return f.encrypt(value.encode()).decode()


def decrypt_value(token: str, key: str | None = None) -> str:
    """Decrypt a token string back to the original value."""
    f = _get_fernet(key)
    try:
        return f.decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Decryption failed: invalid token or wrong key.") from exc


def encrypt_env_set(env: Dict[str, str], key: str | None = None) -> Dict[str, str]:
    """Return a new dict with all values encrypted."""
    return {k: encrypt_value(v, key) for k, v in env.items()}


def decrypt_env_set(env: Dict[str, str], key: str | None = None) -> Dict[str, str]:
    """Return a new dict with all values decrypted."""
    return {k: decrypt_value(v, key) for k, v in env.items()}
