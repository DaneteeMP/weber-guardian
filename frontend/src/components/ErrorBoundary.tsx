import { Component, type ReactNode } from "react";
import { t, type Lang } from "../i18n";

// Last-resort crash net: without it any render throw unmounts the whole app
// and the user stares at a blank page with nothing to report. This shows what
// broke (so it can be pasted into a bug report) plus a reload button.
export default class ErrorBoundary extends Component<
  { lang: Lang; children: ReactNode },
  { error: unknown }
> {
  state = { error: null as unknown };

  static getDerivedStateFromError(error: unknown) {
    return { error };
  }

  componentDidCatch(error: unknown) {
    console.error(error);
  }

  render() {
    if (this.state.error) {
      const message =
        this.state.error instanceof Error ? this.state.error.message : String(this.state.error);
      return (
        <div className="flex min-h-screen items-center justify-center bg-canvas p-4">
          <div className="max-w-sm rounded-xl border border-red-200 bg-white p-5 text-center">
            <p className="text-sm font-bold text-ink">{t(this.props.lang, "err_crash_title")}</p>
            <p className="mt-1 break-words text-xs text-muted">{message}</p>
            <button
              type="button"
              onClick={() => window.location.reload()}
              className="mt-3 h-9 rounded-lg border border-primary bg-primary px-4 text-sm font-medium text-white transition hover:bg-primary/90"
            >
              {t(this.props.lang, "err_crash_retry")}
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
