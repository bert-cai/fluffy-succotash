export default function BrowseLoading() {
  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <header className="mb-6 border-b border-subtle pb-6">
        <a href="/" className="text-2xl font-bold text-dark font-heading">Civly</a>
        <p className="mt-2 text-sm text-mid">
          Federal regulations open for public comment right now. Your input is
          legally required to be considered.
        </p>
      </header>

      {/* Agency filter placeholder */}
      <div className="mb-6 flex flex-wrap gap-2" aria-hidden="true">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="h-7 w-20 animate-pulse rounded-full bg-subtle"
          />
        ))}
      </div>

      {/* Rule card skeletons */}
      <div
        className="space-y-3"
        role="status"
        aria-label="Loading open comment periods"
      >
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="rounded-lg bg-subtle/50 p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="h-4 w-3/5 animate-pulse rounded bg-subtle" />
              <div className="h-5 w-16 animate-pulse rounded-full bg-subtle" />
            </div>
            <div className="mt-2 h-3 w-24 animate-pulse rounded bg-subtle" />
            <div className="mt-3 space-y-2">
              <div className="h-3 w-full animate-pulse rounded bg-subtle" />
              <div className="h-3 w-4/5 animate-pulse rounded bg-subtle" />
            </div>
          </div>
        ))}
        <span className="sr-only">Loading open comment periods…</span>
      </div>

      <footer className="mt-10 text-center text-xs text-mid">
        Data from Regulations.gov &middot; Updated every 6 hours
      </footer>
    </div>
  );
}
