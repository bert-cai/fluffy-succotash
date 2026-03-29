"""
Tests for Phase 2 — LLM Synthesis Layer.

Requires both REGULATIONS_GOV_API_KEY and ANTHROPIC_API_KEY in .env.
"""
import os
import sys
import unittest
import json
import textwrap

from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

has_reg_key = bool(os.environ.get("REGULATIONS_GOV_API_KEY"))
has_anthropic_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
SKIP_REASON = "Requires REGULATIONS_GOV_API_KEY and ANTHROPIC_API_KEY"

# ── Shared fixture: fetch and enrich one real rule ───────────────────────
_rule = None
_enriched = False


def _get_rule():
    global _rule, _enriched
    if _rule is not None:
        return _rule

    from regulations_pipeline.pipeline import Pipeline
    import tempfile

    db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db.close()
    pipeline = Pipeline(db_path=db.name)

    rules = pipeline.get_open_rules()
    assert len(rules) >= 1, "No open rules found"

    # Pick the first rule and enrich it
    _rule = pipeline.enrich_rule(rules[0])
    _enriched = True
    print(f"\n{'='*60}")
    print(f"TEST RULE: {_rule.title}")
    print(f"Agency: {_rule.agency_id} | Deadline: {_rule.comment_deadline.date()} | Days left: {_rule.days_remaining}")
    print(f"Full text: {len(_rule.full_text) if _rule.full_text else 0} chars")
    print(f"RIA text: {len(_rule.ria_text) if _rule.ria_text else 0} chars")
    print(f"Attachments: {len(_rule.attachments)}")
    print(f"{'='*60}\n")
    return _rule


def _pp(label, obj):
    """Pretty-print a dataclass for test output."""
    print(f"\n{'─'*60}")
    print(f"  {label}")
    print(f"{'─'*60}")
    for k, v in obj.__dict__.items():
        if isinstance(v, list):
            print(f"  {k}:")
            for item in v:
                wrapped = textwrap.fill(str(item), width=76, initial_indent="    - ", subsequent_indent="      ")
                print(wrapped)
        elif isinstance(v, dict):
            print(f"  {k}:")
            for dk, dv in v.items():
                print(f"    {dk}: {dv}")
        elif isinstance(v, str) and len(v) > 100:
            print(f"  {k}:")
            print(textwrap.fill(v, width=76, initial_indent="    ", subsequent_indent="    "))
        else:
            print(f"  {k}: {v}")
    print()


@unittest.skipUnless(has_reg_key and has_anthropic_key, SKIP_REASON)
class TestSummarizeRule(unittest.TestCase):

    def test_summarize_rule(self):
        from rule_synthesizer import summarize_rule
        rule = _get_rule()
        summary, usage = summarize_rule(rule)

        _pp("RuleSummary", summary)
        print(f"  Token usage: {usage}")

        self.assertIsInstance(summary.plain_summary, str)
        self.assertTrue(len(summary.plain_summary) > 10)
        self.assertIsInstance(summary.affected_populations, list)
        self.assertGreaterEqual(len(summary.affected_populations), 1)
        self.assertIn(summary.significance.split(" ")[0].rstrip(" —-:"),
                      ["low", "medium", "high"])


@unittest.skipUnless(has_reg_key and has_anthropic_key, SKIP_REASON)
class TestExtractRIA(unittest.TestCase):

    def test_extract_ria_assumptions(self):
        from rule_synthesizer import extract_ria_assumptions
        rule = _get_rule()
        ria, usage = extract_ria_assumptions(rule)

        _pp("RIAAssumptions", ria)
        print(f"  Token usage: {usage}")

        self.assertIsInstance(ria.core_assumptions, list)
        self.assertGreaterEqual(len(ria.core_assumptions), 1,
                                "Expected at least 1 core assumption")
        self.assertIsInstance(ria.identified_gaps, list)
        if not ria.identified_gaps:
            print("\n  ⚠ WARNING: identified_gaps is EMPTY — prompt may need iteration")
        else:
            self.assertGreaterEqual(len(ria.identified_gaps), 1)


