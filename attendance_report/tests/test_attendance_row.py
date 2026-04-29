from datetime import time
from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from attendance_report.models import AttendanceRow


def test_row_is_immutable_after_creation():
    row = AttendanceRow(entry_time=time(8, 0), exit_time=time(17, 0), total_hours=Decimal("9.00"))

    with pytest.raises(FrozenInstanceError):
        row.entry_time = time(9, 0)


def test_row_rejects_exit_before_or_equal_entry():
    with pytest.raises(ValueError):
        AttendanceRow(entry_time=time(9, 0), exit_time=time(9, 0), total_hours=Decimal("0.00"))

    with pytest.raises(ValueError):
        AttendanceRow(entry_time=time(10, 0), exit_time=time(9, 30), total_hours=Decimal("-0.50"))


def test_row_rejects_negative_total_hours():
    with pytest.raises(ValueError):
        AttendanceRow(entry_time=time(8, 0), exit_time=time(17, 0), total_hours=Decimal("-1.00"))
