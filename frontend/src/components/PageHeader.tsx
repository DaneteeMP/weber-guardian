import type { ReactNode } from "react";

type PageHeaderProps = {
  title: string;
  count?: number;
  action?: ReactNode;
};

export default function PageHeader({
  title,
  count,
  action,
}: PageHeaderProps) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-[22px] font-bold leading-tight text-ink">
          {title}
        </h1>

        {count !== undefined && (
          <span className="text-[12.5px] text-muted">
            {count.toLocaleString()}
          </span>
        )}
      </div>

      {action}
    </div>
  );
}
