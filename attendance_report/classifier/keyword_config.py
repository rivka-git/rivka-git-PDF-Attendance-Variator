"""Configuration for keyword-based classification."""

KEYWORDS_TYPE_A = [
    "הנשר כח אדם",
]

KEYWORDS_TYPE_B = [
    "מחיר לשעה",
    "כרטיס עובד לחודש",
    "כרטים עובד לחודש",   # OCR variation of כרטיס
    "שעת יציאה",          # TYPE_B column header (TYPE_A uses just "יציאה")
    "יום בשבוע",          # TYPE_B column header (TYPE_A uses "מקום" instead)
    "בשבוע",              # Partial match for garbled OCR of יום בשבוע
    "ימי עבודה לחודש",
    "ימי עבודהלחודש",
    "סה\"כ ימי עבודה לחודש",
    "שעתסה\"כ",
    "שעתסהכ",
]
