import logging
import os
import re
import tempfile
from typing import Optional, List

import requests

from .models import RuleAttachment

logger = logging.getLogger(__name__)

MAX_PAGES = 200
RIA_KEYWORDS = re.compile(
    r"regulatory impact|economic analysis|\bria\b|cost.benefit|impact analysis",
    re.IGNORECASE,
)


def download_and_parse_pdf(url: str, attachment_id: str, api_key: Optional[str] = None) -> Optional[str]:
    tmp_path = None
    try:
        headers = {}
        if api_key and "api.regulations.gov" in url:
            headers["X-Api-Key"] = api_key

        logger.debug("Downloading PDF %s", url)
        resp = requests.get(url, headers=headers, timeout=60)
        resp.raise_for_status()

        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp.write(resp.content)
        tmp.close()
        tmp_path = tmp.name

        text = _extract_with_pymupdf(tmp_path)
        if text and len(text.strip()) >= 100:
            logger.info("Extracted %d chars from %s via pymupdf", len(text), attachment_id)
            return text

        text = _extract_with_pdfplumber(tmp_path)
        if text and len(text.strip()) >= 100:
            logger.info("Extracted %d chars from %s via pdfplumber", len(text), attachment_id)
            return text

        logger.warning("PDF extraction yielded insufficient text for %s", attachment_id)
        return None

    except Exception:
        logger.warning("Failed to download/parse PDF %s", attachment_id, exc_info=True)
        return None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _extract_with_pymupdf(path: str) -> Optional[str]:
    try:
        import fitz
        doc = fitz.open(path)
        pages = min(len(doc), MAX_PAGES)
        text = ""
        for i in range(pages):
            text += doc[i].get_text()
        doc.close()
        return text
    except Exception:
        logger.debug("pymupdf extraction failed", exc_info=True)
        return None


def _extract_with_pdfplumber(path: str) -> Optional[str]:
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            pages = pdf.pages[:MAX_PAGES]
            text = ""
            for page in pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text
    except Exception:
        logger.debug("pdfplumber extraction failed", exc_info=True)
        return None


def identify_ria_attachment(attachments: List[RuleAttachment]) -> Optional[RuleAttachment]:
    candidates = []
    for att in attachments:
        if att.file_type.lower() != "pdf":
            continue
        if RIA_KEYWORDS.search(att.title):
            candidates.append(att)

    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    # If multiple candidates, return the first one (no size info to sort by)
    return candidates[0]
