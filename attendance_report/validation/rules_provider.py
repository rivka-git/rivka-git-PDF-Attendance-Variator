from dataclasses import dataclass
from decimal import Decimal

from .validation_rules import ValidationRules


@dataclass(frozen=True)
class ReportRules:
    """Configurable validation envelope for a report type."""

    min_working_hours: Decimal
    max_working_hours: Decimal
    min_break_minutes: int
    max_break_minutes: int


DEFAULT_RULES_REGISTRY = {
    "TYPE_A": ReportRules(
        min_working_hours=ValidationRules.MIN_WORKING_HOURS,
        max_working_hours=ValidationRules.MAX_WORKING_HOURS,
        min_break_minutes=ValidationRules.MIN_BREAK_MINUTES,
        max_break_minutes=ValidationRules.MAX_BREAK_MINUTES,
    ),
    "TYPE_B": ReportRules(
        min_working_hours=ValidationRules.MIN_WORKING_HOURS,
        max_working_hours=ValidationRules.MAX_WORKING_HOURS,
        min_break_minutes=ValidationRules.MIN_BREAK_MINUTES,
        max_break_minutes=ValidationRules.MAX_BREAK_MINUTES,
    ),
}


class RulesProvider:
    """Injectable model that owns and exposes rules by report type."""

    def __init__(self, registry: dict | None = None):
        self._registry = dict(registry if registry is not None else DEFAULT_RULES_REGISTRY)

    def get(self, report_type: str):
        return self._registry.get(report_type)

    def register(self, report_type: str, rules: ReportRules) -> None:
        self._registry[report_type] = rules

    def known_types(self) -> list[str]:
        return sorted(self._registry)


DEFAULT_RULES_PROVIDER = RulesProvider()
