"""CLI entry point for attendance report transformer."""

import argparse
import sys
from pathlib import Path

from attendance_report.classifier import Classifier
from attendance_report.exceptions import AttendanceReportError
from attendance_report.generator import PdfGenerator
from attendance_report.models import AttendanceReport
from attendance_report.ocr import TextExtractor
from attendance_report.parser import ParserFactory
from attendance_report.service import passes_quality_gate, report_completeness
from attendance_report.validation import (
    DEFAULT_RULES_PROVIDER,
    LoggingObserver,
    TransformationService,
    TypeATransformationStrategy,
    TypeBTransformationStrategy,
    ValidatingStrategyDecorator,
)


def _report_completeness(report: AttendanceReport) -> dict:
    return report_completeness(report)


def _passes_quality_gate(report: AttendanceReport, metrics: dict, strict_quality: bool = False) -> bool:
    return passes_quality_gate(report, metrics, strict_quality=strict_quality)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Transform attendance PDF reports with validation and reformatting."
    )
    parser.add_argument("input_pdf", type=Path, help="Path to input PDF file")
    parser.add_argument("-o", "--output-dir", type=Path, required=True, help="Output directory")
    parser.add_argument(
        "--strict-quality",
        action="store_true",
        help="Fail when parsed field coverage is not high enough for reliable output",
    )
    
    args = parser.parse_args(argv)
    
    # Validate input
    if not args.input_pdf.exists():
        print(f"Error: Input file not found: {args.input_pdf}", file=sys.stderr)
        return 1
    
    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Stage 1: Extract text from PDF
        print(f"[1/6] Extracting text from {args.input_pdf.name}...")
        extractor = TextExtractor()
        raw_text = extractor.extract(args.input_pdf)

        # Stage 2: Classify report type
        print("[2/6] Classifying report type...")
        classifier = Classifier()
        report_type = classifier.classify(raw_text)
        print(f"  -> Detected type: {report_type}")

        if report_type == "UNKNOWN":
            print("Warning: Could not determine report type. Skipping further processing.")
            return 0

        # Stage 3: Parse into domain object
        print("[3/6] Parsing into domain object...")
        parser = ParserFactory.get_parser(report_type)
        report = parser.parse(raw_text, args.input_pdf, report_type)
        print(f"  -> Extracted {len(report.rows)} rows")

        completeness = _report_completeness(report)
        print(
            "  -> Completeness: "
            f"date={completeness['date']:.0%}, "
            f"entry={completeness['entry']:.0%}, "
            f"exit={completeness['exit']:.0%}, "
            f"total={completeness['total_hours']:.0%}"
        )
        if not _passes_quality_gate(report, completeness, strict_quality=args.strict_quality):
            print("Error: Parsed data quality is too low for reliable output. Stopping before generation.")
            return 2

        # Stage 4: Transform and validate
        print("[4/6] Transforming and validating rows...")
        strategy_registry = {
            "TYPE_A": ValidatingStrategyDecorator(TypeATransformationStrategy()),
            "TYPE_B": ValidatingStrategyDecorator(TypeBTransformationStrategy()),
        }
        transformation_service = TransformationService(
            strategy_registry,
            rules_provider=DEFAULT_RULES_PROVIDER,
            observers=[LoggingObserver()],
        )
        transformed_report = transformation_service.transform_report(report)
        print("  -> Transformation complete")

        # Stage 5: Generate output PDF
        print("[5/6] Generating output PDF...")
        generator = PdfGenerator()
        output_pdf = args.output_dir / f"{args.input_pdf.stem}_output.pdf"
        generator.generate(transformed_report, output_pdf)
        print(f"  -> Output saved to {output_pdf}")

        # Stage 6: Complete
        print("[6/6] Process complete!")
        return 0
    
    except AttendanceReportError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
