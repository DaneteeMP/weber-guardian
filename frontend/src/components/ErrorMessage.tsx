import type { ReactNode } from "react";

type ErrorMessageProps = {
  children: ReactNode;
};

export default function ErrorMessage({
  children,
}: ErrorMessageProps) {
  return (
    <p className="text-sm text-red-600 bg-white rounded-lg shadow p-3">
      {children}
    </p>
  );
}