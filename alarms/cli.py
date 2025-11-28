"""Command line interface for managing alarms."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List

from .manager import AlarmManager
from .scheduler import AlarmScheduler, preview_schedule


def parse_weekdays(values: Iterable[str]) -> List[int]:
    mapping = {
        "mon": 0,
        "monday": 0,
        "pon": 0,
        "tue": 1,
        "tuesday": 1,
        "wto": 1,
        "wed": 2,
        "wednesday": 2,
        "śro": 2,
        "thu": 3,
        "thursday": 3,
        "czw": 3,
        "fri": 4,
        "friday": 4,
        "pia": 4,
        "sat": 5,
        "saturday": 5,
        "sob": 5,
        "sun": 6,
        "sunday": 6,
        "nie": 6,
    }
    days: List[int] = []
    for value in values:
        key = value.strip().lower()
        if key.isdigit():
            days.append(int(key))
            continue
        if key not in mapping:
            raise argparse.ArgumentTypeError(
                f"Nieznany dzień tygodnia: {value}. Użyj nazw (pon, tue, ...) lub numerów 0-6."
            )
        days.append(mapping[key])
    return days


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prosty menedżer budzików")
    parser.add_argument(
        "--storage",
        type=Path,
        default=None,
        help="Ścieżka do pliku z zapisanymi budzikami (domyślnie ~/.alarms.json)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Dodaj nowy budzik")
    add_parser.add_argument("time", help="Godzina w formacie HH:MM")
    add_parser.add_argument("--label", default="Alarm", help="Etykieta budzika")
    add_parser.add_argument(
        "--days",
        nargs="*",
        default=(),
        help="Dni tygodnia (np. pon, wed, 0-6). Brak oznacza codziennie.",
    )

    list_parser = subparsers.add_parser("list", help="Wyświetl istniejące budziki")

    remove_parser = subparsers.add_parser("remove", help="Usuń budzik po identyfikatorze")
    remove_parser.add_argument("alarm_id", help="Identyfikator budzika")

    toggle_parser = subparsers.add_parser("toggle", help="Włącz lub wyłącz budzik")
    toggle_parser.add_argument("alarm_id", help="Identyfikator budzika")
    toggle_parser.add_argument(
        "--enable",
        dest="enabled",
        action="store_true",
        default=None,
        help="Włącz budzik",
    )
    toggle_parser.add_argument(
        "--disable",
        dest="enabled",
        action="store_false",
        help="Wyłącz budzik",
    )

    run_parser = subparsers.add_parser("run", help="Uruchom harmonogram budzików")
    run_parser.add_argument(
        "--refresh",
        type=float,
        default=30.0,
        help="Jak często sprawdzać harmonogram (sekundy)",
    )
    run_parser.add_argument(
        "--once",
        action="store_true",
        help="Zakończ po pierwszym wyzwoleniu budzika",
    )

    subparsers.add_parser("preview", help="Pokaż najbliższe aktywacje budzików")

    return parser


def format_alarm_row(alarm) -> str:
    status = "Włączony" if alarm.enabled else "Wyłączony"
    schedule = alarm.describe_schedule()
    return f"#{alarm.alarm_id} | {alarm.time_str} | {schedule} | {status} | {alarm.label}"


def main(argv: Iterable[str] | None = None, *, storage_path=None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    manager = AlarmManager(storage_path=storage_path or args.storage)

    if args.command == "add":
        days = parse_weekdays(args.days)
        alarm = manager.add_alarm(time_str=args.time, label=args.label, repeat_days=days)
        print("Dodano budzik:")
        print(format_alarm_row(alarm))
        return 0

    if args.command == "list":
        alarms = manager.list_alarms()
        if not alarms:
            print("Brak zapisanych budzików.")
            return 0
        for alarm in alarms:
            print(format_alarm_row(alarm))
        return 0

    if args.command == "remove":
        removed = manager.remove_alarm(args.alarm_id)
        if removed:
            print("Usunięto budzik.")
            return 0
        print("Nie znaleziono budzika o podanym identyfikatorze.")
        return 1

    if args.command == "toggle":
        if args.enabled is None:
            parser.error("Użyj --enable lub --disable aby określić stan budzika.")
        updated = manager.toggle_alarm(args.alarm_id, args.enabled)
        if updated:
            print("Zmieniono stan budzika.")
            return 0
        print("Nie znaleziono budzika.")
        return 1

    if args.command == "run":
        scheduler = AlarmScheduler(manager, refresh_interval=args.refresh)
        scheduler.run(once=args.once)
        return 0

    if args.command == "preview":
        text = preview_schedule(manager.list_alarms())
        if text:
            print(text)
        else:
            print("Brak aktywnych budzików.")
        return 0

    parser.error("Nieznane polecenie")
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
