import re
from datetime import date, time
from decimal import Decimal, InvalidOperation

from ..models import AttendanceRow
from .base_parser import BaseParser

_DATE_RE = re.compile(
    r"\b(?P<d>\d{1,2})\s*[/.\\-]\s*(?P<m>\d{1,2})(?:\s*[/.\\-]\s*(?P<y>\d{2,4}))?\b"
)
_DATE_COMPACT_RE = re.compile(r"\b(?P<d>\d{2})(?P<m>\d{2})(?P<y>\d{2,4})\b")
_TIME_RE = re.compile(r"\b(\d{1,2}[:.]\d{2})\b")
_COMPACT_TIME_RE = re.compile(r"\b(\d{3,4})\b")
_DAY_RE = re.compile(r"(ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת|ש|שמ|רבעי)")
_TOTAL_TOKEN_RE = re.compile(r"\b(\d{3}|\d{1,2}[.,]\d{1,2})\b")

_TOTAL_PAY_RE = re.compile(r'סה"כ לתשלום\s+([\d.,]+)', re.UNICODE)
_WORK_DAYS_RE = re.compile(r'ימי עבודה לחודש.*?(\d+)', re.UNICODE)
_HOURLY_RATE_RE = re.compile(r'מחיר לשעה[^\d]*(\d+\.?\d*)', re.UNICODE)


def _parse_date(s: str):
    normalized = s.translate(str.maketrans({
        "O": "0",
        "o": "0",
        "Q": "0",
        "I": "1",
        "l": "1",
        "|": "1",
        "!": "1",
    }))
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


def _parse_time(s: str):
    if not s:
        return None
    try:
        s = s.replace(".", ":")
        h, m = s.split(":")
        hour = int(h)
        minute = int(m)
        # OCR glitch: 41:01 or 4x:yy may represent 11:yy.
        if hour > 23 and s.startswith("4"):
            hour = 11
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return time(hour, minute)
        return None
    except Exception:
        return None


def _parse_compact_time(token: str):
    """Parse OCR compact times such as 803 -> 08:03 or 1109 -> 11:09."""
    if not token or not token.isdigit():
        return None
    if len(token) == 3:
        hour = int(token[0])
        minute = int(token[1:])
    elif len(token) == 4:
        hour = int(token[:2])
        minute = int(token[2:])
        # OCR glitch in samples: 11:xx can appear as 4xxx.
        if hour > 23 and token.startswith("4"):
            hour = 11
    else:
        return None
    if 0 <= hour <= 23 and 0 <= minute <= 59:
        return time(hour, minute)
    return None


def _extract_times(line: str):
    explicit_matches = list(_TIME_RE.finditer(line))
    compact_matches = list(_COMPACT_TIME_RE.finditer(line))

    candidates = []
    for m in explicit_matches:
        t = _parse_time(m.group(1))
        if t is not None:
            candidates.append((m.start(), t))

    for m in compact_matches:
        raw = m.group(1)
        t = _parse_compact_time(raw)
        if t is None:
            continue
        # Filter compact tokens that are likely totals rather than times.
        if t.hour < 6:
            continue
        candidates.append((m.start(), t))

    candidates.sort(key=lambda x: x[0])
    return [t for _, t in candidates]


