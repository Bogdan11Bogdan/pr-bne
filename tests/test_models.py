from datetime import datetime

from alarms.models import Alarm


def test_alarm_next_trigger_daily_future_time():
    reference = datetime(2024, 1, 1, 8, 0)
    alarm = Alarm(time_str="09:30", label="Poranny alarm")
    trigger = alarm.next_trigger(reference)
    assert trigger == datetime(2024, 1, 1, 9, 30)


def test_alarm_next_trigger_daily_next_day():
    reference = datetime(2024, 1, 1, 10, 0)
    alarm = Alarm(time_str="09:30")
    trigger = alarm.next_trigger(reference)
    assert trigger == datetime(2024, 1, 2, 9, 30)


def test_alarm_next_trigger_specific_days():
    reference = datetime(2024, 1, 1, 8, 0)  # Monday
    alarm = Alarm(time_str="07:00", repeat_days=[2])  # Wednesday
    trigger = alarm.next_trigger(reference)
    assert trigger == datetime(2024, 1, 3, 7, 0)


def test_alarm_disabled_has_no_trigger():
    reference = datetime(2024, 1, 1, 8, 0)
    alarm = Alarm(time_str="07:00", enabled=False)
    assert alarm.next_trigger(reference) is None


def test_alarm_describe_schedule():
    alarm = Alarm(time_str="07:00", repeat_days=[0, 2, 4])
    assert alarm.describe_schedule() == "Pon, Śro, Pią"
