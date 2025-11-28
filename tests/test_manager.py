from pathlib import Path

from alarms.manager import AlarmManager


def test_add_and_list_alarms(tmp_path: Path):
    storage = tmp_path / "alarms.json"
    manager = AlarmManager(storage_path=storage)
    manager.add_alarm("08:15", label="Pobudka")
    manager.add_alarm("21:30", label="Przypomnienie", repeat_days=[0, 2])

    alarms = manager.list_alarms()
    assert len(alarms) == 2
    assert alarms[0].label == "Pobudka"
    assert alarms[1].repeat_days == (0, 2)


def test_remove_alarm(tmp_path: Path):
    storage = tmp_path / "alarms.json"
    manager = AlarmManager(storage_path=storage)
    alarm = manager.add_alarm("08:15")
    assert manager.remove_alarm(alarm.alarm_id)
    assert not manager.list_alarms()


def test_toggle_alarm(tmp_path: Path):
    storage = tmp_path / "alarms.json"
    manager = AlarmManager(storage_path=storage)
    alarm = manager.add_alarm("08:15")
    assert manager.toggle_alarm(alarm.alarm_id, False)
    stored = manager.get_alarm(alarm.alarm_id)
    assert stored is not None
    assert stored.enabled is False
