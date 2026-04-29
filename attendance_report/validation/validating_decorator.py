from ..models import AttendanceRow
from .transformation_strategy import BaseTransformationStrategy
from .validation_rules import ValidationRules


class TransformationError(Exception):
    """Raised when a transformed row fails validation checks."""


class ValidatingStrategyDecorator(BaseTransformationStrategy):
    """
    Decorator that wraps a transformation strategy.
    Validates the transformed row; if invalid, returns original unchanged.
    """
    
    def __init__(self, inner_strategy: BaseTransformationStrategy) -> None:
        self.inner = inner_strategy
    
    def transform_row(self, row: AttendanceRow) -> AttendanceRow:
        """Transform and validate; raise TransformationError on failure."""
        transformed = self.inner.transform_row(row)
        if not ValidationRules.validate_row(transformed):
            raise TransformationError("Transformed row failed validation")
        return transformed
