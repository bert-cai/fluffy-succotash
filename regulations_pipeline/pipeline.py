import logging
from datetime import datetime
from typing import Optional, List

from .cache import Cache
from .config import REGULATIONS_GOV_API_KEY, DB_PATH
from .federal_register_client import FederalRegisterClient
from .models import Rule, RuleAttachment
from .pdf_parser import download_and_parse_pdf, identify_ria_attachment
from .regulations_client import RegulationsClient, _parse_datetime

logger = logging.getLogger(__name__)


def _parse_attachments(detail: dict) -> List[RuleAttachment]:
    included = detail.get("included", [])
    attachments = []
    for item in included:
        if item.get("type") != "attachments":
            continue
        attrs = item.get("attributes", {})
        file_formats = attrs.get("fileFormats", [])
        if not file_formats:
            continue
        # Take the first available file format (usually PDF)
        fmt = file_formats[0]
        attachments.append(RuleAttachment(
            attachment_id=item.get("id", ""),
            title=attrs.get("title", ""),
            url=fmt.get("fileUrl", ""),
            file_type=fmt.get("format", "unknown"),
        ))
    return attachments


def _build_rule(doc: dict, docket_data: Optional[dict] = None) -> Rule:
    attrs = doc.get("attributes", {})
    doc_id = doc.get("id", attrs.get("documentId", ""))
    docket_id = attrs.get("docketId", "")

    comment_end = _parse_datetime(attrs.get("commentEndDate"))
    posted = _parse_datetime(attrs.get("postedDate"))

    rin = None
    if docket_data:
        docket_attrs = docket_data.get("data", {}).get("attributes", {})
        rin = docket_attrs.get("rin")

    return Rule(
        document_id=doc_id,
        docket_id=docket_id,
        title=attrs.get("title", ""),
        agency=attrs.get("agencyId", ""),
        agency_id=attrs.get("agencyId", ""),
        summary=attrs.get("summary"),
        comment_deadline=comment_end or datetime.min,
        posted_date=posted or datetime.min,
        regulations_gov_url=f"https://www.regulations.gov/document/{doc_id}",
        rin=rin,
    )


class Pipeline:
    def __init__(self, api_key: Optional[str] = None, db_path: Optional[str] = None):
        self.api_key = api_key or REGULATIONS_GOV_API_KEY
        self.reg_client = RegulationsClient(self.api_key)
        self.fr_client = FederalRegisterClient()
        self.cache = Cache(db_path or DB_PATH)

    def get_open_rules(
        self,
        days_remaining_max: int = 60,
        agency_ids: Optional[List[str]] = None,
        force_refresh: bool = False,
    ) -> List[Rule]:
        docs = self.reg_client.fetch_open_comment_periods(
            days_remaining_max=days_remaining_max,
            agency_ids=agency_ids,
        )

        rules = []
        for doc in docs:
            doc_id = doc.get("id", "")
            if not doc_id:
                continue

            # Check cache for detail
            cached = None if force_refresh else self.cache.get_cached_rule(doc_id)
            if cached:
                detail = cached
            else:
                try:
                    detail = self.reg_client.fetch_rule_detail(doc_id)
                    self.cache.cache_rule(doc_id, detail)
                except Exception:
                    logger.warning("Failed to fetch detail for %s, using listing data", doc_id)
                    detail = {"data": doc}

            # Try to get docket info for RIN
            docket_id = doc.get("attributes", {}).get("docketId", "")
            docket_data = None
            if docket_id:
                try:
                    docket_data = self.reg_client.fetch_docket_detail(docket_id)
                except Exception:
                    logger.debug("Failed to fetch docket %s", docket_id)

            rule_doc = detail.get("data", doc)
            rule = _build_rule(rule_doc, docket_data)
            rule.attachments = _parse_attachments(detail)

            # Mark RIA attachments
            ria = identify_ria_attachment(rule.attachments)
            if ria:
                ria.is_ria = True

            rules.append(rule)

        rules.sort(key=lambda r: r.days_remaining)
        return rules

    def enrich_rule(self, rule: Rule) -> Rule:
        # Check text cache first
        cached_full, cached_ria = self.cache.get_cached_texts(rule.document_id)
        if cached_full or cached_ria:
            rule.full_text = cached_full
            rule.ria_text = cached_ria
            return rule

        # If we don't have attachments yet, fetch detail
        if not rule.attachments:
            try:
                detail = self.reg_client.fetch_rule_detail(rule.document_id)
                rule.attachments = _parse_attachments(detail)
                ria = identify_ria_attachment(rule.attachments)
                if ria:
                    ria.is_ria = True
            except Exception:
                logger.warning("Failed to fetch attachments for %s", rule.document_id)

        # Try to get RIA text from PDF
        ria_attachment = identify_ria_attachment(rule.attachments)
        if ria_attachment and ria_attachment.url:
            try:
                rule.ria_text = download_and_parse_pdf(
                    ria_attachment.url,
                    ria_attachment.attachment_id,
                    api_key=self.api_key,
                )
            except Exception:
                logger.warning("Failed to parse RIA PDF for %s", rule.document_id)

        # Try to get full text from Federal Register
        fr_doc_num = None
        try:
            detail = self.cache.get_cached_rule(rule.document_id)
            if detail:
                fr_doc_num = detail.get("data", {}).get("attributes", {}).get("frDocNum")
        except Exception:
            pass

        if fr_doc_num:
            try:
                rule.full_text = self.fr_client.fetch_rule_text(fr_doc_num)
            except Exception:
                logger.warning("Failed to fetch FR text for %s", fr_doc_num)

        # Cache whatever we got
        if rule.full_text or rule.ria_text:
            self.cache.cache_texts(rule.document_id, rule.full_text, rule.ria_text)

        return rule
