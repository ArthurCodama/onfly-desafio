"""Rank exact hotel aggregates before applying the limit."""

import pytest
from helpers import run_cli


@pytest.mark.parametrize("top,expected", [(1, ["H03"]), (3, ["H03", "H01", "H02"]), (10, ["H03", "H01", "H02", "H04"])])
def test_ranking_aggregates_ties_and_limits(tmp_path, top, expected):
    report = run_cli(
        tmp_path,
        [
            {"hotel_id": "H02", "amount": "100.00"},
            {"hotel_id": "H01", "amount": "100.00"},
            {"hotel_id": "H03", "amount": "60.00"},
            {"hotel_id": "H03", "amount": "60.00"},
            {"hotel_id": "H04", "amount": "10.00"},
        ],
        top=top,
    )
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == expected
    assert report["top_hotels"][0]["total_brl"] == "120.00"
    assert report["top_hotels"][0]["room_nights"] == 2


def test_ranking_uses_exact_totals_before_display_rounding(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"hotel_id": "H01", "amount": "1.001"},
            {"hotel_id": "H02", "amount": "1.004"},
        ],
    )
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H02", "H01"]
    assert [hotel["total_brl"] for hotel in report["top_hotels"]] == ["1.00", "1.00"]
