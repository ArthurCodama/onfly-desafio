"""Civil-date and occupancy regressions."""

import pytest
from helpers import run_cli


@pytest.mark.parametrize(
    "checkin,checkout,rooms,expected",
    [
        ("2025-01-30", "2025-02-02", 2, 6),
        ("2025-12-30", "2026-01-02", 3, 9),
        ("2024-02-28", "2024-03-01", 2, 4),
        ("2025-01-10", "2025-01-13", 2, 6),
        ("2025-01-10", "2025-01-10", 2, 0),
    ],
)
def test_civil_dates_and_rooms(tmp_path, checkin, checkout, rooms, expected):
    report = run_cli(tmp_path, [{"checkin_date": checkin, "checkout_date": checkout, "rooms": str(rooms)}])
    assert report["summary"]["total_room_nights"] == expected
    assert report["by_month"][0]["month"] == checkin[:7]
    assert report["by_month"][0]["room_nights"] == expected
    assert report["top_hotels"][0]["room_nights"] == expected
    if expected == 0:
        assert report["summary"]["average_nightly_rate_brl"] == "0.00"
