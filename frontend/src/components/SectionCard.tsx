import type { ReactNode } from "react";

type SectionCardProps = {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
};

export default function SectionCard({
  title,
  subtitle,
  children,
  className = "",
}: SectionCardProps) {
  return (
    <section className={`rounded-xl border border-line bg-white ${className}`}>
      {title && (
        <div className="flex shrink-0 items-center justify-between gap-3 border-b border-line px-5 py-3.5">
          <div>
            <h2 className="text-[15px] font-semibold text-ink">{title}</h2>
            {subtitle && <p className="mt-px text-xs text-muted">{subtitle}</p>}
          </div>
        </div>
      )}

      <div className="flex min-h-0 flex-1 flex-col px-5 py-4">{children}</div>
    </section>
  );
}
