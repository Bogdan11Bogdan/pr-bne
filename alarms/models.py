"""Data models for the alarm application."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Iterable, List, Optional, Sequence, Set


def _parse_time(value: str) -> time:
    try:
        hour_str, minute_str = value.split(":", 1)
        hour = int(hour_str)
        minute = int(minute_str)
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError
    except ValueError as exc:  # pragma: no cover - defensive branch
        raise ValueError(
            "Time must be in HH:MM format using 24 hour clock"
        ) from exc
    return time(hour=hour, minute=minute)


@dataclass
class Alarm:
    """Represents a single alarm configuration."""

    time_str: str
    label: str = "Alarm"
    repeat_days: Sequence[int] = field(default_factory=list)
    enabled: bool = True
    alarm_id: Optional[str] = None

    def __post_init__(self) -> None:
        self.time: time = _parse_time(self.time_str)
        self.repeat_days = tuple(sorted(set(self.repeat_days)))

    def with_id(self, alarm_id: str) -> "Alarm":
        clone = Alarm(
            time_str=self.time_str,
            label=self.label,
            repeat_days=self.repeat_days,
            enabled=self.enabled,
            alarm_id=alarm_id,
        )
        return clone

    def to_dict(self) -> dict:
        return {
            "alarm_id": self.alarm_id,
            "time": self.time_str,
            "label": self.label,
            "repeat_days": list(self.repeat_days),
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "Alarm":
        return cls(
            time_str=payload["time"],
            label=payload.get("label", "Alarm"),
            repeat_days=payload.get("repeat_days", ()),
            enabled=payload.get("enabled", True),
            alarm_id=payload.get("alarm_id"),
        )

    def next_trigger(self, reference: Optional[datetime] = None) -> Optional[datetime]:
        if not self.enabled:
            return None

        reference = reference or datetime.now()
        days: Set[int] = set(self.repeat_days)

        for offset in range(8):
            candidate_date = reference.date() + timedelta(days=offset)
            if days and candidate_date.weekday() not in days:
                continue
            candidate_dt = datetime.combine(candidate_date, self.time)
            if candidate_dt >= reference:
                return candidate_dt
        return None

    def matches_day(self, weekday: int) -> bool:
        return not self.repeat_days or weekday in self.repeat_days

    def describe_schedule(self) -> str:
        if not self.repeat_days:
            return "Codziennie"
        names = [
            "Pon",
            "Wto",
            "Śro",
            "Czw",
            "Pią",
            "Sob",
            "Nie",
        ]
        return ", ".join(names[day] for day in self.repeat_days)


def validate_days(days: Iterable[int]) -> List[int]:
    unique_days = sorted(set(days))
    for day in unique_days:
        if day < 0 or day > 6:
            raise ValueError("Days of week must be between 0 (Monday) and 6 (Sunday)")
    return unique_days
