import re
from datetime import date, time
from decimal import Decimal, InvalidOperation
from typing import Any

from ..models import AttendanceRow
from .base_parser import BaseParser

_DATE_RE = re.compile(
    r"\b(?P<d>\d{1,2})\s*[/.\\-]\s*(?P<m>\d{1,2})(?:\s*[/.\\-]\s*(?P<y>\d{2,4}))?\b"
)
_DATE_COMPACT_RE = re.compile(r"\b(?P<d>\d{2})(?P<m>\d{2})(?P<y>\d{2,4})\b")
_TIME_RE = re.compile(r"\b(\d{1,2}:\d{2})\b")
_DAY_RE = re.compile(r"(ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)")
_TOTAL_TOKEN_RE = re.compile(r"\b(\d{1,4}(?:[.,]\d{1,2})?)\b")

_SUMMARY_HOURS_RE = re.compile(r"(?P<label>סה\"כ שעות|שעות \d+%|שבת)\s+(?P<val>[\d.]+)", re.UNICODE)


def _parse_time(s: str) -> time | None:
    try:
        h, m = s.split(":")
        return time(int(h), int(m))
    except Exception:
        return None


def _parse_decimal(s: str) -> Decimal | None:
    try:
        return Decimal(s.replace(",", "."))
    except InvalidOperation:
        return None


def _parse_date(s: str) -> date | None:
    normalized = s.translate(str.maketrans({
        "O": "0",
        "o": "0",
        "Q": "0",
        "I": "1",
        "l": "1",
        "|": "1",
        "!": "1",
    }))

    # Normalize common OCR separator glitches so date tokens are discoverable.
    normalized = normalized.replace("\\", "/").replace("_", "-")

    for match in _DATE_RE.finditer(normalized):
        try:
            d = int(match.group("d"))
            m = int(match.group("m"))
            y_str = match.group("y")
            y = int(y_str) if y_str else date.today().year
            if y < 100:
                y += 2000
            return date(y, m, d)
        except Exception:
            continue

    for match in _DATE_COMPACT_RE.finditer(normalized):
        try:
            d = int(match.group("d"))
            m = int(match.group("m"))
            y = int(match.group("y"))
            if y < 100:
                y += 2000
            return date(y, m, d)
        except Exception:
            continue

    return None


def _normalize_hour_token(token: str) -> Decimal | None:
    tok = token.replace(",", ".")
    if "." in tok:
        return _parse_decimal(tok)
    if tok.isdigit():
        val = int(tok)
        # OCR often converts 6.50 -> 650.
        if 100 <= val <= 2400:
            return Decimal(val) / Decimal("100")
        if 0 <= val <= 24:
            return Decimal(val)
    return None


class TypeAParser(BaseParser):
    """Parser for TYPE_A reports (הנשר כח אדם)."""

    def _parse_metadata(self, text: str) -> dict[str, str]:
        company = ""
        for line in text.splitlines():
            if "הנשר" in line:
                company = line.strip()
                break
        return {"company_name": company, "employee_name": "", "month_label": ""}

    def _is_header_line(self, line: str) -> bool:
        tokens = ("תאריך", "יום", "כניסה", "יציאה", "סה\"כ")
        return any(tok in line for tok in tokens)

    def _parse_row(self, line: str) -> AttendanceRow | None:
        times = _TIME_RE.findall(line)
        if len(times) < 3:
            return None

        day_match = _DAY_RE.search(line)
        day_name = day_match.group(1) if day_match else None

        numeric_tokens = _TOTAL_TOKEN_RE.findall(line)
        total_val = None
        # Try candidates after the 3rd time token, fallback to last numeric token.
        for tok in reversed(numeric_tokens):
            cand = _normalize_hour_token(tok)
            if cand is not None and Decimal("0") <= cand <= Decimal("24"):
                total_val = cand
                break

        return AttendanceRow(
            work_date=_parse_date(line),
            day_name=day_name,
            location=None,
            entry_time=_parse_time(times[0]),
            exit_time=_parse_time(times[1]),
            break_minutes=None,
            total_hours=total_val,
        )

    def _parse_summary(self, text: str) -> dict[str, Any]:
        summary: dict[str, Any] = {}
        for m in _SUMMARY_HOURS_RE.finditer(text):
            summary[m.group("label")] = _parse_decimal(m.group("val"))
        return summary
