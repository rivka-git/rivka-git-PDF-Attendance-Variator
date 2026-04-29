from attendance_report.parser import ParserFactory, TypeCParser


def test_parser_factory_returns_type_c_parser() -> None:
    parser = ParserFactory.get_parser("TYPE_C")
    assert isinstance(parser, TypeCParser)
