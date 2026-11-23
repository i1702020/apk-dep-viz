"""Tests for dependency fetcher (test mode)."""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.fetcher import DependencyFetcher


class TestTestRepoFetcher(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).resolve().parents[1] / "data"
        self.fetcher = DependencyFetcher(
            repo=str(self.data_dir / "test_repo_simple.txt"),
            test_mode=True,
        )

    def test_direct_deps_a(self):
        deps = self.fetcher.get_direct_dependencies("A")
        self.assertEqual(sorted(deps), ["B", "C"])

    def test_direct_deps_d(self):
        deps = self.fetcher.get_direct_dependencies("D")
        self.assertEqual(deps, [])

    def test_case_insensitive(self):
        deps = self.fetcher.get_direct_dependencies("a")
        self.assertEqual(sorted(deps), ["B", "C"])

    def test_unknown_package(self):
        deps = self.fetcher.get_direct_dependencies("Z")
        self.assertEqual(deps, [])

    def test_all_packages(self):
        pkgs = self.fetcher.get_all_packages()
        self.assertIn("A", pkgs)
        self.assertIn("F", pkgs)


if __name__ == "__main__":
    unittest.main()