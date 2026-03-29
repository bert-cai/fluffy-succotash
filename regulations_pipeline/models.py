from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List


@dataclass
class RuleAttachment:
    attachment_id: str
    title: str
    url: str
    file_type: str
    is_ria: bool = False


@dataclass
class Rule:
    document_id: str
    docket_id: str
    title: str
    agency: str
    agency_id: str
    comment_deadline: datetime
    posted_date: datetime
    summary: Optional[str] = None
    full_text: Optional[str] = None
    ria_text: Optional[str] = None
    attachments: List[RuleAttachment] = field(default_factory=list)
    regulations_gov_url: str = ""
    rin: Optional[str] = None

    @property
    def days_remaining(self) -> int:
        delta = self.comment_deadline.date() - date.today()
        return max(delta.days, 0)

    def __repr__(self) -> str:
        return (
            f"Rule(document_id={self.document_id!r}, title={self.title!r}, "
            f"agency={self.agency_id!r}, days_remaining={self.days_remaining}, "
            f"comment_deadline={self.comment_deadline.date().isoformat()}, "
            f"attachments={len(self.attachments)}, "
            f"has_full_text={self.full_text is not None}, "
            f"has_ria_text={self.ria_text is not None})"
        )
