import type { ReactNode } from "react";

// Label + value row used in breakdowns and headers. The emphasis flag marks
// the rows that carry the totals of the block.
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
    <div className={`flex justify-between py-0.5 text-sm ${emphasis ? "font-bold" : ""}`}>
      <span className={emphasis ? "text-gray-900" : "text-gray-600"}>{label}</span>
      <span className="font-mono text-right">{children}</span>
    </div>
  );
}
