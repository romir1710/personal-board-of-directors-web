"""
pdf_utils.py — PDF text extraction using pypdf.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str | Path) -> str:
    """
    Extract all text from a PDF file using pypdf.

    Returns:
        Extracted text as a single string, with pages separated by newlines.

    Raises:
        ValueError: If the PDF has no extractable text (e.g. scanned image-only PDF).
        Exception:  Re-raises any pypdf parsing errors after logging them.
    """
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError as exc:
        raise ImportError("pypdf is not installed. Run: pip install pypdf") from exc

    try:
        reader = PdfReader(str(file_path))
        pages_text: list[str] = []

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages_text.append(text)
            else:
                logger.debug("Page %d had no extractable text.", page_num)

        full_text = "\n\n".join(pages_text).strip()

        if not full_text:
            raise ValueError(
                "No extractable text found in the PDF. "
                "It may be a scanned document or image-only PDF."
            )

        return full_text

    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to parse PDF at %s", file_path)
        raise
