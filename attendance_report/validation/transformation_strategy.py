from abc import ABC, abstractmethod
from datetime import time
from decimal import Decimal

from ..models import AttendanceRow


class BaseTransformationStrategy(ABC):
    """Strategy base for transforming attendance rows."""
    
    @abstractmethod
    def transform_row(self, row: AttendanceRow) -> AttendanceRow:
        """Transform a row with type-specific logic."""
        pass


def _time_to_minutes(t: time) -> int:
    return (t.hour * 60) + t.minute


def _minutes_to_time(minutes: int) -> time:
    minutes = max(0, min((23 * 60) + 59, minutes))
    h = minutes // 60
    m = minutes % 60
    return time(h, m)


def _deterministic_offset(row: AttendanceRow, span: int = 10) -> int:
    token = f"{row.work_date}-{row.day_name}-{row.entry_time}-{row.total_hours}"
    return (sum(ord(ch) for ch in token) % (2 * span + 1)) - span


class TypeATransformationStrategy(BaseTransformationStrategy):
    """Apply logical transformations for TYPE_A rows."""
    
    def transform_row(self, row: AttendanceRow) -> AttendanceRow:
        """Apply deterministic transformations for TYPE_A."""
        if row.entry_time is None or row.exit_time is None:
            return row

        # Shift both entry/exit by deterministic offset so total duration remains stable.
        offset = _deterministic_offset(row, span=8)
        new_entry = _minutes_to_time(_time_to_minutes(row.entry_time) + offset)
        new_exit = _minutes_to_time(_time_to_minutes(row.exit_time) + offset)

        # Keep row unchanged when a shift could violate chronological order.
        if new_exit <= new_entry:
            return row

        # Recompute total_hours from shifted times for consistency.
        new_total = Decimal(_time_to_minutes(new_exit) - _time_to_minutes(new_entry)) / Decimal("60")

        return AttendanceRow(
            work_date=row.work_date,
            location=row.location,
            day_name=row.day_name,
            entry_time=new_entry,
            exit_time=new_exit,
            total_hours=new_total.quantize(Decimal("0.01")),
            notes=row.notes,
            break_minutes=row.break_minutes,
            overtime_125_hours=row.overtime_125_hours,
            overtime_150_hours=row.overtime_150_hours,
            saturday_hours=row.saturday_hours,
            hourly_rate=row.hourly_rate,
            amount_to_pay=row.amount_to_pay,
        )


class TypeBTransformationStrategy(BaseTransformationStrategy):
    """Apply logical transformations for TYPE_B rows."""
    
    def transform_row(self, row: AttendanceRow) -> AttendanceRow:
        """Apply deterministic transformations for TYPE_B."""
        # For sparse OCR rows, avoid inventing full shifts; only adjust when core fields exist.
        if row.entry_time is None or row.exit_time is None:
            return row

        offset = _deterministic_offset(row, span=6)
        new_entry = _minutes_to_time(_time_to_minutes(row.entry_time) + offset)
        new_exit = _minutes_to_time(_time_to_minutes(row.exit_time) + offset)

        if new_exit <= new_entry:
            return row

        total = Decimal(_time_to_minutes(new_exit) - _time_to_minutes(new_entry)) / Decimal("60")

        return AttendanceRow(
            work_date=row.work_date,
            location=row.location,
            day_name=row.day_name,
            entry_time=new_entry,
            exit_time=new_exit,
            total_hours=total.quantize(Decimal("0.01")),
            notes=row.notes,
            break_minutes=row.break_minutes,
            overtime_125_hours=row.overtime_125_hours,
            overtime_150_hours=row.overtime_150_hours,
            saturday_hours=row.saturday_hours,
            hourly_rate=row.hourly_rate,
            amount_to_pay=row.amount_to_pay,
        )
