"use client";

import type { Rule } from "@/types";
import { DeadlineBadge } from "./DeadlineBadge";

export function RuleCard({
  rule,
  onClick,
}: {
  rule: Rule;
  onClick: () => void;
}) {
  const summaryText =
    rule.summary && rule.summary.length > 120
      ? rule.summary.slice(0, 120) + "…"
      : rule.summary ?? "No summary available for this proposed rule.";

  return (
    <button
      onClick={onClick}
      className="w-full cursor-pointer rounded-lg bg-subtle/50 p-4 text-left transition-shadow hover:bg-light hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-3">
        <h2 className="line-clamp-2 text-sm font-semibold text-dark">
          {rule.title}
        </h2>
        <DeadlineBadge daysRemaining={rule.days_remaining} />
      </div>
      <p className="mt-1 text-xs font-medium text-mid">
        {rule.agency_id}
      </p>
      <p className="mt-2 text-sm text-mid">{summaryText}</p>
    </button>
  );
}
