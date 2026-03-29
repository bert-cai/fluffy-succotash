"use client";

import type { CommentArgument } from "@/types";

export function ArgumentDisplay({
  argument,
  regulationsGovUrl,
}: {
  argument: CommentArgument;
  regulationsGovUrl: string;
}) {
  return (
    <div className="space-y-8">
      {/* Section 1 — Main points */}
      <section>
        <h2 className="mb-4 text-lg font-semibold text-slate-900">
          What your comment should argue
        </h2>
        <div className="space-y-4">
          {argument.main_points.map((point, i) => (
            <div
              key={i}
              className="rounded-lg border border-slate-200 bg-white p-4"
            >
              <div className="mb-1 text-xs font-medium text-blue-600">
                Point {i + 1}
              </div>
              <p className="text-sm text-slate-900">{point}</p>
              {argument.ria_challenges[i] && (
                <p className="mt-3 text-xs text-slate-500">
                  <span className="font-medium">
                    Challenges agency assumption:{" "}
                  </span>
                  {argument.ria_challenges[i]}
                </p>
              )}
            </div>
          ))}
          {/* Show remaining ria_challenges not matched by index */}
          {argument.ria_challenges.length > argument.main_points.length &&
            argument.ria_challenges
              .slice(argument.main_points.length)
              .map((challenge, i) => (
                <div
                  key={`extra-${i}`}
                  className="rounded-lg border border-slate-200 bg-white p-4"
                >
                  <p className="text-xs text-slate-500">
                    <span className="font-medium">
                      Additional agency assumption challenged:{" "}
                    </span>
                    {challenge}
                  </p>
                </div>
              ))}
        </div>
      </section>

      {/* Section 2 — Strengthening suggestions */}
      {argument.strengthening_suggestions.length > 0 && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-slate-900">
            What would make this stronger
          </h2>
          <div className="rounded-lg bg-slate-50 p-5">
            <p className="mb-3 text-xs font-medium text-slate-500">
              If you can provide any of the following, add it before submitting
            </p>
            <ul className="space-y-2">
              {argument.strengthening_suggestions.map((s, i) => (
                <li key={i} className="flex gap-2 text-sm text-slate-700">
                  <span className="mt-0.5 text-slate-400">○</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {/* Section 3 — Alternatives */}
      {argument.suggested_alternatives.length > 0 && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-slate-900">
            Alternatives you could propose
          </h2>
          <ul className="space-y-2">
            {argument.suggested_alternatives.map((alt, i) => (
              <li key={i} className="flex gap-2 text-sm text-slate-700">
                <span className="mt-0.5 text-slate-400">•</span>
                <span>{alt}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Section 4 — Submit */}
      <section>
        <h2 className="mb-4 text-lg font-semibold text-slate-900">
          Submit your comment
        </h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <button
              disabled
              className="w-full cursor-not-allowed rounded-lg bg-slate-100 px-6 py-3 text-sm font-medium text-slate-400"
            >
              Draft my comment
            </button>
            <p className="mt-2 text-center text-xs text-slate-400">
              Full comment drafting coming soon
            </p>
          </div>
          <div>
            <a
              href={regulationsGovUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full rounded-lg bg-blue-600 px-6 py-3 text-center text-sm font-medium text-white transition-colors hover:bg-blue-700"
            >
              Submit on Regulations.gov
            </a>
            <details className="mt-2">
              <summary className="cursor-pointer text-center text-xs text-slate-500 hover:text-slate-700">
                Use this outline when writing your comment
              </summary>
              <pre className="mt-2 whitespace-pre-wrap rounded-lg bg-slate-50 p-4 text-xs text-slate-700">
                {argument.draft_structure}
              </pre>
            </details>
          </div>
        </div>
      </section>

      {/* Back link */}
      <div className="pt-4 text-center">
        <a href="/" className="text-sm text-blue-600 hover:text-blue-700">
          ← Start over with a different rule
        </a>
      </div>
    </div>
  );
}
