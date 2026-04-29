from ..models import AttendanceReport
from .observer import (
    LoggingObserver,
    ReportCompleteEvent,
    RowTransformedEvent,
    TransformationObserver,
)
from .rules_provider import DEFAULT_RULES_PROVIDER, RulesProvider
from .validating_decorator import TransformationError


class TransformationService:
    """Service that applies transformations to all rows in a report."""

    def __init__(
        self,
        strategy_registry: dict,
        rules_provider: RulesProvider | None = None,
        observers: list[TransformationObserver] | None = None,
    ):
        """
        Initialize with registry mapping report_type -> decorated strategy.
        
        Example:
            registry = {
                "TYPE_A": ValidatingStrategyDecorator(TypeATransformationStrategy()),
                "TYPE_B": ValidatingStrategyDecorator(TypeBTransformationStrategy()),
            }
        """
        self.registry = strategy_registry
        self.rules_provider = rules_provider if rules_provider is not None else DEFAULT_RULES_PROVIDER
        self.observers = observers if observers is not None else [LoggingObserver()]

    def _notify_row(self, event: RowTransformedEvent) -> None:
        for observer in self.observers:
            observer.on_row_transformed(event)

    def _notify_complete(self, event: ReportCompleteEvent) -> None:
        for observer in self.observers:
            observer.on_report_complete(event)

    def transform_report(self, report: AttendanceReport) -> AttendanceReport:
        """Apply transformation strategy to all rows in report."""
        if report.report_type not in self.registry:
            # No transformation strategy; return as-is
            return report

        if self.rules_provider.get(report.report_type) is None:
            # Unknown rule set for this report type; return as-is for safety.
            return report
        
        strategy = self.registry[report.report_type]
        transformed_rows = []
        fallback_count = 0
        for row in report.rows:
            try:
                transformed = strategy.transform_row(row)
                transformed_rows.append(transformed)
                self._notify_row(
                    RowTransformedEvent(
                        report_type=report.report_type,
                        original_row=row,
                        transformed_row=transformed,
                        used_fallback=False,
                    )
                )
            except TransformationError:
                # Required fallback behavior: preserve original row when validation fails.
                transformed_rows.append(row)
                fallback_count += 1
                self._notify_row(
                    RowTransformedEvent(
                        report_type=report.report_type,
                        original_row=row,
                        transformed_row=row,
                        used_fallback=True,
                    )
                )

        self._notify_complete(
            ReportCompleteEvent(
                report_type=report.report_type,
                row_count=len(transformed_rows),
                fallback_count=fallback_count,
            )
        )

        return AttendanceReport(
            report_type=report.report_type,
            source_path=report.source_path,
            company_name=report.company_name,
            employee_name=report.employee_name,
            month_label=report.month_label,
            rows=tuple(transformed_rows),
            summary=report.summary
        )
