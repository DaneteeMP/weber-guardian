import type { ReactNode } from "react";

// Label + value row used in breakdowns and headers. The emphasis flag marks
// the rows that carry the totals of the block. Compact by default so it
// matches the module list next to it in the offer builder.
export default function FieldRow({
  label,
  children,
  emphasis = false,
}: {
  label: string;
  children: ReactNode;
  emphasis?: boolean;
}) {
  return (
    <div className={`flex justify-between py-0.5 text-[11px] ${emphasis ? "font-bold" : ""}`}>
      <span className={emphasis ? "text-gray-900" : "text-gray-600"}>{label}</span>
      <span className="font-mono text-right">{children}</span>
    </div>
  );
}
