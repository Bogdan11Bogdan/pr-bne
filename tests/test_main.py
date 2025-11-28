import json
from alarms.__main__ import _normalize_remainder, main


def test_main_cli_uses_provided_storage(tmp_path):
    storage = tmp_path / "alarms.json"
    exit_code = main(["--storage", str(storage), "cli", "add", "08:00", "--label", "Test"])
    assert exit_code == 0

    with storage.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert data[0]["label"] == "Test"


def test_normalize_remainder_strips_separator():
    assert _normalize_remainder(["--", "preview"]) == ["preview"]
    assert _normalize_remainder(["preview"]) == ["preview"]
