import re
import logging

from .keyword_config import KEYWORDS_TYPE_A, KEYWORDS_TYPE_B, KEYWORDS_TYPE_C


logger = logging.getLogger(__name__)


class Classifier:
    """Classifies report type based on keyword scoring."""

    def _normalize(self, text: str) -> str:
        normalized = text.replace("׳", "").replace("\"", "")
        normalized = normalized.replace("'", "").replace("`", "")
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized

    def classify(self, raw_text: str) -> str:
        """
        Analyze raw text and return "TYPE_A", "TYPE_B", "TYPE_C", or "UNKNOWN".
        """
        text = self._normalize(raw_text)

        score_a = sum(1 for kw in KEYWORDS_TYPE_A if kw in text)
        score_b = sum(1 for kw in KEYWORDS_TYPE_B if kw in text)
        score_c = sum(1 for kw in KEYWORDS_TYPE_C if kw in text)

        # Structural fallback for noisy OCR TYPE_B files.
        dates = len(re.findall(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", text))
        times = len(re.findall(r"\b\d{1,2}[:.]\d{2}\b", text))
        if score_b == 0 and dates >= 4 and times >= 6 and ("לחודש" in text or "עבודה" in text):
            score_b = 1

        # Structural fallback for TYPE_A files.
        if score_a == 0 and ("הפסקה" in text and "כניסה" in text and "150%" in text):
            score_a = 1

        scores = {
            "TYPE_A": score_a,
            "TYPE_B": score_b,
            "TYPE_C": score_c,
        }
        positives = [report_type for report_type, score in scores.items() if score > 0]
        if len(positives) == 1:
            logger.debug("Classifier selected %s with scores=%s", positives[0], scores)
            return positives[0]
        logger.debug("Classifier returned UNKNOWN with scores=%s", scores)
        return "UNKNOWN"
