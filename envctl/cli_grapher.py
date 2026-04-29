"""CLI commands for the dependency grapher."""
from __future__ import annotations

import click

from envctl.grapher import build_graph, find_dependents, topological_sort, format_graph_report
from envctl.store import EnvStore


@click.group("graph")
def graph_group() -> None:
    """Visualise and analyse env-set dependency graphs."""


@graph_group.command("show")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def show(store_path: str | None) -> None:
    """Print the full dependency graph for all env sets."""
    store = EnvStore(store_path)
    graph = build_graph(store)
    click.echo(format_graph_report(graph))


@graph_group.command("deps")
@click.argument("set_name")
@click.option("--store", "store_path", default=None)
def deps(set_name: str, store_path: str | None) -> None:
    """List sets that SET_NAME depends on."""
    store = EnvStore(store_path)
    graph = build_graph(store)
    if set_name not in graph:
        click.echo(f"Set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    dependencies = sorted(graph[set_name])
    if not dependencies:
        click.echo(f"'{set_name}' has no dependencies.")
    else:
        click.echo(f"'{set_name}' depends on:")
        for d in dependencies:
            click.echo(f"  - {d}")


@graph_group.command("dependents")
@click.argument("set_name")
@click.option("--store", "store_path", default=None)
def dependents_cmd(set_name: str, store_path: str | None) -> None:
    """List sets that depend on SET_NAME."""
    store = EnvStore(store_path)
    graph = build_graph(store)
    result = sorted(find_dependents(graph, set_name))
    if not result:
        click.echo(f"No sets depend on '{set_name}'.")
    else:
        click.echo(f"Sets depending on '{set_name}':")
        for name in result:
            click.echo(f"  - {name}")


@graph_group.command("order")
@click.option("--store", "store_path", default=None)
def order(store_path: str | None) -> None:
    """Print sets in safe dependency (topological) order."""
    store = EnvStore(store_path)
    graph = build_graph(store)
    try:
        ordered = topological_sort(graph)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    click.echo("Evaluation order (dependencies first):")
    for i, name in enumerate(ordered, 1):
        click.echo(f"  {i}. {name}")
