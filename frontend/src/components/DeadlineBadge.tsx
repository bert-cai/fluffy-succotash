export function DeadlineBadge({ daysRemaining }: { daysRemaining: number }) {
  let classes: string;
  if (daysRemaining <= 1) {
    classes = "bg-accent/15 text-accent";
  } else if (daysRemaining <= 7) {
    classes = "bg-secondary/15 text-secondary";
  } else {
    classes = "bg-tertiary/15 text-tertiary";
  }

  return (
    <span
      className={`inline-block whitespace-nowrap shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${classes}`}
    >
      {daysRemaining} {daysRemaining === 1 ? "day" : "days"} left
    </span>
  );
}
