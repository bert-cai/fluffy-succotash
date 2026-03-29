from dataclasses import dataclass, field
from typing import Optional, List, Dict

from regulations_pipeline.models import Rule


@dataclass
class RuleSummary:
    plain_summary: str
    what_is_changing: str
    affected_populations: List[str]
    key_dates: Dict[str, str]
    significance: str  # "low" | "medium" | "high" with rationale


@dataclass
class RIAAssumptions:
    core_assumptions: List[str]
    affected_party_estimates: List[str]
    cost_benefit_claims: List[str]
    data_sources_cited: List[str]
    identified_gaps: List[str]


@dataclass
class InterviewTurn:
    role: str  # "assistant" or "user"
    content: str


@dataclass
class InterviewState:
    rule: Rule
    rule_summary: RuleSummary
    ria_assumptions: RIAAssumptions
    turns: List[InterviewTurn] = field(default_factory=list)
    user_situation: Optional[str] = None
    identified_gaps: List[str] = field(default_factory=list)
    is_complete: bool = False


@dataclass
class CommentArgument:
    main_points: List[str]
    ria_challenges: List[str]
    suggested_alternatives: List[str]
    strengthening_suggestions: List[str]
    draft_structure: str
