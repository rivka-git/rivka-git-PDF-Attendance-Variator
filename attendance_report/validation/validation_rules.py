from decimal import Decimal

from ..config import (
    MAX_BREAK_MINUTES as CFG_MAX_BREAK_MINUTES,
    MAX_TOTAL_MISMATCH_HOURS as CFG_MAX_TOTAL_MISMATCH_HOURS,
    MAX_WORKING_HOURS as CFG_MAX_WORKING_HOURS,
    MIN_BREAK_MINUTES as CFG_MIN_BREAK_MINUTES,
    MIN_WORKING_HOURS as CFG_MIN_WORKING_HOURS,
)
from ..models import AttendanceRow


class ValidationRules:
    """Business rules for validating attendance rows."""
    
    # Time boundaries (in hours)
    MIN_WORKING_HOURS = CFG_MIN_WORKING_HOURS
    MAX_WORKING_HOURS = CFG_MAX_WORKING_HOURS
    MAX_TOTAL_MISMATCH_HOURS = CFG_MAX_TOTAL_MISMATCH_HOURS
    
    # Break time (in minutes)
    MIN_BREAK_MINUTES = CFG_MIN_BREAK_MINUTES
    MAX_BREAK_MINUTES = CFG_MAX_BREAK_MINUTES
    
    @staticmethod
    def validate_row(row: AttendanceRow) -> bool:
        """
        Validate a single attendance row.
        
        Rules:
        - If entry and exit times exist: exit > entry
        - If total_hours exists: within reasonable range
        - If break_minutes exists: within reasonable range
        """
        if row.entry_time and row.exit_time:
            if row.exit_time <= row.entry_time:
                return False

            if row.total_hours is not None:
                entry_mins = (row.entry_time.hour * 60) + row.entry_time.minute
                exit_mins = (row.exit_time.hour * 60) + row.exit_time.minute
                worked = Decimal(exit_mins - entry_mins) / Decimal("60")

                if row.break_minutes is not None:
                    worked -= Decimal(row.break_minutes) / Decimal("60")

                if abs(worked - row.total_hours) > ValidationRules.MAX_TOTAL_MISMATCH_HOURS:
                    return False
        
        if row.total_hours:
            if row.total_hours < ValidationRules.MIN_WORKING_HOURS:
                return False
            if row.total_hours > ValidationRules.MAX_WORKING_HOURS:
                return False
        
        if row.break_minutes is not None:
            if row.break_minutes < ValidationRules.MIN_BREAK_MINUTES:
                return False
            if row.break_minutes > ValidationRules.MAX_BREAK_MINUTES:
                return False
        
        return True
