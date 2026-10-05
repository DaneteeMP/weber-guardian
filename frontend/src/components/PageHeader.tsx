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
        <h1 className="text-2xl font-bold text-gray-900">
          {title}
        </h1>

        {count !== undefined && (
          <span className="text-sm text-gray-500">
            {count.toLocaleString()}
          </span>
        )}
      </div>

      {action}
    </div>
  );
}