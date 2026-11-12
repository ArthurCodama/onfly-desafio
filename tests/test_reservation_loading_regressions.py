"""Regression coverage for complete CSV ingestion."""

import pytest
from helpers import run_cli


@pytest.mark.parametrize("count", [199, 200, 201, 300])
def test_all_rows_reach_report(tmp_path, count):
    rows = [{"reservation_id": f"R-{index}", "amount": "1.00"} for index in range(count - 1)]
    rows.append({"reservation_id": "LAST", "amount": "7.00", "rooms": "2"})
    report = run_cli(tmp_path, rows)
    assert report["summary"]["total_reservations"] == count
    assert report["summary"]["confirmed_reservations"] == count
    assert report["summary"]["total_room_nights"] == count + 1
    assert report["summary"]["total_amount_brl"] == f"{count + 6}.00"
    assert report["by_month"][0]["reservations"] == count
    assert report["top_hotels"][0]["total_brl"] == f"{count + 6}.00"
