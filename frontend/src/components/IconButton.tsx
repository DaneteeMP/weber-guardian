import type { ReactNode } from "react";

type IconButtonProps = {
  icon: ReactNode;
  label: string;
  onClick: () => void;
  variant?: "default" | "danger";
  disabled?: boolean;
};

export default function IconButton({
  icon,
  label,
  onClick,
  variant = "default",
  disabled = false,
}: IconButtonProps) {
  return (
    <button
      type="button"
      title={label}
      aria-label={label}
      onClick={onClick}
      disabled={disabled}
      className={[
        "inline-flex h-8 w-8 items-center justify-center rounded-lg border",
        "transition-colors disabled:cursor-not-allowed disabled:opacity-50",
        variant === "danger"
          ? "border-red-200 text-red-600 hover:bg-red-50"
          : "border-line text-muted hover:bg-canvas hover:text-ink",
      ].join(" ")}
    >
      {icon}
    </button>
  );
}