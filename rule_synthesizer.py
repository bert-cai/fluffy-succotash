import json
import logging
import os
from typing import Tuple

import anthropic

from regulations_pipeline.models import Rule
from synthesis_models import RuleSummary, RIAAssumptions

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"


def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def _log_usage(label: str, usage) -> None:
    logger.debug(
        "%s token usage: input=%d output=%d cache_creation=%d cache_read=%d",
        label,
        usage.input_tokens,
        usage.output_tokens,
        getattr(usage, "cache_creation_input_tokens", 0) or 0,
        getattr(usage, "cache_read_input_tokens", 0) or 0,
    )


def _parse_json(raw: str, label: str) -> dict:
    text = raw.strip()
    # Strip markdown fences if present despite instructions
    if text.startswith("```"):
        first_newline = text.index("\n")
        last_fence = text.rfind("```")
        text = text[first_newline + 1:last_fence].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error("%s returned invalid JSON: %s", label, raw[:500])
        raise ValueError(f"{label} returned invalid JSON: {e}\nRaw response: {raw[:300]}") from e


def summarize_rule(rule: Rule) -> Tuple[RuleSummary, dict]:
    """Summarize a rule in plain language. Returns (RuleSummary, usage_dict)."""
    client = _get_client()

    doc_text = rule.full_text or rule.ria_text or rule.summary or ""
    if not doc_text:
        logger.warning("No text available for rule %s", rule.document_id)

    schema = {
        "plain_summary": "2-3 sentence plain English explanation",
        "what_is_changing": "specifically what the rule modifies",
        "affected_populations": ["list of who this concretely affects"],
        "key_dates": {"comment_deadline": "...", "effective_date": "..."},
        "significance": "low|medium|high — one sentence rationale",
    }

    user_content = []
    user_content.append({
        "type": "text",
        "text": (
            f"Rule Title: {rule.title}\n"
            f"Agency: {rule.agency_id}\n"
            f"Summary: {rule.summary or 'Not provided'}\n"
            f"Comment Deadline: {rule.comment_deadline.date().isoformat()}\n\n"
            "Full rule text follows:"
        ),
    })
    user_content.append({
        "type": "text",
        "text": doc_text[:100000],  # cap at 100k chars
        "cache_control": {"type": "ephemeral"},
    })
    user_content.append({
        "type": "text",
        "text": (
            f"\n\nReturn ONLY valid JSON matching this exact schema, no preamble or markdown fences:\n"
            f"{json.dumps(schema, indent=2)}"
        ),
    })

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system="You are an expert in federal regulatory analysis. Your job is to explain "
               "proposed rules clearly to members of the public who are affected by them "
               "but have no legal or policy background. Be concrete and specific. Never "
               "use jargon without immediately explaining it.",
        messages=[{"role": "user", "content": user_content}],
    )

    _log_usage("summarize_rule", response.usage)
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "cache_creation_input_tokens": getattr(response.usage, "cache_creation_input_tokens", 0) or 0,
        "cache_read_input_tokens": getattr(response.usage, "cache_read_input_tokens", 0) or 0,
    }

    raw = response.content[0].text
    data = _parse_json(raw, "summarize_rule")

    return RuleSummary(
        plain_summary=data.get("plain_summary", ""),
        what_is_changing=data.get("what_is_changing", ""),
        affected_populations=data.get("affected_populations", []),
        key_dates=data.get("key_dates", {}),
        significance=data.get("significance", "medium"),
    ), usage


def extract_ria_assumptions(rule: Rule) -> Tuple[RIAAssumptions, dict]:
    """Extract RIA assumptions from a rule. Returns (RIAAssumptions, usage_dict)."""
    doc_text = rule.ria_text or rule.full_text or ""
    if not doc_text:
        logger.warning("No RIA or full text for rule %s — returning empty assumptions", rule.document_id)
        return RIAAssumptions(
            core_assumptions=[],
            affected_party_estimates=[],
            cost_benefit_claims=[],
            data_sources_cited=[],
            identified_gaps=[],
        ), {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}

    client = _get_client()

    schema = {
        "core_assumptions": ["factual/empirical claims the agency is making"],
        "affected_party_estimates": ["who and how many the agency says are affected"],
        "cost_benefit_claims": ["economic claims in the RIA"],
        "data_sources_cited": ["what evidence the agency relies on"],
        "identified_gaps": ["populations or scenarios the RIA seems to undercount or not address"],
    }

    user_content = []
    user_content.append({
        "type": "text",
        "text": (
            f"Rule Title: {rule.title}\n"
            f"Agency: {rule.agency_id}\n\n"
            "Document text (this may be the full rule text or the Regulatory Impact Analysis):"
        ),
    })
    user_content.append({
        "type": "text",
        "text": doc_text[:100000],
        "cache_control": {"type": "ephemeral"},
    })
    user_content.append({
        "type": "text",
        "text": (
            "\n\nAnalyze the above document. Identify all factual and empirical assumptions, "
            "especially those that might not hold for all affected parties. Pay close attention "
            "to populations, use cases, or scenarios the analysis may have undercounted or missed entirely.\n\n"
            "The identified_gaps field is the MOST IMPORTANT — think carefully about who might be "
            "affected but isn't represented in the agency's analysis, what cost categories might be "
            "missing, and what assumptions might not hold for small entities, rural communities, "
            "or non-traditional participants in the regulated activity.\n\n"
            f"Return ONLY valid JSON matching this exact schema, no preamble or markdown fences:\n"
            f"{json.dumps(schema, indent=2)}"
        ),
    })

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system="You are an expert in administrative law and regulatory impact analysis. "
               "Your job is to identify the factual and empirical assumptions an agency is "
               "making in its regulatory impact analysis — especially assumptions that might "
               "not hold for all affected parties, and populations or use cases the analysis "
               "may have undercounted or missed.",
        messages=[{"role": "user", "content": user_content}],
    )

    _log_usage("extract_ria_assumptions", response.usage)
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "cache_creation_input_tokens": getattr(response.usage, "cache_creation_input_tokens", 0) or 0,
        "cache_read_input_tokens": getattr(response.usage, "cache_read_input_tokens", 0) or 0,
    }

    raw = response.content[0].text
    data = _parse_json(raw, "extract_ria_assumptions")

    return RIAAssumptions(
        core_assumptions=data.get("core_assumptions", []),
        affected_party_estimates=data.get("affected_party_estimates", []),
        cost_benefit_claims=data.get("cost_benefit_claims", []),
        data_sources_cited=data.get("data_sources_cited", []),
        identified_gaps=data.get("identified_gaps", []),
    ), usage
