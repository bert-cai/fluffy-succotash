export function DeadlineBadge({ daysRemaining }: { daysRemaining: number }) {
  let classes: string;
  if (daysRemaining <= 7) {
    classes = "bg-accent/15 text-accent";
  } else if (daysRemaining <= 21) {
    classes = "bg-secondary/15 text-secondary";
  } else {
    classes = "bg-tertiary/15 text-tertiary";
  }

  return (
    <span
      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium font-heading ${classes}`}
    >
      {daysRemaining} {daysRemaining === 1 ? "day" : "days"} left
    </span>
  );
}
