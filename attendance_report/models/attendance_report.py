from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .attendance_row import AttendanceRow


@dataclass
class AttendanceReport:
    """Domain object representing full attendance report."""
    report_type: str  # "TYPE_A" or "TYPE_B"
    source_path: Path
    company_name: str = ""
    employee_name: str = ""
    month_label: str = ""
    rows: tuple = field(default_factory=tuple)  # tuple of AttendanceRow
    summary: dict = field(default_factory=dict)  # dict[str, Any]
