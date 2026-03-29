"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { Rule } from "@/types";
import { AgencyFilter } from "./AgencyFilter";
import { RuleCard } from "./RuleCard";

export function RuleBrowser({ rules }: { rules: Rule[] }) {
  const router = useRouter();
  const [selectedAgency, setSelectedAgency] = useState<string | null>(null);

  const agencies = [...new Set(rules.map((r) => r.agency_id))].sort();

  const filtered = selectedAgency
    ? rules.filter((r) => r.agency_id === selectedAgency)
    : rules;

  return (
    <>
      <div className="mb-6">
        <AgencyFilter
          agencies={agencies}
          selected={selectedAgency}
          onSelect={setSelectedAgency}
        />
      </div>

      <div className="space-y-3">
        {filtered.length === 0 ? (
          <p className="py-12 text-center text-mid">
            No open comment periods match this filter.
          </p>
        ) : (
          filtered.map((rule) => (
            <RuleCard
              key={rule.document_id}
              rule={rule}
              onClick={() =>
                router.push(`/rules/${encodeURIComponent(rule.document_id)}`)
              }
            />
          ))
        )}
      </div>
    </>
  );
}
