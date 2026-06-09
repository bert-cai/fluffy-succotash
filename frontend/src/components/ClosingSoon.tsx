"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { getRules } from "@/lib/api";
import type { Rule } from "@/types";
import { DeadlineBadge } from "./DeadlineBadge";

type State =
  | { status: "loading" }
  | { status: "ready"; rules: Rule[] }
  | { status: "fallback" };

// The hero leads with real, closing-soon comment periods when the backend
// responds; if it's slow, errors, or has nothing open, the slot falls back to
// the static product screenshot so first paint never depends on the API.
export function ClosingSoon() {
  const [state, setState] = useState<State>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;
    getRules(undefined, 8000)
      .then((rules) => {
        if (cancelled) return;
        const soonest = rules
          .filter((r) => r.days_remaining >= 0)
          .sort((a, b) => a.days_remaining - b.days_remaining)
          .slice(0, 3);
        setState(
          soonest.length > 0
            ? { status: "ready", rules: soonest }
            : { status: "fallback" },
        );
      })
      .catch(() => {
        if (!cancelled) setState({ status: "fallback" });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (state.status === "fallback") {
    return (
      <div className="mx-auto max-w-4xl px-6">
        <Image
          src="/app-screenshot.png"
          alt="Civly app showing open federal comment periods"
          width={2940}
          height={1666}
          className="rounded-xl border border-subtle shadow-2xl"
        />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl px-6">
      <div className="overflow-hidden rounded-xl border border-subtle bg-light">
        <div className="flex items-baseline justify-between border-b border-subtle px-5 py-3">
          <span className="font-heading text-sm font-semibold text-dark">
            Closing soon
          </span>
          <span className="font-heading text-xs text-ink-soft">
            Open for public comment
          </span>
        </div>

        <ul className="divide-y divide-subtle">
          {state.status === "loading"
            ? Array.from({ length: 3 }).map((_, i) => (
                <li
                  key={i}
                  className="flex items-center gap-3 px-5 py-4"
                  aria-hidden="true"
                >
                  <div className="min-w-0 flex-1 space-y-2">
                    <div className="h-3.5 w-4/5 animate-pulse rounded bg-subtle motion-reduce:animate-none" />
                    <div className="h-3 w-16 animate-pulse rounded bg-subtle motion-reduce:animate-none" />
                  </div>
                  <div className="h-5 w-16 shrink-0 animate-pulse rounded-full bg-subtle motion-reduce:animate-none" />
                </li>
              ))
            : state.rules.map((rule) => (
                <li key={rule.document_id}>
                  <a
                    href={`/rules/${encodeURIComponent(rule.document_id)}`}
                    className="flex items-center gap-3 px-5 py-4 transition-colors hover:bg-subtle/50"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate font-body text-sm text-dark">
                        {rule.title}
                      </p>
                      <p className="mt-0.5 font-heading text-xs font-medium text-ink-soft">
                        {rule.agency_id}
                      </p>
                    </div>
                    <DeadlineBadge daysRemaining={rule.days_remaining} />
                  </a>
                </li>
              ))}
        </ul>

        <a
          href="/browse"
          className="block border-t border-subtle px-5 py-3 text-center font-heading text-sm font-medium text-accent transition-colors hover:bg-subtle/50 hover:text-accent-hover"
        >
          See all open rules →
        </a>
      </div>
      {state.status === "loading" && (
        <span className="sr-only" role="status">
          Loading comment periods that are closing soon…
        </span>
      )}
    </div>
  );
}
