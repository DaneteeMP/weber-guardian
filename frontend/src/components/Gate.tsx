// Entry gate for the public demo. Shown only when the API answers with a Basic
// challenge, so local dev (no gate configured) never sees it. It never stores
// anything in the bundle: the shared password lives in sessionStorage.
import { useState } from "react";
import { clearGateCredentials, probeGate, setGateCredentials } from "../api";
import { t, type Lang } from "../i18n";

export default function Gate({ lang, onPass }: { lang: Lang; onPass: () => void }) {
  const [user, setUser] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setGateCredentials(user, password);
    try {
      if (await probeGate()) {
        onPass();
        return;
      }
      clearGateCredentials();
      setError(t(lang, "gate_error"));
    } catch {
      clearGateCredentials();
      setError(t(lang, "gate_error"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas p-4">
      <form
        onSubmit={submit}
        className="w-full max-w-sm space-y-3 rounded-xl border border-line bg-white p-6"
      >
        <h1 className="text-lg font-bold text-ink">{t(lang, "gate_title")}</h1>
        <p className="text-xs text-muted">{t(lang, "gate_hint")}</p>
        <label className="block text-sm">
          <span className="ui-label">{t(lang, "gate_user")}</span>
          <input
            value={user}
            onChange={(e) => setUser(e.target.value)}
            autoComplete="username"
            className="ui-input w-full"
          />
        </label>
        <label className="block text-sm">
          <span className="ui-label">{t(lang, "gate_password")}</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            className="ui-input w-full"
          />
        </label>
        {error && <p className="rounded-lg border border-red-200 bg-red-50 px-2 py-1 text-sm text-red-700">{error}</p>}
        <button
          type="submit"
          disabled={busy}
          className="h-9 w-full rounded-lg border border-primary bg-primary px-4 text-sm font-medium text-white transition hover:bg-primary/90 disabled:opacity-50"
        >
          {t(lang, "gate_enter")}
        </button>
      </form>
    </div>
  );
}
