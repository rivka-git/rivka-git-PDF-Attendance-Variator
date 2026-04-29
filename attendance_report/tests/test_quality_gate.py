from pathlib import Path

from attendance_report.models import AttendanceReport
from main import _passes_quality_gate


def _report(report_type: str) -> AttendanceReport:
    return AttendanceReport(report_type=report_type, source_path=Path("sample.pdf"))


def test_type_a_quality_gate_non_strict_allows_missing_dates_when_time_coverage_high():
    metrics = {"rows": 10, "date": 0.20, "entry": 0.95, "exit": 0.95, "total_hours": 0.95}

    assert _passes_quality_gate(_report("TYPE_A"), metrics, strict_quality=False)


def test_type_a_quality_gate_strict_requires_date_coverage_threshold():
    metrics = {"rows": 10, "date": 0.79, "entry": 0.95, "exit": 0.95, "total_hours": 0.95}

    assert not _passes_quality_gate(_report("TYPE_A"), metrics, strict_quality=True)


def test_type_a_quality_gate_strict_passes_when_all_thresholds_met():
    metrics = {"rows": 10, "date": 0.80, "entry": 0.95, "exit": 0.95, "total_hours": 0.95}

    assert _passes_quality_gate(_report("TYPE_A"), metrics, strict_quality=True)
