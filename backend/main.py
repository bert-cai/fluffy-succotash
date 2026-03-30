import asyncio
import hashlib
import logging
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is on the path so top-level modules resolve
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from regulations_pipeline.pipeline import Pipeline
from regulations_pipeline.models import Rule
from rule_synthesizer import summarize_rule, extract_ria_assumptions
from comment_interviewer import start_interview, continue_interview, build_comment_argument
from synthesis_models import RuleSummary, RIAAssumptions

from backend.schemas import (
    RuleResponse, RuleDetailResponse, AnalysisResponse,
    RuleSummaryResponse, RIAAssumptionsResponse,
    StartInterviewRequest, StartInterviewResponse,
    RespondRequest, RespondResponse,
    CommentArgumentResponse,
    SubmitRequest, SubmitResponse,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Public Comment Tool API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"(http://localhost:3000|https://.*\.vercel\.app)",
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory caches ────────────────────────────────────────────────────
CACHE_TTL = 6 * 3600  # 6 hours

rules_cache: dict = {}          # { params_hash: { "rules": [...], "ts": float } }
rule_detail_cache: dict = {}    # { document_id: Rule }
analysis_cache: dict = {}       # { document_id: AnalysisResponse }
sessions: dict = {}             # { session_id: { "state": InterviewState, "argument": ... } }

# Thread-local pipeline to avoid SQLite cross-thread issues
_local = threading.local()


def _get_pipeline() -> Pipeline:
    if not hasattr(_local, "pipeline"):
        _local.pipeline = Pipeline()
    return _local.pipeline


# ── Middleware: request logging ──────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = (time.time() - start) * 1000
    logger.info("%s %s %.0fms", request.method, request.url.path, elapsed)
    return response


# ── Helpers ──────────────────────────────────────────────────────────────
def _cache_key(days_remaining_max: int, agency_ids: Optional[str]) -> str:
    raw = f"{days_remaining_max}:{agency_ids or ''}"
    return hashlib.md5(raw.encode()).hexdigest()


def _rule_to_response(rule: Rule) -> RuleResponse:
    return RuleResponse(
        document_id=rule.document_id,
        title=rule.title,
        agency=rule.agency,
        agency_id=rule.agency_id,
        comment_deadline=rule.comment_deadline,
        days_remaining=rule.days_remaining,
        summary=rule.summary,
        regulations_gov_url=rule.regulations_gov_url,
        rin=rule.rin,
        posted_date=rule.posted_date,
    )


def _rule_to_detail_response(rule: Rule) -> RuleDetailResponse:
    return RuleDetailResponse(
        document_id=rule.document_id,
        title=rule.title,
        agency=rule.agency,
        agency_id=rule.agency_id,
        comment_deadline=rule.comment_deadline,
        days_remaining=rule.days_remaining,
        summary=rule.summary,
        regulations_gov_url=rule.regulations_gov_url,
        rin=rule.rin,
        posted_date=rule.posted_date,
        full_text=rule.full_text,
        ria_text=rule.ria_text,
        attachments=[
            {
                "attachment_id": a.attachment_id,
                "title": a.title,
                "url": a.url,
                "file_type": a.file_type,
                "is_ria": a.is_ria,
            }
            for a in rule.attachments
        ],
    )


def _get_rules_cached(days_remaining_max: int = 60, agency_ids: Optional[str] = None) -> List[Rule]:
    key = _cache_key(days_remaining_max, agency_ids)
    cached = rules_cache.get(key)
    if cached and (time.time() - cached["ts"]) < CACHE_TTL:
        logger.debug("rules_cache hit for key=%s", key)
        return cached["rules"]

    parsed_agencies = [a.strip() for a in agency_ids.split(",")] if agency_ids else None
    pipeline = _get_pipeline()
    rules = pipeline.get_open_rules(
        days_remaining_max=days_remaining_max,
        agency_ids=parsed_agencies,
    )
    rules_cache[key] = {"rules": rules, "ts": time.time()}
    return rules


def _find_rule(document_id: str) -> Rule:
    if document_id in rule_detail_cache:
        return rule_detail_cache[document_id]
    rules = _get_rules_cached()
    for r in rules:
        if r.document_id == document_id:
            return r
    raise HTTPException(status_code=404, detail=f"Rule {document_id} not found")


def _get_enriched_rule(document_id: str) -> Rule:
    if document_id in rule_detail_cache:
        return rule_detail_cache[document_id]
    rule = _find_rule(document_id)
    pipeline = _get_pipeline()
    enriched = pipeline.enrich_rule(rule)
    rule_detail_cache[document_id] = enriched
    return enriched


def _analysis_from_cache(document_id: str):
    """Convert cached AnalysisResponse back to dataclasses."""
    analysis = analysis_cache[document_id]
    rule_summary = RuleSummary(
        plain_summary=analysis.rule_summary.plain_summary,
        what_is_changing=analysis.rule_summary.what_is_changing,
        affected_populations=analysis.rule_summary.affected_populations,
        key_dates=analysis.rule_summary.key_dates,
        significance=analysis.rule_summary.significance,
    )
    ria_assumptions = RIAAssumptions(
        core_assumptions=analysis.ria_assumptions.core_assumptions,
        affected_party_estimates=analysis.ria_assumptions.affected_party_estimates,
        cost_benefit_claims=analysis.ria_assumptions.cost_benefit_claims,
        data_sources_cited=analysis.ria_assumptions.data_sources_cited,
        identified_gaps=analysis.ria_assumptions.identified_gaps,
    )
    return rule_summary, ria_assumptions


def _build_analysis_response(summary, ria) -> AnalysisResponse:
    return AnalysisResponse(
        rule_summary=RuleSummaryResponse(
            plain_summary=summary.plain_summary,
            what_is_changing=summary.what_is_changing,
            affected_populations=summary.affected_populations,
            key_dates=summary.key_dates,
            significance=summary.significance,
        ),
        ria_assumptions=RIAAssumptionsResponse(
            core_assumptions=ria.core_assumptions,
            affected_party_estimates=ria.affected_party_estimates,
            cost_benefit_claims=ria.cost_benefit_claims,
            data_sources_cited=ria.data_sources_cited,
            identified_gaps=ria.identified_gaps,
        ),
    )


# ── Routes ───────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/rules", response_model=List[RuleResponse])
async def list_rules(days_remaining_max: int = 60, agency_ids: Optional[str] = None):
    try:
        rules = await asyncio.to_thread(_get_rules_cached, days_remaining_max, agency_ids)
        return [_rule_to_response(r) for r in rules]
    except Exception as e:
        logger.error("Failed to fetch rules: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rules/{document_id}", response_model=RuleDetailResponse)
async def get_rule_detail(document_id: str):
    try:
        # Return basic listing data immediately — no enrichment API calls.
        # Enrichment (full_text, ria_text) only happens in /analyze.
        rule = _find_rule(document_id)
        return _rule_to_detail_response(rule)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch rule detail: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rules/{document_id}/analyze", response_model=AnalysisResponse)
async def analyze_rule(document_id: str):
    if document_id in analysis_cache:
        logger.debug("analysis_cache hit for %s", document_id)
        return analysis_cache[document_id]

    try:
        enriched = await asyncio.to_thread(_get_enriched_rule, document_id)

        loop = asyncio.get_event_loop()
        summary_future = loop.run_in_executor(None, summarize_rule, enriched)
        ria_future = loop.run_in_executor(None, extract_ria_assumptions, enriched)
        (summary, _usage1), (ria, _usage2) = await asyncio.gather(summary_future, ria_future)

        result = _build_analysis_response(summary, ria)
        analysis_cache[document_id] = result
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to analyze rule: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/interview/start", response_model=StartInterviewResponse)
async def interview_start(req: StartInterviewRequest):
    try:
        enriched = await asyncio.to_thread(_get_enriched_rule, req.document_id)

        if req.document_id in analysis_cache:
            rule_summary, ria_assumptions = _analysis_from_cache(req.document_id)
        else:
            loop = asyncio.get_event_loop()
            summary_future = loop.run_in_executor(None, summarize_rule, enriched)
            ria_future = loop.run_in_executor(None, extract_ria_assumptions, enriched)
            (rule_summary, _), (ria_assumptions, _) = await asyncio.gather(summary_future, ria_future)
            analysis_cache[req.document_id] = _build_analysis_response(rule_summary, ria_assumptions)

        state = await asyncio.to_thread(start_interview, enriched, rule_summary, ria_assumptions)
        session_id = str(uuid.uuid4())
        sessions[session_id] = {"state": state, "argument": None}

        return StartInterviewResponse(
            session_id=session_id,
            message=state.turns[0].content,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start interview: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/interview/{session_id}/respond", response_model=RespondResponse)
async def interview_respond(session_id: str, req: RespondRequest):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    if session["state"].is_complete:
        raise HTTPException(status_code=400, detail="Interview already complete")

    try:
        state = await asyncio.to_thread(continue_interview, session["state"], req.message)
        session["state"] = state

        if state.is_complete:
            argument = await asyncio.to_thread(build_comment_argument, state)
            session["argument"] = argument

        return RespondResponse(
            message=state.turns[-1].content,
            is_complete=state.is_complete,
        )
    except Exception as e:
        logger.error("Failed in interview respond: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/interview/{session_id}/argument", response_model=CommentArgumentResponse)
async def get_argument(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    argument = sessions[session_id]["argument"]
    if argument is None:
        raise HTTPException(status_code=400, detail="Interview not yet complete")

    return CommentArgumentResponse(
        main_points=argument.main_points,
        ria_challenges=argument.ria_challenges,
        suggested_alternatives=argument.suggested_alternatives,
        strengthening_suggestions=argument.strengthening_suggestions,
        draft_structure=argument.draft_structure,
    )


@app.post("/interview/{session_id}/submit", response_model=SubmitResponse)
async def submit_comment(session_id: str, req: SubmitRequest):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = sessions[session_id]["state"]
    logger.info("Submission requested for session %s by %s", session_id, req.commenter_name)

    return SubmitResponse(
        success=True,
        message="Submission coming soon",
        regulations_gov_url=state.rule.regulations_gov_url,
    )


# ── Startup ─────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_prewarm():
    """Pre-warm rules cache in background — failures don't block the app."""
    async def _warm():
        try:
            rules = await asyncio.to_thread(_get_rules_cached)
            logger.info("Rules cache pre-warmed: %d rules loaded", len(rules))
        except Exception as e:
            logger.warning("Pre-warm failed (app still functional): %s", e)
    asyncio.create_task(_warm())
