"""Fetching direct dependencies for Alpine (apk) and test repositories."""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Set


class DependencyFetcher:
    """Responsible for obtaining direct dependencies of a package."""

    def __init__(self, repo: str, test_mode: bool = False):
        self.repo = repo
        self.test_mode = test_mode
        self._test_graph: Dict[str, List[str]] | None = None

    def get_direct_dependencies(self, package: str) -> List[str]:
        """
        Return list of direct dependency names for the given package.

        In test mode reads a local graph description file.
        In normal mode attempts to fetch Alpine package index information.
        """
        if self.test_mode:
            return self._get_from_test_repo(package)
        return self._get_from_apk_repo(package)

    def get_all_packages(self) -> Set[str]:
        """Return set of all known package names (useful in test mode)."""
        if self.test_mode:
            self._ensure_test_graph()
            assert self._test_graph is not None
            packages: Set[str] = set(self._test_graph.keys())
            for deps in self._test_graph.values():
                packages.update(deps)
            return packages
        return set()

    # ------------------------------------------------------------------
    # Test repository
    # ------------------------------------------------------------------

    def _ensure_test_graph(self) -> None:
        if self._test_graph is not None:
            return
        self._test_graph = self._parse_test_file(Path(self.repo))

    def _parse_test_file(self, path: Path) -> Dict[str, List[str]]:
        """
        Parse simple test repository format:

            PACKAGE: DEP1 DEP2 DEP3
            ...
        """
        graph: Dict[str, List[str]] = {}
        with path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" not in line:
                    raise ValueError(
                        f"Некорректный формат строки {line_no} в тестовом файле: {line}"
                    )
                pkg, deps_str = line.split(":", 1)
                pkg = pkg.strip().upper()
                deps = [d.strip().upper() for d in deps_str.split() if d.strip()]
                if not pkg:
                    raise ValueError(f"Пустое имя пакета в строке {line_no}")
                graph[pkg] = deps
        return graph

    def _get_from_test_repo(self, package: str) -> List[str]:
        self._ensure_test_graph()
        assert self._test_graph is not None
        key = package.upper()
        if key not in self._test_graph:
            # Package may appear only as a dependency
            return []
        return list(self._test_graph[key])

    # ------------------------------------------------------------------
    # Real Alpine repository (simplified)
    # ------------------------------------------------------------------

    def _get_from_apk_repo(self, package: str) -> List[str]:
        """
        Attempt to obtain direct dependencies of an Alpine package.

        Strategy (no package managers used):
        1. Try to fetch the HTML page from packages.alpinelinux.org
           and parse the "Dependencies" section.
        2. Fallback: error message suggesting test mode.

        Note: full correct resolution of apk dependencies is complex
        (versions, architectures, provides). This implementation is
        intentionally simplified for educational purposes.
        """
        deps = self._fetch_from_packages_site(package)
        if deps is not None:
            return deps

        raise RuntimeError(
            f"Не удалось получить зависимости для пакета '{package}' "
            f"из репозитория '{self.repo}'. "
            "Используйте --test с локальным файлом описания графа."
        )

    def _fetch_from_packages_site(self, package: str) -> List[str] | None:
        """Fetch and parse dependencies from packages.alpinelinux.org."""
        versions = ["edge", "v3.20", "v3.19", "v3.18"]
        for ver in versions:
            url = (
                f"https://pkgs.alpinelinux.org/package/{ver}/main/x86_64/{package}"
            )
            try:
                with urllib.request.urlopen(url, timeout=10) as resp:
                    html = resp.read().decode("utf-8", errors="ignore")
                deps = self._parse_alpine_html(html)
                if deps is not None:
                    return deps
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
                continue
        return None

    def _parse_alpine_html(self, html: str) -> List[str] | None:
        """Very simple extraction of dependency links from the packages page."""
        match = re.search(
            r"Dependencies.*?</th>\s*<td[^>]*>(.*?)</td>",
            html,
            re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return None
        section = match.group(1)
        names = re.findall(r">([a-zA-Z0-9._+-]+)<", section)
        deps = [n for n in names if n and not n.startswith("http")]
        seen: Set[str] = set()
        result: List[str] = []
        for d in deps:
            if d not in seen:
                seen.add(d)
                result.append(d)
        return result
