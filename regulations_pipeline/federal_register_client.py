import html
import logging
import re
from typing import Optional

import requests

from . import config

logger = logging.getLogger(__name__)


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class FederalRegisterClient:
    def __init__(self):
        self.base_url = config.FR_BASE_URL
        self.session = requests.Session()

    def fetch_rule_text(self, document_number: str) -> Optional[str]:
        url = f"{self.base_url}/documents/{document_number}.json"
        params = {
            "fields[]": ["abstract", "body_html_url", "raw_text_url", "full_text_xml_url"],
        }
        try:
            logger.debug("GET %s", url)
            resp = self.session.get(url, params=params, timeout=30)
            if resp.status_code != 200:
                logger.warning("Federal Register returned %d for %s", resp.status_code, document_number)
                return None
            data = resp.json()
        except Exception:
            logger.warning("Failed to fetch Federal Register doc %s", document_number, exc_info=True)
            return None

        # Try raw text URL first
        raw_text_url = data.get("raw_text_url")
        if raw_text_url:
            try:
                text_resp = self.session.get(raw_text_url, timeout=30)
                if text_resp.status_code == 200 and len(text_resp.text) > 100:
                    text = text_resp.text
                    # raw_text_url sometimes returns HTML despite the name
                    if "<html" in text.lower() or "<body" in text.lower():
                        text = _strip_html(text)
                    return text
            except Exception:
                logger.debug("Failed to fetch raw text for %s", document_number)

        # Try body HTML URL
        body_html_url = data.get("body_html_url")
        if body_html_url:
            try:
                html_resp = self.session.get(body_html_url, timeout=30)
                if html_resp.status_code == 200:
                    text = _strip_html(html_resp.text)
                    if len(text) > 100:
                        return text
            except Exception:
                logger.debug("Failed to fetch body HTML for %s", document_number)

        # Fall back to abstract
        abstract = data.get("abstract")
        if abstract:
            return abstract

        return None
