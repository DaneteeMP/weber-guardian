import type { ReactNode } from "react";

type SectionCardProps = {
  title?: string;
  children: ReactNode;
  className?: string;
};

export default function SectionCard({
  title,
  children,
  className = "",
}: SectionCardProps) {
  return (
    <section
      className={`rounded-lg bg-white shadow ${className}`}
    >
      {title && (
        <h2 className="shrink-0 border-b px-4 py-3 text-sm font-semibold text-gray-900">
          {title}
        </h2>
      )}

      <div className="flex min-h-0 flex-1 flex-col p-4">
        {children}
      </div>
    </section>
  );
}