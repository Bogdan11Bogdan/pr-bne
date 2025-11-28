"""Convenient entrypoint to run the alarms package."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List

from . import cli as cli_module
from .gui import launch
from .manager import AlarmManager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Uruchom aplikację alarmów w trybie graficznym (domyślnie) lub CLI.",
        add_help=True,
    )
    parser.add_argument(
        "--storage",
        type=Path,
        default=None,
        help="Ścieżka do pliku z budzikami (domyślnie ~/.alarms.json)",
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["gui", "cli"],
        default="gui",
        help="Wybierz tryb: gui lub cli (domyślnie gui)",
    )
    parser.add_argument(
        "cli_args",
        nargs=argparse.REMAINDER,
        help="Pozostałe argumenty przekazywane do trybu CLI, np. add 07:30 --label ...",
    )
    return parser


def _normalize_remainder(args: List[str]) -> List[str]:
    # argparse.REMAINDER pozostawia separator "--"; usuń go, jeśli jest pierwszym elementem.
    if args and args[0] == "--":
        return args[1:]
    return args


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.mode == "gui":
        manager = AlarmManager(storage_path=args.storage)
        launch(manager=manager)
        return 0

    cli_args = _normalize_remainder(list(args.cli_args))
    return cli_module.main(cli_args, storage_path=args.storage)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
