from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal
from typing import Optional


@dataclass
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
