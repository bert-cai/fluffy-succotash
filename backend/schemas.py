from datetime import datetime
from typing import Optional, List, Dict

from pydantic import BaseModel


class RuleResponse(BaseModel):
    document_id: str
    title: str
    agency: str
    agency_id: str
    comment_deadline: datetime
    days_remaining: int
    summary: Optional[str]
    regulations_gov_url: str
    rin: Optional[str]
    posted_date: datetime


class RuleDetailResponse(RuleResponse):
    full_text: Optional[str]
    ria_text: Optional[str]
    attachments: List[dict]


class RuleSummaryResponse(BaseModel):
    plain_summary: str
    what_is_changing: str
    affected_populations: List[str]
    key_dates: Dict[str, str]
    significance: str


class RIAAssumptionsResponse(BaseModel):
    core_assumptions: List[str]
    affected_party_estimates: List[str]
    cost_benefit_claims: List[str]
    data_sources_cited: List[str]
    identified_gaps: List[str]


class AnalysisResponse(BaseModel):
    rule_summary: RuleSummaryResponse
    ria_assumptions: RIAAssumptionsResponse


class StartInterviewRequest(BaseModel):
    document_id: str


class StartInterviewResponse(BaseModel):
    session_id: str
    message: str


class RespondRequest(BaseModel):
    message: str


class RespondResponse(BaseModel):
    message: str
    is_complete: bool


class CommentArgumentResponse(BaseModel):
    main_points: List[str]
    ria_challenges: List[str]
    suggested_alternatives: List[str]
    strengthening_suggestions: List[str]
    draft_structure: str


class SubmitRequest(BaseModel):
    commenter_name: str
    commenter_email: Optional[str] = None


class SubmitResponse(BaseModel):
    success: bool
    message: str
    regulations_gov_url: str
