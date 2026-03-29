"use client";

export function AgencyFilter({
  agencies,
  selected,
  onSelect,
}: {
  agencies: string[];
  selected: string | null;
  onSelect: (agency: string | null) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      <button
        onClick={() => onSelect(null)}
        className={`rounded-full px-3 py-1 text-sm font-medium transition-colors ${
          selected === null
            ? "bg-blue-600 text-white"
            : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
        }`}
      >
        All
      </button>
      {agencies.map((agency) => (
        <button
          key={agency}
          onClick={() => onSelect(selected === agency ? null : agency)}
          className={`rounded-full px-3 py-1 text-sm font-medium transition-colors ${
            selected === agency
              ? "bg-blue-600 text-white"
              : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
          }`}
        >
          {agency}
        </button>
      ))}
    </div>
  );
}
