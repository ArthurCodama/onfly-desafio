"""End-to-end README examples and CLI contract."""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta

import pytest
from helpers import PROJECT_ROOT, SRC_DIR

from onfly_report.cli import main


def invoke(tmp_path, *arguments):
    return subprocess.run(
        [sys.executable, "-m", "onfly_report", *map(str, arguments)],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(SRC_DIR)},
        capture_output=True,
        text=True,
        timeout=60,
    )


def sample_arguments():
    return ["--input", PROJECT_ROOT / "data/exemplo-validacao.csv", "--rates", PROJECT_ROOT / "data/taxas_cambio.csv"]


def test_readme_sample_and_default_output(tmp_path):
    process = invoke(tmp_path, *sample_arguments())
    assert process.returncode == 0, process.stderr
    assert process.stdout.strip() == "Reservas: 12 | Confirmadas: 9 | Noites: 28 | Total BRL: 7566.00"
    report = json.loads((tmp_path / "output/report.json").read_text(encoding="utf-8"))
    assert set(report) == {"report_version", "generated_at", "summary", "by_month", "top_hotels"}
    assert report["report_version"] == "1.0"
    assert datetime.fromisoformat(report["generated_at"]).utcoffset() == timedelta(hours=-3)
    assert report["summary"] == {
        "total_reservations": 12,
        "confirmed_reservations": 9,
        "cancelled_reservations": 2,
        "no_show_reservations": 1,
        "total_room_nights": 28,
        "total_amount_brl": "7566.00",
        "average_nightly_rate_brl": "270.21",
    }
    assert report["by_month"] == [
        {"month": "2025-01", "reservations": 8, "room_nights": 25, "total_brl": "6684.00"},
        {"month": "2025-02", "reservations": 1, "room_nights": 3, "total_brl": "882.00"},
    ]
    assert report["top_hotels"] == [
        {"hotel_id": hotel_id, "hotel_name": name, "room_nights": nights, "total_brl": amount}
        for hotel_id, name, nights, amount in [
            ("H01", "Hotel Aurora Paulista", 3, "1200.00"),
            ("H02", "Hotel Mirante", 2, "1084.00"),
            ("H12", "Hotel Miami Beach", 1, "1000.00"),
            ("H10", "Hotel Madrid, Gran Vía", 4, "900.00"),
            ("H09", "Hotel Lisboa, Centro", 3, "882.00"),
        ]
    ]
    for key, value in report["summary"].items():
        if key.endswith("_brl"):
            assert isinstance(value, str) and re.fullmatch(r"\d+\.\d{2}", value)
        else:
            assert type(value) is int


def test_main_dataset_and_nested_output(tmp_path):
    output = tmp_path / "nested/reports/main.json"
    process = invoke(
        tmp_path,
        "--input",
        PROJECT_ROOT / "data/reservas_hoteis.csv",
        "--rates",
        PROJECT_ROOT / "data/taxas_cambio.csv",
        "--output",
        output,
    )
    assert process.returncode == 0, process.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["summary"]["total_reservations"] == 300
    months = [row["month"] for row in report["by_month"]]
    assert months == sorted(months)


@pytest.mark.parametrize("arguments", [[], ["--top", "0"], ["--top", "-1"], ["--top", "x"]])
def test_invalid_arguments_exit_two(tmp_path, arguments):
    args = sample_arguments() + arguments if arguments else []
    assert invoke(tmp_path, *args).returncode == 2
    assert not (tmp_path / "output/report.json").exists()


@pytest.mark.parametrize("kind", ["missing", "columns", "types"])
def test_invalid_input_exits_two(tmp_path, kind):
    source = tmp_path / "bad.csv"
    if kind == "columns":
        source.write_text("wrong\nvalue\n", encoding="utf-8")
    elif kind == "types":
        source.write_text(
            (PROJECT_ROOT / "data/exemplo-validacao.csv").read_text(encoding="utf-8").replace("2025-01-", "invalid-"),
            encoding="utf-8",
        )
    args = sample_arguments()
    args[1] = source
    assert invoke(tmp_path, *args).returncode == 2


def test_output_failure_exits_one(tmp_path):
    process = invoke(tmp_path, *sample_arguments(), "--output", tmp_path)
    assert process.returncode == 1


def test_unexpected_builder_failure_exits_one(tmp_path, monkeypatch):
    def fail(_self):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr("onfly_report.cli.ReportBuilder.build", fail)
    assert main([*map(str, sample_arguments()), "--output", str(tmp_path / "report.json")]) == 1
    assert not (tmp_path / "report.json").exists()
