import json
import logging
import os
import re
from typing import List

import anthropic

from regulations_pipeline.models import Rule
from synthesis_models import (
    RuleSummary, RIAAssumptions, InterviewTurn, InterviewState, CommentArgument,
)

logger = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5-20251001"

INTERVIEW_SYSTEM_PROMPT = """\
You are helping a member of the public write a substantive comment on a \
federal proposed rulemaking. Your goal is to help them articulate how this \
rule affects their specific situation in a way that the agency is legally \
required to engage with.

A substantive comment must do one or more of the following:
- Identify a factual assumption in the agency's analysis that doesn't hold \
for the commenter's situation, with a concrete reason
- Point to a population or use case the agency's analysis undercounts or ignores
- Provide data or evidence that challenges the agency's stated rationale
- Propose a specific regulatory alternative that achieves the rule's goals \
with less burden or harm

Generic assertions ("this rule is bad for small businesses") are not \
substantive and agencies are not required to respond to them. Help the user \
move from assertions to evidence-backed arguments.

Interview the user to extract:
1. Who they are and their relationship to the regulated activity
2. Specifically how this rule would affect their operations, costs, or situation
3. Any data they have (numbers, timelines, examples) that quantify the impact
4. Whether their situation represents a gap in the agency's analysis

Ask one focused question at a time. After 3-4 exchanges you should have enough \
to build an argument. Keep your questions concise and specific."""

ARGUMENT_SYSTEM_PROMPT = """\
You are an expert in administrative law. Given this interview with an affected \
party, identify the strongest substantive arguments for a public comment. Focus \
on arguments that challenge specific factual or empirical claims in the agency's \
regulatory impact analysis, not just policy disagreements."""


def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def _parse_json(raw: str, label: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        first_newline = text.index("\n")
        last_fence = text.rfind("```")
        text = text[first_newline + 1:last_fence].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error("%s returned invalid JSON: %s", label, raw[:500])
        raise ValueError(f"{label} returned invalid JSON: {e}\nRaw response: {raw[:300]}") from e


def _build_rule_context(rule: Rule, rule_summary: RuleSummary, ria_assumptions: RIAAssumptions) -> str:
    gaps = "\n".join(f"  - {g}" for g in ria_assumptions.identified_gaps) if ria_assumptions.identified_gaps else "  None identified"
    assumptions = "\n".join(f"  - {a}" for a in ria_assumptions.core_assumptions) if ria_assumptions.core_assumptions else "  None identified"

    return (
        f"RULE: {rule.title}\n"
        f"AGENCY: {rule.agency_id}\n"
        f"COMMENT DEADLINE: {rule.comment_deadline.date().isoformat()}\n\n"
        f"PLAIN SUMMARY: {rule_summary.plain_summary}\n\n"
        f"WHAT IS CHANGING: {rule_summary.what_is_changing}\n\n"
        f"KEY AGENCY ASSUMPTIONS:\n{assumptions}\n\n"
        f"IDENTIFIED GAPS IN AGENCY ANALYSIS:\n{gaps}"
    )


def _build_system_with_context(rule: Rule, rule_summary: RuleSummary, ria_assumptions: RIAAssumptions) -> list:
    """Build system message with cached rule text block."""
    doc_text = rule.ria_text or rule.full_text or ""
    parts = [
        {"type": "text", "text": INTERVIEW_SYSTEM_PROMPT},
        {"type": "text", "text": f"\n\nRULE CONTEXT:\n{_build_rule_context(rule, rule_summary, ria_assumptions)}\n\nFULL DOCUMENT TEXT:"},
    ]
    if doc_text:
        parts.append({
            "type": "text",
            "text": doc_text[:80000],
            "cache_control": {"type": "ephemeral"},
        })
    return parts


def _turns_to_messages(turns: List[InterviewTurn]) -> list:
    return [{"role": t.role, "content": t.content} for t in turns]


def _assess_completeness(state: InterviewState) -> bool:
    if len(state.turns) < 6:  # need at least 3 exchanges
        return False
    user_turns = [t for t in state.turns if t.role == "user"]
    all_user_text = " ".join(t.content for t in user_turns)
    # Check for concrete details: numbers, dollar amounts, percentages, time periods
    has_numbers = bool(re.search(r'\d+', all_user_text))
    has_specifics = bool(re.search(
        r'(\$[\d,]+|\d+\s*(employees?|workers?|months?|days?|years?|percent|%|units?|products?|SKUs?))',
        all_user_text, re.IGNORECASE
    ))
    return has_numbers and has_specifics


def start_interview(rule: Rule, rule_summary: RuleSummary, ria_assumptions: RIAAssumptions) -> InterviewState:
    client = _get_client()

    state = InterviewState(
        rule=rule,
        rule_summary=rule_summary,
        ria_assumptions=ria_assumptions,
    )

    system = _build_system_with_context(rule, rule_summary, ria_assumptions)

    opening_prompt = (
        f"The agency ({rule.agency_id}) has proposed a rule: \"{rule.title}\"\n\n"
        f"{rule_summary.what_is_changing}\n\n"
        f"The comment deadline is {rule.comment_deadline.date().isoformat()} "
        f"({rule.days_remaining} days remaining).\n\n"
        "Please introduce yourself to the commenter, briefly explain what this rule would change, "
        "and ask them to describe their relationship to the regulated activity. "
        "Keep it to 3-4 sentences."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": opening_prompt}],
    )

    assistant_text = response.content[0].text
    state.turns.append(InterviewTurn(role="assistant", content=assistant_text))
    return state


def continue_interview(state: InterviewState, user_message: str) -> InterviewState:
    client = _get_client()

    state.turns.append(InterviewTurn(role="user", content=user_message))

    # Capture user_situation from first user response
    if state.user_situation is None:
        state.user_situation = user_message

    system = _build_system_with_context(state.rule, state.rule_summary, state.ria_assumptions)
    messages = _turns_to_messages(state.turns)

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system,
        messages=messages,
    )

    assistant_text = response.content[0].text
    state.turns.append(InterviewTurn(role="assistant", content=assistant_text))

    state.is_complete = _assess_completeness(state)
    return state


