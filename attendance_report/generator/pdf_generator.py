from pathlib import Path

from ..models import AttendanceReport
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PdfGenerator:
    """Generates PDF output from AttendanceReport object."""

    def _fmt_date(self, value) -> str:
        if value is None:
            return ""
        return value.strftime("%d/%m/%Y")

    def _fmt_time(self, value) -> str:
        if value is None:
            return ""
        return value.strftime("%H:%M")

    def _fmt_num(self, value) -> str:
        if value is None:
            return ""
        try:
            return f"{value:.2f}"
        except Exception:
            return str(value)

    def _table_for_type_a(self, report: AttendanceReport):
        headers = ["Date", "Day", "Entry", "Exit", "Total"]
        rows = [headers]
        for row in report.rows:
            rows.append(
                [
                    self._fmt_date(row.work_date),
                    row.day_name or "",
                    self._fmt_time(row.entry_time),
                    self._fmt_time(row.exit_time),
                    self._fmt_num(row.total_hours),
                ]
            )
        return rows

    def _table_for_type_b(self, report: AttendanceReport):
        headers = ["Date", "Day", "Entry", "Exit", "Total", "Notes"]
        rows = [headers]
        for row in report.rows:
            rows.append(
                [
                    self._fmt_date(row.work_date),
                    row.day_name or "",
                    self._fmt_time(row.entry_time),
                    self._fmt_time(row.exit_time),
                    self._fmt_num(row.total_hours),
                    row.notes or "",
                ]
            )
        return rows

    def generate(self, report: AttendanceReport, output_path: Path) -> Path:
        """
        Create PDF file from report.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(f"Attendance Report - {report.report_type}", styles["Title"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"Source: {report.source_path.name}", styles["Normal"]))
        if report.company_name:
            story.append(Paragraph(f"Company: {report.company_name}", styles["Normal"]))
        if report.employee_name:
            story.append(Paragraph(f"Employee: {report.employee_name}", styles["Normal"]))
        if report.month_label:
            story.append(Paragraph(f"Month: {report.month_label}", styles["Normal"]))

        story.append(Spacer(1, 12))

        if report.report_type == "TYPE_A":
            table_data = self._table_for_type_a(report)
            col_widths = [80, 80, 70, 70, 70]
        else:
            table_data = self._table_for_type_b(report)
            col_widths = [80, 70, 60, 60, 60, 100]

        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ]
            )
        )
        story.append(table)

        if report.summary:
            story.append(Spacer(1, 12))
            story.append(Paragraph("Summary", styles["Heading3"]))
            summary_rows = [["Key", "Value"]]
            for key, value in report.summary.items():
                summary_rows.append([str(key), self._fmt_num(value)])
            summary_table = Table(summary_rows, colWidths=[220, 120], repeatRows=1)
            summary_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ]
                )
            )
            story.append(summary_table)

        doc.build(story)
        return output_path


class PdfRenderer(PdfGenerator):
    """Backward-compatible renderer name used by assignment docs."""
