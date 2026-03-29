import logging
import time
from datetime import datetime, date, timezone
from typing import Optional, List

import requests

from . import config

logger = logging.getLogger(__name__)


class APIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"API Error {status_code}: {message}")


class RateLimitError(APIError):
    def __init__(self, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        super().__init__(429, "Rate limit exceeded")


class NotFoundError(APIError):
    def __init__(self, resource: str):
        super().__init__(404, f"Not found: {resource}")


def _parse_datetime(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    # Python 3.9 fromisoformat doesn't handle trailing Z
    s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)


class RegulationsClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.REGULATIONS_GOV_API_KEY
        self.base_url = config.BASE_URL
        self.session = requests.Session()
        self.session.headers["X-Api-Key"] = self.api_key

    def _request(self, path: str, params: Optional[dict] = None) -> dict:
        url = f"{self.base_url}{path}"
        for attempt in range(config.MAX_RETRIES + 1):
            logger.debug("GET %s params=%s attempt=%d", url, params, attempt)
            resp = self.session.get(url, params=params, timeout=30)

            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 429:
                if attempt == config.MAX_RETRIES:
                    raise RateLimitError()
                wait = config.RATE_LIMIT_PAUSE_SECONDS * (2 ** attempt)
                logger.warning("Rate limited, waiting %ds", wait)
                time.sleep(wait)
                continue
            if resp.status_code == 404:
                raise NotFoundError(path)
            raise APIError(resp.status_code, resp.text[:200])

        raise RateLimitError()

    def fetch_open_comment_periods(
        self,
        days_remaining_max: int = 60,
        agency_ids: Optional[List[str]] = None,
        page_size: int = 25,
    ) -> List[dict]:
        today = date.today().isoformat()
        params = {
            "filter[documentType]": "Proposed Rule",
            "filter[commentEndDate][ge]": today,
            "sort": "commentEndDate",
            "page[size]": page_size,
            "page[number]": 1,
        }
        if agency_ids:
            params["filter[agencyId]"] = ",".join(agency_ids)

        all_docs: List[dict] = []
        while True:
            data = self._request("/documents", params=params)
            docs = data.get("data", [])
            all_docs.extend(docs)
            if len(docs) < page_size:
                break
            params["page[number]"] += 1

        return all_docs

    def fetch_rule_detail(self, document_id: str) -> dict:
        data = self._request(
            f"/documents/{document_id}",
            params={"include": "attachments"},
        )
        return data

    def fetch_docket_detail(self, docket_id: str) -> dict:
        data = self._request(f"/dockets/{docket_id}")
        return data
