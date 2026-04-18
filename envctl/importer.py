"""Import environment variable sets from existing files."""

import os
import re
import shlex
from pathlib import Path


SUPPORTED_FORMATS = ["dotenv", "bash"]


def parse_dotenv(text: str) -> dict:
    """Parse a .env file into a dict of key-value pairs."""
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip surrounding quotes
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        result[key] = value
    return result


def parse_bash(text: str) -> dict:
    """Parse a bash export file into a dict of key-value pairs."""
    result = {}
    export_re = re.compile(r'^export\s+([A-Za-z_][A-Za-z0-9_]*)=(.*)$')
    for line in text.splitlines():
        line = line.strip()
        match = export_re.match(line)
        if not match:
            continue
        key = match.group(1)
        value = match.group(2)
        try:
            value = shlex.split(value)[0] if value else ""
        except ValueError:
            value = value.strip('"\'')
        result[key] = value
    return result


def import_env_set(path: str, fmt: str) -> dict:
    """Read a file and parse it according to the given format."""
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")
    text = Path(path).read_text(encoding="utf-8")
    if fmt == "dotenv":
        return parse_dotenv(text)
    elif fmt == "bash":
        return parse_bash(text)