def build_comment_argument(state: InterviewState) -> CommentArgument:
    client = _get_client()

    rule_context = _build_rule_context(state.rule, state.rule_summary, state.ria_assumptions)
    interview_transcript = "\n\n".join(
        f"{'INTERVIEWER' if t.role == 'assistant' else 'COMMENTER'}: {t.content}"
        for t in state.turns
    )

    schema = {
        "main_points": ["2-4 concrete arguments the comment should make"],
        "ria_challenges": ["specific RIA assumptions the user's situation contradicts"],
        "suggested_alternatives": ["regulatory alternatives the user could propose"],
        "strengthening_suggestions": ["data or citations that would improve the comment"],
        "draft_structure": "prose outline of the comment structure",
    }

    user_content = []
    user_content.append({
        "type": "text",
        "text": f"RULE CONTEXT:\n{rule_context}\n\nINTERVIEW TRANSCRIPT:\n{interview_transcript}",
    })
    doc_text = state.rule.ria_text or state.rule.full_text or ""
    if doc_text:
        user_content.append({
            "type": "text",
            "text": f"\n\nFULL DOCUMENT TEXT:\n{doc_text[:80000]}",
            "cache_control": {"type": "ephemeral"},
        })
    user_content.append({
        "type": "text",
        "text": (
            "\n\nBased on the interview above, identify the strongest substantive arguments "
            "this commenter can make. Focus especially on where their specific situation "
            "contradicts the agency's assumptions or reveals gaps in the analysis.\n\n"
            f"Return ONLY valid JSON matching this schema, no preamble or markdown fences:\n"
            f"{json.dumps(schema, indent=2)}"
        ),
    })

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=ARGUMENT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    raw = response.content[0].text
    data = _parse_json(raw, "build_comment_argument")

    return CommentArgument(
        main_points=data.get("main_points", []),
        ria_challenges=data.get("ria_challenges", []),
        suggested_alternatives=data.get("suggested_alternatives", []),
        strengthening_suggestions=data.get("strengthening_suggestions", []),
        draft_structure=data.get("draft_structure", ""),
    )
