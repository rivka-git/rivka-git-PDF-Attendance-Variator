import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..models import AttendanceRow

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RowTransformedEvent:
    report_type: str
    original_row: AttendanceRow
    transformed_row: AttendanceRow
    used_fallback: bool = False


@dataclass(frozen=True)
class ReportCompleteEvent:
    report_type: str
    row_count: int
    fallback_count: int


class TransformationObserver(ABC):
    @abstractmethod
    def on_row_transformed(self, event: RowTransformedEvent) -> None:
        pass

    @abstractmethod
    def on_report_complete(self, event: ReportCompleteEvent) -> None:
        pass


class LoggingObserver(TransformationObserver):
    def on_row_transformed(self, event: RowTransformedEvent) -> None:
        if event.used_fallback:
            logger.debug("[%s] fallback row preserved", event.report_type)

    def on_report_complete(self, event: ReportCompleteEvent) -> None:
        logger.info(
            "[%s] transformation complete: rows=%d, fallbacks=%d",
            event.report_type,
            event.row_count,
            event.fallback_count,
        )


class AuditObserver(TransformationObserver):
    """Observer useful for tests and quality audits."""

    def __init__(self) -> None:
        self._rows: list[RowTransformedEvent] = []
        self._complete: ReportCompleteEvent | None = None

    def on_row_transformed(self, event: RowTransformedEvent) -> None:
        self._rows.append(event)

    def on_report_complete(self, event: ReportCompleteEvent) -> None:
        self._complete = event

    def summary(self) -> dict:
        fallback_count = self._complete.fallback_count if self._complete else 0
        return {
            "row_count": len(self._rows),
            "fallback_count": fallback_count,
        }
