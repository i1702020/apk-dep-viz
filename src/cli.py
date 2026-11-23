"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from .config import Config
from .fetcher import DependencyFetcher
from .graph import DependencyGraph
from .visualizer import print_graphviz


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="apk-dep-viz",
        description=(
            "Визуализация графа зависимостей пакетов Alpine Linux (apk). "
            "Вариант №28."
        ),
    )
    parser.add_argument(
        "-p",
        "--package",
        required=True,
        help="Имя анализируемого пакета",
    )
    parser.add_argument(
        "-r",
        "--repo",
        required=True,
        help="URL репозитория или путь к файлу тестового репозитория",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Режим работы с тестовым репозиторием",
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=10,
        help="Максимальная глубина анализа зависимостей (по умолчанию 10)",
    )
    parser.add_argument(
        "-f",
        "--filter",
        default=None,
        help="Подстрока для фильтрации пакетов (игнорировать пакеты, содержащие подстроку)",
    )
    parser.add_argument(
        "--stage1",
        action="store_true",
        help="Только вывести параметры конфигурации (ключ=значение) и выйти",
    )
    parser.add_argument(
        "--direct-only",
        action="store_true",
        help="Вывести только прямые зависимости (этап 2)",
    )
    return parser


def create_config(args: argparse.Namespace) -> Config:
    cfg = Config(
        package=args.package,
        repo=args.repo,
        test_mode=args.test,
        max_depth=args.depth,
        filter_substr=args.filter,
    )
    cfg.validate()
    return cfg


def print_config(cfg: Config) -> None:
    """Stage 1: print all user-configurable parameters as key=value."""
    for key, value in cfg.as_dict().items():
        print(f"{key}={value}")


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        cfg = create_config(args)
    except ValueError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return 1

    # Stage 1 only
    if args.stage1:
        print_config(cfg)
        return 0

    fetcher = DependencyFetcher(repo=cfg.repo, test_mode=cfg.test_mode)

    # Stage 2: direct dependencies only
    if args.direct_only:
        try:
            deps = fetcher.get_direct_dependencies(cfg.package)
        except Exception as exc:  # noqa: BLE001
            print(f"Ошибка получения зависимостей: {exc}", file=sys.stderr)
            return 1
        print(f"Прямые зависимости пакета '{cfg.package}':")
        if not deps:
            print("  (нет)")
        else:
            for d in deps:
                print(f"  - {d}")
        return 0

    # Stages 3 + 5: build graph and visualize
    graph = DependencyGraph(
        fetcher=fetcher,
        max_depth=cfg.max_depth,
        filter_substr=cfg.filter_substr,
    )
    graph.build(cfg.package)

    if graph.has_cycles():
        print(
            f"[info] Обнаружены циклические зависимости: {graph.get_cycles()}",
            file=sys.stderr,
        )

    print_graphviz(
        edges=graph.get_adjacency(),
        nodes=graph.nodes,
        root=cfg.package,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
