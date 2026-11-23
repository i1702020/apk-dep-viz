"""Tests for iterative DFS graph construction."""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.fetcher import DependencyFetcher
from src.graph import DependencyGraph


class TestGraphBuild(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).resolve().parents[1] / "data"

    def test_simple_graph(self):
        fetcher = DependencyFetcher(
            repo=str(self.data_dir / "test_repo_simple.txt"),
            test_mode=True,
        )
        g = DependencyGraph(fetcher=fetcher, max_depth=10)
        g.build("A")

        adj = g.get_adjacency()
        self.assertIn("A", adj)
        self.assertIn("B", adj["A"])
        self.assertIn("C", adj["A"])
        self.assertIn("D", adj["B"])
        self.assertIn("D", adj["C"])
        self.assertIn("E", adj["C"])
        self.assertFalse(g.has_cycles())

    def test_max_depth(self):
        fetcher = DependencyFetcher(
            repo=str(self.data_dir / "test_repo_deep.txt"),
            test_mode=True,
        )
        g = DependencyGraph(fetcher=fetcher, max_depth=2)
        g.build("A")
        # With depth 2 we should reach at most C
        nodes = g.nodes
        self.assertIn("A", nodes)
        self.assertIn("B", nodes)
        self.assertIn("C", nodes)
        # D is depth 3 from A, should not be fully expanded in a strict sense,
        # but depending on implementation may appear as a leaf.
        # At least G/H should not be present.
        self.assertNotIn("G", nodes)
        self.assertNotIn("H", nodes)

    def test_filter(self):
        fetcher = DependencyFetcher(
            repo=str(self.data_dir / "test_repo_simple.txt"),
            test_mode=True,
        )
        g = DependencyGraph(fetcher=fetcher, max_depth=10, filter_substr="E")
        g.build("A")
        # E and F should be filtered out
        self.assertNotIn("E", g.nodes)
        self.assertNotIn("F", g.nodes)
        # A, B, C, D should remain
        self.assertIn("A", g.nodes)
        self.assertIn("D", g.nodes)

    def test_cycle_detection(self):
        fetcher = DependencyFetcher(
            repo=str(self.data_dir / "test_repo_cycle.txt"),
            test_mode=True,
        )
        g = DependencyGraph(fetcher=fetcher, max_depth=10)
        g.build("A")
        self.assertTrue(g.has_cycles())
        # Graph should still contain the nodes
        self.assertIn("A", g.nodes)
        self.assertIn("B", g.nodes)
        self.assertIn("C", g.nodes)


if __name__ == "__main__":
    unittest.main()