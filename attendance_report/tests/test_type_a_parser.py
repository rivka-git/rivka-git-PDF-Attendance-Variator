from datetime import date
from pathlib import Path

from attendance_report.parser import TypeAParser


def test_type_a_parser_parses_date_with_ocr_noise_and_dash_separator():
    parser = TypeAParser()
    text = "O5-O4-2O26 ראשון 08:00 17:00 00:00 8.50"

    report = parser.parse(text, Path("sample.pdf"), "TYPE_A")

    assert len(report.rows) == 1
    assert report.rows[0].work_date == date(2026, 4, 5)


def test_type_a_parser_parses_compact_date_token():
    parser = TypeAParser()
    text = "05042026 שני 08:00 17:00 00:00 8.50"

    report = parser.parse(text, Path("sample.pdf"), "TYPE_A")

    assert len(report.rows) == 1
    assert report.rows[0].work_date == date(2026, 4, 5)


def test_type_a_parser_falls_back_to_current_year_when_year_missing():
    parser = TypeAParser()
    text = "05/04 שלישי 08:00 17:00 00:00 8.50"

    report = parser.parse(text, Path("sample.pdf"), "TYPE_A")

    assert len(report.rows) == 1
    assert report.rows[0].work_date == date(date.today().year, 4, 5)
