"""Graphviz (DOT) visualization."""

from __future__ import annotations

from typing import Dict, List, Set


def to_graphviz(
    edges: Dict[str, List[str]],
    nodes: Set[str],
    root: str | None = None,
    title: str = "Dependency Graph",
) -> str:
    """
    Generate a Graphviz DOT representation of the dependency graph.

    Returns the full DOT source as a string.
    """
    lines: List[str] = [
        "digraph dependencies {",
        "    rankdir=LR;",
        "    node [shape=box, style=rounded, fontname=\"Helvetica\"];",
        "    edge [fontname=\"Helvetica\"];",
        f'    labelloc="t";',
        f'    label="{title}";',
        "",
    ]

    # Declare all nodes (ensures isolated nodes appear)
    for node in sorted(nodes):
        attrs = ""
        if root and node == root:
            attrs = ' [style="rounded,filled", fillcolor="#e6f3ff"]'
        lines.append(f'    "{node}"{attrs};')

    lines.append("")

    # Edges
    for src, deps in sorted(edges.items()):
        for dst in sorted(deps):
            lines.append(f'    "{src}" -> "{dst}";')

    lines.append("}")
    return "\n".join(lines)


def print_graphviz(
    edges: Dict[str, List[str]],
    nodes: Set[str],
    root: str | None = None,
) -> None:
    """Print Graphviz DOT description to stdout."""
    print(to_graphviz(edges, nodes, root=root))
