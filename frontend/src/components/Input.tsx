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
      className={`ui-input w-full ${className}`}
    />
  );

  if (!label) {
    return input;
  }

  return (
    <label className="block">
      <span className="ui-label">{label}</span>

      {input}
    </label>
  );
}
