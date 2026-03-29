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
        className={`rounded-full px-3 py-1 text-sm font-medium font-heading transition-colors ${
          selected === null
            ? "bg-accent text-light"
            : "border border-subtle bg-light text-mid hover:bg-subtle/50"
        }`}
      >
        All
      </button>
      {agencies.map((agency) => (
        <button
          key={agency}
          onClick={() => onSelect(selected === agency ? null : agency)}
          className={`rounded-full px-3 py-1 text-sm font-medium font-heading transition-colors ${
            selected === agency
              ? "bg-accent text-light"
              : "border border-subtle bg-light text-mid hover:bg-subtle/50"
          }`}
        >
          {agency}
        </button>
      ))}
    </div>
  );
}
