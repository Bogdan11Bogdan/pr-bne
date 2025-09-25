"""Simple alarm application package."""

from .models import Alarm
from .manager import AlarmManager
from .scheduler import AlarmScheduler

try:  # pragma: no cover - tkinter may be unavailable in some environments
    from .gui import AlarmApp
except Exception:  # pragma: no cover - fallback for headless setups
    AlarmApp = None  # type: ignore[assignment]

__all__ = ["Alarm", "AlarmManager", "AlarmScheduler", "AlarmApp"]
