import type { ReactNode } from "react";

type ErrorMessageProps = {
  children: ReactNode;
};

export default function ErrorMessage({
  children,
}: ErrorMessageProps) {
  return (
    <p className="rounded-xl border border-red-200 bg-white p-3 text-sm text-red-600">
      {children}
    </p>
  );
}