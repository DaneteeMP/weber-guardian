import type { ReactNode } from "react";

// Label + value row used in breakdowns and headers.
export default function FieldRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex justify-between py-0.5 text-sm">
      <span className="text-gray-600">{label}</span>
      <span className="font-mono text-right">{children}</span>
    </div>
  );
}
