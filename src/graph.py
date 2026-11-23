"""Graph construction using iterative DFS (without recursion)."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from .fetcher import DependencyFetcher


class DependencyGraph:
    """Builds and stores a dependency graph using iterative DFS."""

    def __init__(
        self,
        fetcher: DependencyFetcher,
        max_depth: int = 10,
        filter_substr: Optional[str] = None,
    ):
        self.fetcher = fetcher
        self.max_depth = max_depth
        self.filter_substr = filter_substr.lower() if filter_substr else None
        # adjacency list: package -> list of direct dependencies
        self.edges: Dict[str, List[str]] = defaultdict(list)
        self.nodes: Set[str] = set()
        self.cycles: List[Tuple[str, str]] = []  # detected back-edges

    def _should_skip(self, package: str) -> bool:
        """Return True if package must be ignored due to filter."""
        if self.filter_substr is None:
            return False
        return self.filter_substr in package.lower()

    def build(self, root: str) -> None:
        """
        Build the transitive dependency graph starting from `root`
        using iterative Depth-First Search (explicit stack).

        Correctly handles:
        - maximum depth
        - package name filter
        - cyclic dependencies (via path tracking / gray nodes)
        """
        root = root.strip()
        if not root or self._should_skip(root):
            return

        # Colors: 0 = white (unvisited), 1 = gray (in current path), 2 = black (done)
        color: Dict[str, int] = {}
        # Stack of frames: (package, depth, iterator_over_deps or None)
        stack: List[Tuple[str, int, Optional[List[str]]]] = []

        stack.append((root, 0, None))
        self.nodes.add(root)

        while stack:
            package, depth, deps_iter = stack[-1]

            if deps_iter is None:
                # First time we see this frame -> enter node
                if color.get(package, 0) == 2:
                    stack.pop()
                    continue
                if color.get(package, 0) == 1:
                    stack.pop()
                    continue

                if depth > self.max_depth:
                    color[package] = 2
                    stack.pop()
                    continue

                if self._should_skip(package):
                    color[package] = 2
                    stack.pop()
                    continue

                # Mark gray
                color[package] = 1
                self.nodes.add(package)

                # Fetch dependencies
                try:
                    deps = self.fetcher.get_direct_dependencies(package)
                except Exception as exc:  # noqa: BLE001
                    print(
                        f"[warning] не удалось получить зависимости для {package}: {exc}"
                    )
                    deps = []

                # Store edges and prepare iterator
                clean_deps: List[str] = []
                for dep in deps:
                    dep = dep.strip()
                    if not dep or self._should_skip(dep):
                        continue
                    self.nodes.add(dep)
                    if dep not in self.edges[package]:
                        self.edges[package].append(dep)
                    clean_deps.append(dep)

                # Replace top frame with one that has the deps list
                stack[-1] = (package, depth, clean_deps)
                continue

            # We have deps list. Process next dependency or finish.
            if deps_iter:
                dep = deps_iter.pop(0)
                c = color.get(dep, 0)
                if c == 1:
                    # Gray -> back edge (cycle)
                    self.cycles.append((package, dep))
                elif c == 0:
                    # White -> explore
                    stack.append((dep, depth + 1, None))
                # if black (2) - already done, skip
            else:
                # No more deps -> mark black and pop
                color[package] = 2
                stack.pop()

    def get_adjacency(self) -> Dict[str, List[str]]:
        """Return the adjacency list of the built graph."""
        return dict(self.edges)

    def has_cycles(self) -> bool:
        return bool(self.cycles)

    def get_cycles(self) -> List[Tuple[str, str]]:
        return list(self.cycles)
