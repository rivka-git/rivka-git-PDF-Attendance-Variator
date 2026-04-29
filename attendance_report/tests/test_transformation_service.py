from pathlib import Path
from datetime import time

from attendance_report.models import AttendanceReport, AttendanceRow
from attendance_report.validation import (
    AuditObserver,
    ReportRules,
    RulesProvider,
    TransformationService,
    ValidatingStrategyDecorator,
)
from attendance_report.validation.transformation_strategy import BaseTransformationStrategy


class _IdentityStrategy(BaseTransformationStrategy):
    def transform_row(self, row: AttendanceRow) -> AttendanceRow:
        return row


class _BrokenStrategy(BaseTransformationStrategy):
    def transform_row(self, row: AttendanceRow) -> AttendanceRow:
        # Always invalid so decorator raises and service falls back.
        return AttendanceRow(work_date=row.work_date, entry_time=row.exit_time, exit_time=row.entry_time)


def _report() -> AttendanceReport:
    return AttendanceReport(
        report_type="TYPE_A",
        source_path=Path("sample.pdf"),
        rows=(
            AttendanceRow(day_name="ראשון", entry_time=time(8, 0), exit_time=time(17, 0)),
            AttendanceRow(day_name="שני", entry_time=time(8, 10), exit_time=time(17, 5)),
            AttendanceRow(day_name="שלישי", entry_time=time(8, 20), exit_time=time(17, 10)),
        ),
    )


def test_observer_receives_events_and_completion_summary():
    audit = AuditObserver()
    service = TransformationService(
        strategy_registry={"TYPE_A": _IdentityStrategy()},
        rules_provider=RulesProvider(),
        observers=[audit],
    )

    service.transform_report(_report())

    summary = audit.summary()
    assert summary["row_count"] == 3
    assert summary["fallback_count"] == 0


def test_service_uses_fallback_and_observer_counts_it():
    audit = AuditObserver()
    service = TransformationService(
        strategy_registry={"TYPE_A": ValidatingStrategyDecorator(_BrokenStrategy())},
        rules_provider=RulesProvider(),
        observers=[audit],
    )

    transformed = service.transform_report(_report())

    assert len(transformed.rows) == 3
    assert audit.summary()["fallback_count"] == 3


def test_rules_provider_is_injectable_for_known_types():
    custom_provider = RulesProvider(
        {"TYPE_A": ReportRules(min_working_hours=0, max_working_hours=24, min_break_minutes=0, max_break_minutes=180)}
    )
    service = TransformationService(
        strategy_registry={"TYPE_A": _IdentityStrategy()},
        rules_provider=custom_provider,
        observers=[],
    )

    transformed = service.transform_report(_report())
    assert len(transformed.rows) == 3
