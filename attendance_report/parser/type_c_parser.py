from .type_b_parser import TypeBParser


class TypeCParser(TypeBParser):
    """Parser for TYPE_C reports.

    Current TYPE_C layout is aligned with TYPE_B, so this parser reuses
    TYPE_B parsing behavior while keeping an explicit extension point.
    """
