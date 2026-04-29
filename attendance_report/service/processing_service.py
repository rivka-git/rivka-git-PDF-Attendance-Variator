from attendance_report.config import QUALITY_GATE_THRESHOLDS
from attendance_report.models import AttendanceReport


def report_completeness(report: AttendanceReport) -> dict:
    rows = report.rows
    total = len(rows)
    if total == 0:
        return {"rows": 0, "date": 0.0, "entry": 0.0, "exit": 0.0, "total_hours": 0.0}

    date_ratio = sum(1 for r in rows if r.work_date is not None) / total
    entry_ratio = sum(1 for r in rows if r.entry_time is not None) / total
    exit_ratio = sum(1 for r in rows if r.exit_time is not None) / total
    total_ratio = sum(1 for r in rows if r.total_hours is not None) / total
    return {
        "rows": total,
        "date": date_ratio,
        "entry": entry_ratio,
        "exit": exit_ratio,
        "total_hours": total_ratio,
    }


def passes_quality_gate(report: AttendanceReport, metrics: dict, strict_quality: bool = False) -> bool:
    if metrics["rows"] == 0:
        return False

    report_thresholds = QUALITY_GATE_THRESHOLDS.get(report.report_type)
    if report_thresholds is None:
        return False

    profile = "strict" if strict_quality else "non_strict"
    required = report_thresholds[profile]
    return all(metrics[field] >= threshold for field, threshold in required.items())
