import type { ReactNode } from "react";

// White card with a small uppercase section title, as in OfferBuilder.
export default function SectionCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="bg-white rounded-lg shadow p-4">
      <h2 className="text-xs font-bold text-gray-500 uppercase mb-2">{title}</h2>
      {children}
    </section>
  );
}
