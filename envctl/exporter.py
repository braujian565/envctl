"""Export environment variable sets to various shell formats."""

from typing import Dict, Optional


SUPPORTED_FORMATS = ["bash", "dotenv", "fish"]


def export_bash(env_vars: Dict[str, str]) -> str:
    """Export env vars as bash export statements."""
    lines = ["#!/usr/bin/env bash"]
    for key, value in sorted(env_vars.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines) + "\n"


def export_dotenv(env_vars: Dict[str, str]) -> str:
    """Export env vars as .env file format."""
    lines = []
    for key, value in sorted(env_vars.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + "\n"


def export_fish(env_vars: Dict[str, str]) -> str:
    """Export env vars as fish shell set statements."""
    lines = []
    for key, value in sorted(env_vars.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'set -x {key} "{escaped}"')
    return "\n".join(lines) + "\n"


def export_env_set(
    env_vars: Dict[str, str], fmt: str = "bash"
) -> Optional[str]:
    """Export env vars in the given format. Returns None if format unsupported."""
    fmt = fmt.lower()
    if fmt == "bash":
        return export_bash(env_vars)
    elif fmt == "dotenv":
        return export_dotenv(env_vars)
    elif fmt == "fish":
        return export_fish(env_vars)
    return None
