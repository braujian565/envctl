"""grapher.py – build and analyse dependency graphs between env sets.

A dependency edge A -> B means set A references values from set B
(detected via cross-set interpolation markers like {{B:KEY}}).
"""
from __future__ import annotations

import re
from typing import Dict, List, Set, Tuple

_CROSS_REF_RE = re.compile(r"\{\{([^:}]+):([^}]+)\}\}")


def build_graph(store) -> Dict[str, Set[str]]:
    """Return adjacency map {set_name: {dependency_set, ...}} for all sets."""
    graph: Dict[str, Set[str]] = {}
    for name in store.list_sets():
        env = store.load(name) or {}
        deps: Set[str] = set()
        for value in env.values():
            for ref_set, _ in _CROSS_REF_RE.findall(str(value)):
                if ref_set != name:
                    deps.add(ref_set)
        graph[name] = deps
    return graph


def find_dependents(graph: Dict[str, Set[str]], target: str) -> List[str]:
    """Return all set names that depend (directly) on *target*."""
    return [name for name, deps in graph.items() if target in deps]


def topological_sort(graph: Dict[str, Set[str]]) -> List[str]:
    """Return sets in dependency order (dependencies first).

    Raises ValueError on cyclic dependency.
    """
    visited: Set[str] = set()
    stack: List[str] = []
    in_progress: Set[str] = set()

    def visit(node: str) -> None:
        if node in in_progress:
            raise ValueError(f"Cyclic dependency detected involving '{node}'")
        if node in visited:
            return
        in_progress.add(node)
        for dep in graph.get(node, set()):
            visit(dep)
        in_progress.discard(node)
        visited.add(node)
        stack.append(node)

    for node in list(graph):
        visit(node)
    return stack


def format_graph_report(graph: Dict[str, Set[str]]) -> str:
    """Human-readable dependency report."""
    if not graph:
        return "No env sets found."
    lines: List[str] = ["Dependency graph:", ""]
    for name in sorted(graph):
        deps = sorted(graph[name])
        dep_str = ", ".join(deps) if deps else "(none)"
        lines.append(f"  {name} -> {dep_str}")
    return "\n".join(lines)
