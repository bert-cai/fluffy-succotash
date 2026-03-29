export function DeadlineBadge({ daysRemaining }: { daysRemaining: number }) {
  let classes: string;
  if (daysRemaining <= 7) {
    classes = "bg-red-100 text-red-700";
  } else if (daysRemaining <= 21) {
    classes = "bg-amber-100 text-amber-700";
  } else {
    classes = "bg-green-100 text-green-700";
  }

  return (
    <span
      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${classes}`}
    >
      {daysRemaining} {daysRemaining === 1 ? "day" : "days"} left
    </span>
  );
}
