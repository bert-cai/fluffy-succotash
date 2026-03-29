import type {
  Rule,
  RuleDetail,
  AnalysisResult,
  InterviewStartResponse,
  InterviewResponse,
  CommentArgument,
  SubmitResult,
} from "@/types";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    public override message: string,
  ) {
    super(message);
  }
}

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new ApiError(res.status, body);
  }
  return res.json() as Promise<T>;
}

export function getRules(agencyIds?: string[]): Promise<Rule[]> {
  const params = new URLSearchParams();
  if (agencyIds?.length) {
    params.set("agency_ids", agencyIds.join(","));
  }
  const qs = params.toString();
  return request<Rule[]>(`/rules${qs ? `?${qs}` : ""}`);
}

export function getRule(documentId: string): Promise<RuleDetail> {
  return request<RuleDetail>(`/rules/${encodeURIComponent(documentId)}`);
}

export function analyzeRule(documentId: string): Promise<AnalysisResult> {
  return request<AnalysisResult>(
    `/rules/${encodeURIComponent(documentId)}/analyze`,
    { method: "POST" },
  );
}

export function startInterview(
  documentId: string,
): Promise<InterviewStartResponse> {
  return request<InterviewStartResponse>("/interview/start", {
    method: "POST",
    body: JSON.stringify({ document_id: documentId }),
  });
}

export function respondToInterview(
  sessionId: string,
  message: string,
): Promise<InterviewResponse> {
  return request<InterviewResponse>(
    `/interview/${encodeURIComponent(sessionId)}/respond`,
    {
      method: "POST",
      body: JSON.stringify({ message }),
    },
  );
}

export function getArgument(sessionId: string): Promise<CommentArgument> {
  return request<CommentArgument>(
    `/interview/${encodeURIComponent(sessionId)}/argument`,
  );
}

export function submitComment(
  sessionId: string,
  name: string,
  email?: string,
): Promise<SubmitResult> {
  return request<SubmitResult>(
    `/interview/${encodeURIComponent(sessionId)}/submit`,
    {
      method: "POST",
      body: JSON.stringify({ commenter_name: name, commenter_email: email }),
    },
  );
}
