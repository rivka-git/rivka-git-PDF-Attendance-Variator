from datetime import date, time
from decimal import Decimal

from attendance_report.models import AttendanceRow
from attendance_report.validation import TypeATransformationStrategy, TypeBTransformationStrategy


def _row() -> AttendanceRow:
    return AttendanceRow(
        work_date=date(2026, 4, 7),
        day_name="Tuesday",
        entry_time=time(8, 15),
        exit_time=time(17, 5),
        total_hours=Decimal("8.83"),
    )


def test_type_a_transformation_is_deterministic_for_same_input_row():
    strategy = TypeATransformationStrategy()
    row = _row()

    first = strategy.transform_row(row)
    second = strategy.transform_row(row)

    assert first == second


def test_type_b_transformation_is_deterministic_for_same_input_row():
    strategy = TypeBTransformationStrategy()
    row = _row()

    first = strategy.transform_row(row)
    second = strategy.transform_row(row)

    assert first == second
