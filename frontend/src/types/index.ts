export interface Rule {
  document_id: string;
  title: string;
  agency: string;
  agency_id: string;
  comment_deadline: string;
  days_remaining: number;
  summary: string | null;
  regulations_gov_url: string;
  rin: string | null;
  posted_date: string;
}

export interface RuleDetail extends Rule {
  full_text: string | null;
  ria_text: string | null;
  attachments: Record<string, unknown>[];
}

export interface RuleSummaryData {
  plain_summary: string;
  what_is_changing: string;
  affected_populations: string[];
  key_dates: Record<string, string>;
  significance: string;
}

export interface RIAAssumptions {
  core_assumptions: string[];
  affected_party_estimates: string[];
  cost_benefit_claims: string[];
  data_sources_cited: string[];
  identified_gaps: string[];
}

export interface AnalysisResult {
  rule_summary: RuleSummaryData;
  ria_assumptions: RIAAssumptions;
}

export interface InterviewStartResponse {
  session_id: string;
  message: string;
}

export interface InterviewResponse {
  message: string;
  is_complete: boolean;
}

export interface CommentArgument {
  main_points: string[];
  ria_challenges: string[];
  suggested_alternatives: string[];
  strengthening_suggestions: string[];
  draft_structure: string;
}

export interface SubmitResult {
  success: boolean;
  message: string;
  regulations_gov_url: string;
}
