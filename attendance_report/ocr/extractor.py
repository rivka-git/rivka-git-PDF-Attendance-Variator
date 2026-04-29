"""PDF text extraction with OCR fallback."""

import logging
import shutil
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import ImageOps
from pypdf import PdfReader

from ..exceptions import OCRError

logger = logging.getLogger(__name__)

WIN_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
WIN_POPPLER = r"C:\poppler\Library\bin"


def _configure_binaries() -> tuple[str, str | None]:
    """Auto-detect system binary paths."""
    tesseract = WIN_TESSERACT if Path(WIN_TESSERACT).exists() else (shutil.which("tesseract") or "tesseract")
    poppler = WIN_POPPLER if Path(WIN_POPPLER).exists() else None
    return tesseract, poppler


TESSERACT_CMD, POPPLER_PATH = _configure_binaries()
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


class TextExtractor:
    """
    Hybrid PDF text extractor: direct extraction + OCR fallback.
    
    Attempts direct text extraction first, falls back to OCR if needed.
    Returns the result with higher quality score (based on content).
    """

    def _score_text(self, text: str) -> int:
        """Score text quality based on structured content indicators."""
        if not text:
            return 0
        hebrew_chars = sum(1 for ch in text if "\u0590" <= ch <= "\u05ff")
        time_tokens = text.count(":")
        date_tokens = text.count("/")
        return hebrew_chars + (time_tokens * 5) + (date_tokens * 3)

    def _extract_direct_text(self, pdf_path: Path) -> str:
        """Extract text directly from PDF structure (no OCR)."""
        try:
            reader = PdfReader(str(pdf_path))
            chunks = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(c for c in chunks if c.strip())
            logger.debug(f"Direct extraction: {len(chunks)} pages")
            return text
        except Exception as e:
            logger.debug(f"Direct extraction failed: {e}")
            return ""

    def _extract_with_ocr(self, pdf_path: Path) -> str:
        """Extract text using Tesseract OCR."""
        try:
            pages = convert_from_path(str(pdf_path), dpi=300, poppler_path=POPPLER_PATH)
            page_texts = []
            
            for i, page in enumerate(pages):
                processed = ImageOps.autocontrast(ImageOps.grayscale(page))
                text = pytesseract.image_to_string(
                    processed,
                    lang="heb+eng",
                    config="--oem 1 --psm 6 -c preserve_interword_spaces=1",
                )
                page_texts.append(text)
            
            logger.debug(f"OCR extraction: {len(page_texts)} pages")
            return "\n".join(page_texts)
        except Exception as e:
            raise OCRError(
                "OCR extraction failed",
                context={"pdf": str(pdf_path)},
                suggestion="Ensure Tesseract and Poppler are installed"
            ) from e

    def extract(self, pdf_path: Path) -> str:
        """
        Extract text from PDF using hybrid strategy.
        
        Returns the extraction method (direct or OCR) that produces higher quality.
        """
        logger.info(f"Extracting text from {pdf_path.name}")
        
        direct_text = self._extract_direct_text(pdf_path)
        ocr_text = self._extract_with_ocr(pdf_path)

        if self._score_text(direct_text) >= self._score_text(ocr_text):
            logger.info("Using direct extraction")
            return direct_text
        else:
            logger.info("Using OCR extraction")
            return ocr_text
