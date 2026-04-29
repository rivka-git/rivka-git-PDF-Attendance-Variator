from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class AttendanceRow:
    """Domain object representing a single attendance record."""
    work_date: Optional[date] = None
    location: Optional[str] = None
    day_name: Optional[str] = None
    entry_time: Optional[time] = None
    exit_time: Optional[time] = None
    total_hours: Optional[Decimal] = None
    notes: Optional[str] = None
    
    # Optional fields for TYPE_B
    break_minutes: Optional[int] = None
    overtime_125_hours: Optional[Decimal] = None
    overtime_150_hours: Optional[Decimal] = None
    saturday_hours: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    amount_to_pay: Optional[Decimal] = None

    def __post_init__(self) -> None:
        """Fail fast on invalid domain values."""
        if self.entry_time is not None and self.exit_time is not None:
            if self.exit_time <= self.entry_time:
                raise ValueError("exit_time must be later than entry_time")

        if self.total_hours is not None and self.total_hours < Decimal("0"):
            raise ValueError("total_hours cannot be negative")
