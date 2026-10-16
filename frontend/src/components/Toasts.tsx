import { useCallback, useRef, useState, type ReactNode } from "react";

// Shared toast vocabulary: bottom-right overlay alerts, so they never push
// the layout around. Tones: success (green tick), warning (amber danger
// sign), error (white cross on red, stays until closed), info (blue "i").
export type ToastTone = "success" | "warning" | "error" | "info";

export type Toast = {
  id: number;
  tone: ToastTone;
  message: string;
  leaving?: boolean;
};

const LEAVE_MS = 180;

const AUTO_DISMISS_MS: Record<ToastTone, number | null> = {
  success: 4000,
  info: 4000,
  warning: 6000,
  error: null,
};

const MAX_VISIBLE = 4;

function CheckIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} className="h-4 w-4" aria-hidden="true">
      <path d="M4 12.5l5 5L20 6.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function WarningIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-4 w-4" aria-hidden="true">
      <path d="M12 3.5L22 20H2z" strokeLinejoin="round" />
      <path d="M12 10v4.5" strokeLinecap="round" />
      <path d="M12 17.5h.01" strokeLinecap="round" strokeWidth={3} />
    </svg>
  );
}

function CrossIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} className="h-4 w-4" aria-hidden="true">
      <path d="M6 6l12 12M18 6L6 18" strokeLinecap="round" />
    </svg>
  );
}

function InfoIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-4 w-4" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v5" strokeLinecap="round" />
      <path d="M12 7.5h.01" strokeLinecap="round" strokeWidth={3} />
    </svg>
  );
}

const TONE_STYLE: Record<ToastTone, { box: string; dismiss: string; icon: ReactNode }> = {
  success: {
    box: "bg-green-600 text-white",
    dismiss: "text-green-100 hover:text-white",
    icon: <CheckIcon />,
  },
  warning: {
    box: "bg-amber-400 text-amber-950",
    dismiss: "text-amber-800 hover:text-amber-950",
    icon: <WarningIcon />,
  },
  error: {
    box: "bg-red-600 text-white",
    dismiss: "text-red-100 hover:text-white",
    icon: <CrossIcon />,
  },
  info: {
    box: "bg-weber-blue text-white",
    dismiss: "text-blue-100 hover:text-white",
    icon: <InfoIcon />,
  },
};

export function useToasts() {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const nextId = useRef(1);

  const dismiss = useCallback((id: number) => {
    // Flag first so the exit animation plays, then unmount.
    setToasts((list) => list.map((toast) => (toast.id === id ? { ...toast, leaving: true } : toast)));
    setTimeout(() => {
      setToasts((list) => list.filter((toast) => toast.id !== id));
    }, LEAVE_MS);
  }, []);

  const push = useCallback(
    (tone: ToastTone, message: string) => {
      const id = nextId.current++;
      setToasts((list) => [...list.slice(-(MAX_VISIBLE - 1)), { id, tone, message }]);
      const ms = AUTO_DISMISS_MS[tone];
      if (ms !== null) {
        setTimeout(() => dismiss(id), ms);
      }
    },
    [dismiss]
  );

  return { toasts, push, dismiss };
}

export function ToastStack({ toasts, onClose }: { toasts: Toast[]; onClose: (id: number) => void }) {
  if (toasts.length === 0) return null;
  return (
    <div className="pointer-events-none fixed bottom-3 right-3 z-50 flex w-full max-w-sm flex-col gap-2">
      {toasts.map((toast) => {
        const style = TONE_STYLE[toast.tone];
        return (
          <div
            key={toast.id}
            role={toast.tone === "error" ? "alert" : "status"}
            className={`pointer-events-auto flex items-start gap-2 rounded-lg p-3 text-sm shadow-xl ${
              toast.leaving ? "toast-leave" : "toast-enter"
            } ${style.box}`}
          >
            <span className="mt-0.5 shrink-0" aria-hidden="true">
              {style.icon}
            </span>
            <span className="min-w-0 flex-1 break-words">{toast.message}</span>
            <button
              type="button"
              onClick={() => onClose(toast.id)}
              aria-label="Close"
              className={`shrink-0 ${style.dismiss}`}
            >
              ✕
            </button>
          </div>
        );
      })}
    </div>
  );
}
