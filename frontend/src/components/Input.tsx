import type { InputHTMLAttributes } from "react";

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
};

export default function Input({
  label,
  className = "",
  ...props
}: InputProps) {
  const input = (
    <input
      {...props}
      className={`border rounded px-3 py-2 text-sm w-full outline-none focus:border-weber-blue focus:ring-1 focus:ring-weber-blue/20 ${className}`}
    />
  );

  if (!label) {
    return input;
  }

  return (
    <label className="block">
      <span className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </span>

      {input}
    </label>
  );
}