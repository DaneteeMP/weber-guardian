import { useEffect, type ReactNode } from "react";

// Centered dialog over a dimmed backdrop. Closes on backdrop click,
// the X button, or Escape. No dependencies, no portal magic.
export default function Modal({
  title,
  onClose,
  children,
  widthClass = "max-w-md",
  bodyClass = "p-5",
}: {
  title: string;
  onClose: () => void;
  children: ReactNode;
  // Tailwind max-width class; wide dialogs (tables) pass e.g. "max-w-3xl".
  widthClass?: string;
  // Content padding/layout; full-height dialogs pass e.g. "p-4 flex flex-col h-[85vh]".
  bodyClass?: string;
}) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div className={`w-full rounded-xl border border-line bg-white shadow-xl ${widthClass}`} onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between border-b border-line px-5 py-3.5">
          <h3 className="text-[15px] font-semibold text-ink">{title}</h3>
          <button onClick={onClose} className="text-lg leading-none text-muted transition hover:text-ink" aria-label="Close">
            ×
          </button>
        </div>
        <div className={bodyClass}>{children}</div>
      </div>
    </div>
  );
}
