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
        <div className="flex min-h-screen items-center justify-center bg-gray-100 p-4">
          <div className="max-w-sm rounded-lg border border-red-200 bg-white p-4 text-center shadow-sm">
            <p className="text-sm font-bold text-gray-900">{t(this.props.lang, "err_crash_title")}</p>
            <p className="mt-1 break-words text-xs text-gray-500">{message}</p>
            <button
              type="button"
              onClick={() => window.location.reload()}
              className="mt-3 rounded-md bg-weber-blue px-4 py-2 text-sm font-bold text-white hover:opacity-90"
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
