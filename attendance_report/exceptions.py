"""
Comprehensive exception hierarchy for attendance report processing.

Follows a clear hierarchy:
- AttendanceReportError (base)
  - OCRError
  - ClassificationError
  - ParsingError
  - ValidationError
  - GenerationError

Each exception carries context about what went wrong and suggestions for recovery.
"""


class AttendanceReportError(Exception):
    """Base exception for all attendance report processing errors."""
    
    def __init__(self, message: str, context: dict | None = None, suggestion: str = "") -> None:
        """
        Initialize exception with context and recovery suggestion.
        
        Args:
            message: Human-readable error description
            context: Dictionary of contextual data (file path, row number, etc.)
            suggestion: Helpful suggestion for recovery or debugging
        """
        self.message = message
        self.context = context or {}
        self.suggestion = suggestion
        super().__init__(self._format_error())
    
    def _format_error(self) -> str:
        """Format error with context and suggestion."""
        msg = f"[{self.__class__.__name__}] {self.message}"
        if self.context:
            msg += f"\nContext: {self.context}"
        if self.suggestion:
            msg += f"\nSuggestion: {self.suggestion}"
        return msg


class OCRError(AttendanceReportError):
    """Raised when PDF text extraction fails."""
    pass


class ClassificationError(AttendanceReportError):
    """Raised when report type classification is ambiguous or fails."""
    pass


class ParsingError(AttendanceReportError):
    """Raised when parsing raw text into domain objects fails."""
    pass


class ParseError(ParsingError):
    """Backward-compatible alias used by some assignment checklists."""
    pass


class ValidationError(AttendanceReportError):
    """Raised when row validation fails and recovery is impossible."""
    pass


class GenerationError(AttendanceReportError):
    """Raised when PDF generation or output writing fails."""
    pass


class ConfigurationError(AttendanceReportError):
    """Raised when configuration or initialization fails."""
    pass