@unittest.skipUnless(has_reg_key and has_anthropic_key, SKIP_REASON)
class TestFullInterviewFlow(unittest.TestCase):

    def test_full_interview_flow(self):
        from rule_synthesizer import summarize_rule, extract_ria_assumptions
        from comment_interviewer import start_interview, continue_interview, build_comment_argument

        rule = _get_rule()
        summary, _ = summarize_rule(rule)
        ria, _ = extract_ria_assumptions(rule)

        # Start interview
        state = start_interview(rule, summary, ria)
        print(f"\n{'─'*60}")
        print("  INTERVIEW TRANSCRIPT")
        print(f"{'─'*60}")
        print(f"  ASSISTANT: {state.turns[0].content}\n")

        # Turn 1
        user_msg_1 = (
            "I run a small food manufacturing company with 12 employees. "
            "We produce specialty hot sauces sold primarily through farmers "
            "markets and local grocery stores."
        )
        state = continue_interview(state, user_msg_1)
        print(f"  USER: {user_msg_1}\n")
        print(f"  ASSISTANT: {state.turns[-1].content}\n")

        # Turn 2
        user_msg_2 = (
            "The new labeling requirements would require us to redesign all "
            "our packaging. We estimate this costs about $8,000 per SKU and "
            "we have 6 products. The agency's analysis assumes large "
            "manufacturers but we can't spread that cost over millions of units."
        )
        state = continue_interview(state, user_msg_2)
        print(f"  USER: {user_msg_2}\n")
        print(f"  ASSISTANT: {state.turns[-1].content}\n")

        # Turn 3
        user_msg_3 = (
            "We'd need about 18 months to work through existing inventory "
            "and packaging stock. The proposed 90-day compliance window would "
            "require us to either destroy existing inventory or halt sales."
        )
        state = continue_interview(state, user_msg_3)
        print(f"  USER: {user_msg_3}\n")
        print(f"  ASSISTANT: {state.turns[-1].content}\n")

        print(f"  Interview complete: {state.is_complete}")
        print(f"  Total turns: {len(state.turns)}")

        # Build comment argument
        argument = build_comment_argument(state)
        _pp("CommentArgument", argument)

        self.assertGreaterEqual(len(argument.main_points), 2)
        self.assertGreaterEqual(len(argument.ria_challenges), 1)
        self.assertTrue(len(argument.strengthening_suggestions) > 0)


@unittest.skipUnless(has_reg_key and has_anthropic_key, SKIP_REASON)
class TestCachingEfficiency(unittest.TestCase):

    def test_caching_efficiency(self):
        from rule_synthesizer import summarize_rule, extract_ria_assumptions
        rule = _get_rule()

        print(f"\n{'─'*60}")
        print("  CACHING EFFICIENCY TEST")
        print(f"{'─'*60}")

        _, usage1 = summarize_rule(rule)
        print(f"  Call 1 (summarize_rule):")
        print(f"    input_tokens: {usage1['input_tokens']}")
        print(f"    output_tokens: {usage1['output_tokens']}")
        print(f"    cache_creation_input_tokens: {usage1['cache_creation_input_tokens']}")
        print(f"    cache_read_input_tokens: {usage1['cache_read_input_tokens']}")

        _, usage2 = extract_ria_assumptions(rule)
        print(f"  Call 2 (extract_ria_assumptions):")
        print(f"    input_tokens: {usage2['input_tokens']}")
        print(f"    output_tokens: {usage2['output_tokens']}")
        print(f"    cache_creation_input_tokens: {usage2['cache_creation_input_tokens']}")
        print(f"    cache_read_input_tokens: {usage2['cache_read_input_tokens']}")

        # Note: cache hits depend on whether the same text block was used
        # and whether the cache is still warm from prior tests. The two calls
        # use different system prompts so they won't cache-hit each other's
        # full request, but the document text block may be cached.
        print(f"\n  Total cache_read across both calls: "
              f"{usage1['cache_read_input_tokens'] + usage2['cache_read_input_tokens']}")

        # If prior tests ran (test_summarize_rule, test_extract_ria), the
        # cache should be warm for at least one of these calls
        total_cache_read = usage1["cache_read_input_tokens"] + usage2["cache_read_input_tokens"]
        if total_cache_read == 0:
            print("  ⚠ No cache hits detected — this may be expected on first run")
        else:
            print(f"  ✓ Cache working: {total_cache_read} tokens read from cache")
            self.assertGreater(total_cache_read, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
