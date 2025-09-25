"""Runtime scheduler that waits for alarms and notifies the user."""

from __future__ import annotations

import sys
import threading
import time
from datetime import datetime
from typing import Callable, Iterable, Optional

from .manager import AlarmManager
from .models import Alarm

NotificationCallback = Callable[[Alarm, datetime], None]


def default_notifier(alarm: Alarm, trigger_time: datetime) -> None:
    message = f"\n🔔 {trigger_time:%Y-%m-%d %H:%M} - {alarm.label} (#{alarm.alarm_id})"
    print(message)
    print("Naciśnij Ctrl+C aby przerwać działanie budzika.")


class AlarmScheduler:
    """Continuously monitors alarms and fires them when the time comes."""

    def __init__(
        self,
        manager: AlarmManager,
        notifier: NotificationCallback = default_notifier,
        refresh_interval: float = 30.0,
    ) -> None:
        self.manager = manager
        self.notifier = notifier
        self.refresh_interval = max(1.0, refresh_interval)
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def run(self, *, once: bool = False) -> None:
        try:
            while not self._stop_event.is_set():
                now = datetime.now()
                alarms = [
                    (alarm.next_trigger(now), alarm)
                    for alarm in self.manager.list_alarms()
                    if alarm.enabled
                ]
                alarms = [(trigger, alarm) for trigger, alarm in alarms if trigger]

                if not alarms:
                    print("Brak aktywnych budzików. Dodaj nowy budzik aby rozpocząć.")
                    if once:
                        return
                    time.sleep(self.refresh_interval)
                    continue

                next_trigger, next_alarm = min(alarms, key=lambda pair: pair[0])
                wait_seconds = max(0.0, (next_trigger - datetime.now()).total_seconds())
                if wait_seconds > 0:
                    sleep_time = min(wait_seconds, self.refresh_interval)
                    self._stop_event.wait(timeout=sleep_time)
                    continue

                self.notifier(next_alarm, next_trigger)
                if once:
                    return
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nPrzerwano działanie budzika.")
            sys.exit(0)


def preview_schedule(alarms: Iterable[Alarm], count: int = 5) -> str:
    upcoming = []
    reference = datetime.now()
    for alarm in alarms:
        trigger = alarm.next_trigger(reference)
        if trigger:
            upcoming.append((trigger, alarm))
    upcoming.sort(key=lambda pair: pair[0])

    lines = []
    for trigger, alarm in upcoming[:count]:
        lines.append(f"{trigger:%Y-%m-%d %H:%M} — {alarm.label} (#{alarm.alarm_id})")
    return "\n".join(lines)
