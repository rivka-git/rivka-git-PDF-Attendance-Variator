from abc import ABC, abstractmethod
import logging
from pathlib import Path
from typing import Any

from ..models import AttendanceReport


logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Template Method base class for parsing."""
    
    def parse(self, raw_text: str, source_path: Path, report_type: str) -> AttendanceReport:
        """Template method defining the parse flow."""
        normalized_text = self._normalize_text(raw_text)
        metadata = self._parse_metadata(normalized_text)
        rows = self._parse_rows(normalized_text)
        summary = self._parse_summary(normalized_text)
        logger.debug("Parsed report_type=%s rows=%d", report_type, len(rows))
        
        return AttendanceReport(
            report_type=report_type,
            source_path=source_path,
            company_name=metadata.get("company_name", ""),
            employee_name=metadata.get("employee_name", ""),
            month_label=metadata.get("month_label", ""),
            rows=rows,
            summary=summary
        )
    
    def _normalize_text(self, raw_text: str) -> str:
        """Clean up raw text: remove extra whitespace, normalize line endings."""
        lines = raw_text.split('\n')
        cleaned = [line.rstrip() for line in lines]
        return '\n'.join(cleaned)
    
    @abstractmethod
    def _parse_metadata(self, text: str) -> dict[str, Any]:
        """Extract company name, employee name, month label."""
        pass
    
    def _parse_rows(self, text: str) -> tuple[Any, ...]:
        """Extract attendance rows. Returns tuple of AttendanceRow."""
        rows = []
        for line in text.splitlines():
            if self._is_header_line(line):
                continue
            row = self._parse_row(line)
            if row is not None:
                rows.append(row)
        return tuple(rows)

    def _parse_row(self, line: str) -> Any:
        """Parse one content line into AttendanceRow or None."""
        return None

    def _is_header_line(self, line: str) -> bool:
        """Decide whether line is a table/header line and should be skipped."""
        return False
    
    @abstractmethod
    def _parse_summary(self, text: str) -> dict[str, Any]:
        """Extract summary totals."""
        pass
