import { useEffect, type ReactNode } from "react";

// Centered dialog over a dimmed backdrop. Closes on backdrop click,
// the X button, or Escape. No dependencies, no portal magic.
export default function Modal({
  title,
  onClose,
  children,
  widthClass = "max-w-md",
}: {
  title: string;
  onClose: () => void;
  children: ReactNode;
  // Tailwind max-width class; wide dialogs (tables) pass e.g. "max-w-3xl".
  widthClass?: string;
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
      <div className={`bg-white rounded-lg shadow-xl w-full ${widthClass}`} onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-4 py-2 border-b">
          <h3 className="text-sm font-bold text-gray-700">{title}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 text-lg leading-none" aria-label="Close">
            ×
          </button>
        </div>
        <div className="p-4">{children}</div>
      </div>
    </div>
  );
}