def _infer_exit_from_total(entry_t: time, total_h: Decimal):
    if entry_t is None or total_h is None:
        return None
    if total_h < Decimal("0") or total_h > Decimal("16"):
        return None
    total_minutes = int((total_h * Decimal("60")).quantize(Decimal("1")))
    entry_minutes = entry_t.hour * 60 + entry_t.minute
    exit_minutes = entry_minutes + total_minutes
    exit_hour = (exit_minutes // 60) % 24
    exit_min = exit_minutes % 60
    return time(exit_hour, exit_min)


def _parse_decimal(s: str):
    if not s:
        return None
    try:
        return Decimal(s.replace(",", "."))
    except InvalidOperation:
        return None


def _normalize_total(token: str):
    if not token:
        return None
    token = token.replace(",", ".")
    if "." in token:
        val = _parse_decimal(token)
        if val is not None and Decimal("0") <= val <= Decimal("24"):
            return val
        return None
    if token.isdigit() and len(token) == 3:
        # OCR often returns 350 instead of 3.50.
        val = Decimal(int(token)) / Decimal("100")
        if Decimal("0") <= val <= Decimal("24"):
            return val
    return None


class TypeBParser(BaseParser):
    """Parser for TYPE_B reports (כרטיס עובד לחודש)."""

    def _parse_metadata(self, text: str) -> dict:
        month_label = ""
        for line in text.splitlines():
            if "כרטיס" in line or "כרטים" in line:
                month_label = line.strip()
                break
        return {"company_name": "", "employee_name": "", "month_label": month_label}

    def _is_header_line(self, line: str) -> bool:
        tokens = ("תאריך", "יום", "כניסה", "יציאה", "סה\"כ", "כרטיס עובד")
        return any(tok in line for tok in tokens)

    def _parse_row(self, line: str):
        parsed_date = _parse_date(line)
        if parsed_date is None:
            return None

        day_match = _DAY_RE.search(line)
        day_name = day_match.group(1) if day_match else None
        if day_name == "שמ":
            day_name = "שני"
        elif day_name == "רבעי":
            day_name = "רביעי"
        elif day_name == "ש":
            day_name = "שישי"

        times = _extract_times(line)
        totals = [_normalize_total(t) for t in _TOTAL_TOKEN_RE.findall(line)]
        totals = [t for t in totals if t is not None]

        return AttendanceRow(
            work_date=parsed_date,
            day_name=day_name,
            entry_time=times[0] if len(times) >= 1 else None,
            exit_time=times[1] if len(times) >= 2 else None,
            total_hours=totals[-1] if totals else None,
        )

    def _parse_rows(self, text: str) -> tuple:
        rows = []
        seen_dates = set()

        def latest_incomplete_index():
            for idx in range(len(rows) - 1, -1, -1):
                row = rows[idx]
                if row.entry_time is None or row.exit_time is None or row.total_hours is None:
                    return idx
            return len(rows) - 1

        for line in text.splitlines():
            if self._is_header_line(line):
                continue

            row = self._parse_row(line)
            if row is None:
                # Enrich last row if this line looks like continuation of values.
                if not rows:
                    continue
                times = _extract_times(line)
                totals = [_normalize_total(t) for t in _TOTAL_TOKEN_RE.findall(line)]
                totals = [t for t in totals if t is not None]
                if not times and not totals:
                    continue

                idx = latest_incomplete_index()
                last = rows[idx]
                entry = last.entry_time
                exit_t = last.exit_time
                total = last.total_hours
                if times:
                    if entry is None and times:
                        entry = times[0]
                    if exit_t is None and len(times) >= 2:
                        exit_t = times[1]
                if total is None and totals:
                    total = totals[-1]
                rows[idx] = AttendanceRow(
                    work_date=last.work_date,
                    day_name=last.day_name,
                    entry_time=entry,
                    exit_time=exit_t,
                    total_hours=total,
                )
                continue

            raw_date = row.work_date.isoformat()
            if raw_date in seen_dates:
                continue
            seen_dates.add(raw_date)
            rows.append(row)

        # Final pass: if exit is missing but entry+total exist, infer exit deterministically.
        for i, row in enumerate(rows):
            if row.exit_time is None and row.entry_time is not None and row.total_hours is not None:
                inferred_exit = _infer_exit_from_total(row.entry_time, row.total_hours)
                if inferred_exit is not None:
                    rows[i] = AttendanceRow(
                        work_date=row.work_date,
                        day_name=row.day_name,
                        entry_time=row.entry_time,
                        exit_time=inferred_exit,
                        total_hours=row.total_hours,
                    )
        return tuple(rows)

    def _parse_summary(self, text: str) -> dict:
        summary = {}
        m = _TOTAL_PAY_RE.search(text)
        if m:
            summary["סהכ לתשלום"] = _parse_decimal(m.group(1))
        m = _WORK_DAYS_RE.search(text)
        if m:
            summary["ימי עבודה"] = int(m.group(1))
        m = _HOURLY_RATE_RE.search(text)
        if m:
            summary["מחיר לשעה"] = _parse_decimal(m.group(1))
        return summary
