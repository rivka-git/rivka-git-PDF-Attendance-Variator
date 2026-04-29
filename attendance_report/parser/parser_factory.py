from .base_parser import BaseParser
from .type_a_parser import TypeAParser
from .type_b_parser import TypeBParser
from .type_c_parser import TypeCParser


class ParserFactory:
    """Factory to get the appropriate parser by type."""
    
    _parsers = {
        "TYPE_A": TypeAParser(),
        "TYPE_B": TypeBParser(),
        "TYPE_C": TypeCParser(),
    }
    
    @classmethod
    def get_parser(cls, report_type: str) -> BaseParser:
        """Return parser instance for given report type."""
        if report_type not in cls._parsers:
            raise ValueError(f"Unknown report type: {report_type}")
        return cls._parsers[report_type]
