import { getRules } from "@/lib/api";
import { RuleBrowser } from "@/components/RuleBrowser";
import type { Rule } from "@/types";

export const dynamic = "force-dynamic";

export default async function BrowsePage() {
  let rules: Rule[] = [];
  try {
    rules = await getRules();
  } catch {
    // render empty state on fetch failure
  }

  // sort by most urgent first
  rules.sort((a, b) => a.days_remaining - b.days_remaining);

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <header className="mb-6 border-b border-subtle pb-6">
        <a href="/" className="text-2xl font-bold text-dark font-heading">Civly</a>
        <p className="mt-2 text-sm text-mid">
          Federal regulations open for public comment right now. Your input is
          legally required to be considered.
        </p>
      </header>

      <RuleBrowser rules={rules} />

      <footer className="mt-10 text-center text-xs text-mid">
        Data from Regulations.gov &middot; Updated every 6 hours
      </footer>
    </div>
  );
}
