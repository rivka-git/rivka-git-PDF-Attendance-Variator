from datetime import date, time
from decimal import Decimal

import main as app
from attendance_report.models import AttendanceReport, AttendanceRow


class _FakeExtractor:
    def extract(self, pdf_path):
        return "synthetic OCR text"


class _FakeClassifier:
    def classify(self, raw_text: str) -> str:
        return "TYPE_A"


class _FakeParser:
    def parse(self, raw_text, source_path, report_type):
        return AttendanceReport(
            report_type=report_type,
            source_path=source_path,
            company_name="Demo Co",
            employee_name="Student",
            month_label="04/2026",
            rows=(
                AttendanceRow(
                    work_date=date(2026, 4, 1),
                    day_name="Wednesday",
                    entry_time=time(8, 0),
                    exit_time=time(17, 0),
                    total_hours=Decimal("9.00"),
                ),
            ),
            summary={"rows": 1},
        )


def test_main_pipeline_runs_end_to_end_without_real_ocr(tmp_path, monkeypatch):
    input_pdf = tmp_path / "input.pdf"
    output_dir = tmp_path / "out"
    input_pdf.write_bytes(b"fake pdf content")

    monkeypatch.setattr(app, "TextExtractor", _FakeExtractor)
    monkeypatch.setattr(app, "Classifier", _FakeClassifier)
    monkeypatch.setattr(app.ParserFactory, "get_parser", lambda _report_type: _FakeParser())

    exit_code = app.main([str(input_pdf), "-o", str(output_dir)])

    assert exit_code == 0
    assert (output_dir / "input_output.pdf").exists()
