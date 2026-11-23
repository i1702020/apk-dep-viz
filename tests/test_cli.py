"""Tests for CLI argument parsing and configuration."""

import unittest
from unittest.mock import patch
import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import Config
from src.cli import build_parser, create_config


class TestConfig(unittest.TestCase):
    def test_valid_config(self):
        cfg = Config(
            package="A",
            repo="data/test_repo_simple.txt",
            test_mode=True,
            max_depth=5,
            filter_substr="X",
        )
        cfg.validate()  # should not raise

    def test_empty_package(self):
        cfg = Config(package="", repo="foo", test_mode=False)
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_negative_depth(self):
        cfg = Config(package="A", repo="foo", max_depth=-1)
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_as_dict(self):
        cfg = Config(package="pkg", repo="url", test_mode=True, max_depth=3)
        d = cfg.as_dict()
        self.assertEqual(d["package"], "pkg")
        self.assertEqual(d["test_mode"], True)
        self.assertEqual(d["max_depth"], 3)


class TestParser(unittest.TestCase):
    def test_required_args(self):
        parser = build_parser()
        args = parser.parse_args(["-p", "busybox", "-r", "http://example.com"])
        self.assertEqual(args.package, "busybox")
        self.assertEqual(args.repo, "http://example.com")
        self.assertFalse(args.test)

    def test_all_flags(self):
        parser = build_parser()
        args = parser.parse_args([
            "--package", "A",
            "--repo", "data/test.txt",
            "--test",
            "--depth", "7",
            "--filter", "util",
            "--stage1",
        ])
        self.assertTrue(args.test)
        self.assertEqual(args.depth, 7)
        self.assertEqual(args.filter, "util")
        self.assertTrue(args.stage1)


if __name__ == "__main__":
    unittest.main()