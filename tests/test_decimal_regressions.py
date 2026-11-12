"""Money stays exact until report serialization."""

from decimal import Decimal

import pytest
from helpers import run_cli

from onfly_report.services.currency_converter import convert_to_brl


@pytest.mark.parametrize("currency,expected", [("BRL", "0.10"), ("USD", "0.542"), ("EUR", "0.588")])
def test_exact_currency_multiplication(currency, expected):
    rates = {"BRL": Decimal("1"), "USD": Decimal("5.42"), "EUR": Decimal("5.88")}
    assert convert_to_brl(Decimal("0.10"), currency, rates) == Decimal(expected)


def test_conversion_does_not_lose_decimal_digits():
    amount = Decimal("123456789012345.123456")
    assert convert_to_brl(amount, "USD", {"USD": Decimal("5.42")}) == amount * Decimal("5.42")


def test_fractional_cents_are_summed_before_half_up_rounding(tmp_path):
    report = run_cli(tmp_path, [{"amount": "0.005"}, {"amount": "0.005"}, {"amount": "0.005"}])
    assert report["summary"]["total_amount_brl"] == "0.02"
    assert report["summary"]["average_nightly_rate_brl"] == "0.01"
    assert report["by_month"][0]["total_brl"] == "0.02"
    assert report["top_hotels"][0]["total_brl"] == "0.02"


def test_average_uses_unrounded_total(tmp_path):
    report = run_cli(tmp_path, [{"amount": "0.014", "rooms": "3"}])
    assert report["summary"]["total_amount_brl"] == "0.01"
    assert report["summary"]["average_nightly_rate_brl"] == "0.00"
