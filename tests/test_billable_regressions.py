"""Nonbillable bookings are counted but never aggregated."""

from helpers import run_cli


def test_nonbillable_hotels_and_months_are_excluded(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"status": "CONFIRMED", "amount": "100.00"},
            {
                "status": "NO_SHOW",
                "hotel_id": "H99",
                "checkin_date": "2025-02-01",
                "checkout_date": "2025-02-02",
                "amount": "900.00",
            },
            {
                "status": "CANCELLED",
                "hotel_id": "H98",
                "checkin_date": "2025-03-01",
                "checkout_date": "2025-03-02",
                "amount": "800.00",
            },
        ],
    )
    assert report["summary"] == {
        "total_reservations": 3,
        "confirmed_reservations": 1,
        "cancelled_reservations": 1,
        "no_show_reservations": 1,
        "total_room_nights": 1,
        "total_amount_brl": "100.00",
        "average_nightly_rate_brl": "100.00",
    }
    assert report["by_month"] == [{"month": "2025-01", "reservations": 1, "room_nights": 1, "total_brl": "100.00"}]
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01"]


def test_all_nonbillable_input(tmp_path):
    report = run_cli(tmp_path, [{"status": "NO_SHOW"}, {"status": "CANCELLED"}])
    assert report["summary"] == {
        "total_reservations": 2,
        "confirmed_reservations": 0,
        "cancelled_reservations": 1,
        "no_show_reservations": 1,
        "total_room_nights": 0,
        "total_amount_brl": "0.00",
        "average_nightly_rate_brl": "0.00",
    }
    assert report["by_month"] == report["top_hotels"] == []


def test_empty_input(tmp_path):
    report = run_cli(tmp_path, [])
    assert report["summary"] == {
        "total_reservations": 0,
        "confirmed_reservations": 0,
        "cancelled_reservations": 0,
        "no_show_reservations": 0,
        "total_room_nights": 0,
        "total_amount_brl": "0.00",
        "average_nightly_rate_brl": "0.00",
    }
    assert report["by_month"] == report["top_hotels"] == []
