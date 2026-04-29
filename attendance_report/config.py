from decimal import Decimal


QUALITY_GATE_THRESHOLDS = {
    "TYPE_A": {
        "non_strict": {"entry": 0.95, "exit": 0.95, "total_hours": 0.95},
        "strict": {"date": 0.80, "entry": 0.95, "exit": 0.95, "total_hours": 0.95},
    },
    "TYPE_B": {
        "non_strict": {"date": 0.85, "entry": 0.85, "exit": 0.80, "total_hours": 0.85},
        "strict": {"date": 0.90, "entry": 0.90, "exit": 0.90, "total_hours": 0.90},
    },
    "TYPE_C": {
        "non_strict": {"date": 0.85, "entry": 0.85, "exit": 0.80, "total_hours": 0.85},
        "strict": {"date": 0.90, "entry": 0.90, "exit": 0.90, "total_hours": 0.90},
    },
}


TRANSFORMATION_SPAN_MINUTES = {
    "TYPE_A": 8,
    "TYPE_B": 6,
    "TYPE_C": 6,
}


MIN_WORKING_HOURS = Decimal("0.5")
MAX_WORKING_HOURS = Decimal("12")
MAX_TOTAL_MISMATCH_HOURS = Decimal("0.30")
MIN_BREAK_MINUTES = 0
MAX_BREAK_MINUTES = 120
