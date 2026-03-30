"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getRule, analyzeRule, startInterview } from "@/lib/api";
import { DeadlineBadge } from "@/components/DeadlineBadge";
import type { RuleDetail, AnalysisResult } from "@/types";

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

export default function RuleDetailPage() {
  const params = useParams<{ documentId: string }>();
  const router = useRouter();
  const documentId = decodeURIComponent(params.documentId);

  const [rule, setRule] = useState<RuleDetail | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [startingInterview, setStartingInterview] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [ruleData, analysisData] = await Promise.all([
          getRule(documentId),
          analyzeRule(documentId),
        ]);
        if (cancelled) return;
        setRule(ruleData);
        setAnalysis(analysisData);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [documentId]);

  async function handleStartInterview() {
    setStartingInterview(true);
    try {
      const resp = await startInterview(documentId);
      sessionStorage.setItem("firstMessage", resp.message);
      sessionStorage.setItem("sessionId", resp.session_id);
      sessionStorage.setItem("regulationsGovUrl", rule?.regulations_gov_url ?? "");
      router.push(`/interview/${encodeURIComponent(resp.session_id)}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start interview");
      setStartingInterview(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <header className="mb-6">
        <a href="/browse" className="text-sm text-accent hover:text-accent-hover">
          ← Back
        </a>
        <a href="/" className="mt-2 block text-xl font-bold text-dark font-heading">
          Civly
        </a>
      </header>

      {/* Always show title immediately */}
      {rule && (
        <h1 className="mb-2 text-2xl font-bold text-dark">
          {rule.title}
        </h1>
      )}
      {!rule && !error && (
        <div className="mb-2 h-8 w-3/4 animate-pulse rounded bg-subtle" />
      )}

      {error && (
        <div className="rounded-lg bg-accent/10 p-4 text-sm text-accent">
          {error}
        </div>
      )}

      {/* Loading state */}
      {loading && !error && (
        <div className="mt-8 flex flex-col items-center gap-3 py-12">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-accent border-t-transparent" />
          <p className="text-sm text-mid">
            Analyzing this rule and its regulatory impact assessment...
          </p>
          <p className="text-xs text-mid">This takes about 10 seconds</p>
        </div>
      )}

      {/* Phase B — Rule detail + analysis */}
      {!loading && analysis && rule && (
        <div className="mt-6 space-y-6">
          {/* Block 1 — What's changing */}
          <div className="rounded-lg bg-subtle/50 p-6">
            <p className="text-sm text-dark">
              {analysis.rule_summary.plain_summary}
            </p>
            <div className="mt-4">
              <p className="text-sm font-medium text-dark">
                Specifically:
              </p>
              <p className="mt-1 text-sm text-dark">
                {analysis.rule_summary.what_is_changing}
              </p>
            </div>
            <div className="mt-4">
              <p className="mb-2 text-sm font-medium text-dark">
                Who this affects:
              </p>
              <div className="flex flex-wrap gap-2">
                {analysis.rule_summary.affected_populations.map((pop, i) => (
                  <span
                    key={i}
                    className="rounded-full bg-secondary/15 px-3 py-1 text-sm text-secondary"
                  >
                    {pop}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Block 2 — Comment deadline */}
          <div className="rounded-lg border border-subtle p-6">
            <div className="flex items-center gap-3">
              <DeadlineBadge daysRemaining={rule.days_remaining} />
              <span className="text-sm text-dark">
                Comments due {formatDate(rule.comment_deadline)}
              </span>
            </div>
            <p className="mt-3 text-sm text-mid">
              Comments submitted by this date are legally required to be
              considered by {rule.agency_id}.
            </p>
            <a
              href={rule.regulations_gov_url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-2 inline-block text-sm text-accent hover:text-accent-hover"
            >
              View on Regulations.gov →
            </a>
          </div>

          {/* Block 3 — Why your comment matters */}
          <div className="rounded-lg border border-subtle p-6">
            <h2 className="mb-3 text-base font-semibold text-dark">
              Why your comment matters
            </h2>
            <p className="mb-3 text-sm text-mid">
              Federal agencies must respond to substantive comments on the
              record. A substantive comment:
            </p>
            <ul className="mb-4 space-y-2 text-sm text-dark">
              <li className="flex gap-2">
                <span className="text-mid">•</span>
                Challenges a factual assumption in the agency&apos;s analysis
                with a concrete reason
              </li>
              <li className="flex gap-2">
                <span className="text-mid">•</span>
                Identifies a population or use case the agency may have missed
              </li>
              <li className="flex gap-2">
                <span className="text-mid">•</span>
                Proposes a specific regulatory alternative
              </li>
            </ul>
            <p className="text-xs text-mid">
              Generic complaints are not legally required to receive a response.
            </p>
          </div>

          {/* CTA */}
          <button
            onClick={handleStartInterview}
            disabled={startingInterview}
            className="w-full rounded-lg bg-accent px-6 py-3 text-sm font-medium font-heading text-light transition-colors hover:bg-accent-hover disabled:bg-accent/60 sm:w-auto"
          >
            {startingInterview
              ? "Starting interview..."
              : "Does this rule affect you? Tell us how →"}
          </button>
        </div>
      )}
    </div>
  );
}
