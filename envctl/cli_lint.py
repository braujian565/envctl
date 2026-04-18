"""CLI commands for linting environment sets."""

import click
from envctl.store import EnvStore
from envctl.linter import lint_env_set, format_findings


@click.group("lint")
def lint_group():
    """Lint environment variable sets for common issues."""


@lint_group.command("check")
@click.argument("name")
@click.option("--store", "store_path", default=None, help="Path to store file.")
@click.option("--strict", is_flag=True, help="Exit with error if warnings found.")
def check(name: str, store_path: str, strict: bool):
    """Lint the environment set NAME."""
    s = EnvStore(store_path)
    env = s.load(name)
    if env is None:
        click.echo(f"Error: set '{name}' not found.", err=True)
        raise SystemExit(1)

    findings = lint_env_set(env)
    click.echo(format_findings(findings))

    if strict and findings:
        raise SystemExit(1)


@lint_group.command("check-all")
@click.option("--store", "store_path", default=None, help="Path to store file.")
@click.option("--strict", is_flag=True, help="Exit with error if any warnings found.")
def check_all(store_path: str, strict: bool):
    """Lint all stored environment sets."""
    s = EnvStore(store_path)
    names = s.list()
    if not names:
        click.echo("No environment sets found.")
        return

    any_findings = False
    for name in names:
        env = s.load(name)
        findings = lint_env_set(env or {})
        if findings:
            any_findings = True
            click.echo(f"--- {name} ---")
            click.echo(format_findings(findings))
        else:
            click.echo(f"--- {name} --- OK")

    if strict and any_findings:
        raise SystemExit(1)
