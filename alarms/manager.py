"""High level API for interacting with alarms."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Iterable, List, Optional

from .models import Alarm, validate_days


class AlarmManager:
    """Stores and retrieves alarms from a JSON file."""

    def __init__(self, storage_path: Optional[os.PathLike[str]] = None) -> None:
        self.storage_path = Path(storage_path or Path.home() / ".alarms.json")
        self._alarms: List[Alarm] = []
        self._loaded = False

    # ------------------------------------------------------------------
    # Internal helpers
    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        if self.storage_path.exists():
            with self.storage_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            self._alarms = [Alarm.from_dict(item) for item in data]
        else:
            self._alarms = []
        self._loaded = True

    def _save(self) -> None:
        payload = [alarm.to_dict() for alarm in self._alarms]
        temp_path = self.storage_path.with_suffix(".tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        temp_path.replace(self.storage_path)

    # ------------------------------------------------------------------
    # Public operations
    def list_alarms(self) -> List[Alarm]:
        self._ensure_loaded()
        return list(self._alarms)

    def add_alarm(
        self,
        time_str: str,
        label: str = "Alarm",
        repeat_days: Optional[Iterable[int]] = None,
        enabled: bool = True,
    ) -> Alarm:
        self._ensure_loaded()
        repeat_days = validate_days(repeat_days or [])
        alarm = Alarm(time_str=time_str, label=label, repeat_days=repeat_days, enabled=enabled)
        alarm_id = alarm.alarm_id or uuid.uuid4().hex
        alarm = alarm.with_id(alarm_id)
        self._alarms.append(alarm)
        self._save()
        return alarm

    def remove_alarm(self, alarm_id: str) -> bool:
        self._ensure_loaded()
        before = len(self._alarms)
        self._alarms = [alarm for alarm in self._alarms if alarm.alarm_id != alarm_id]
        removed = len(self._alarms) != before
        if removed:
            self._save()
        return removed

    def toggle_alarm(self, alarm_id: str, enabled: bool) -> bool:
        self._ensure_loaded()
        updated = False
        for alarm in self._alarms:
            if alarm.alarm_id == alarm_id:
                alarm.enabled = enabled
                updated = True
                break
        if updated:
            self._save()
        return updated

    def get_alarm(self, alarm_id: str) -> Optional[Alarm]:
        self._ensure_loaded()
        for alarm in self._alarms:
            if alarm.alarm_id == alarm_id:
                return alarm
        return None
