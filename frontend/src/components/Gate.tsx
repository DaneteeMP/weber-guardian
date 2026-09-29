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
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <form
        onSubmit={submit}
        className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 w-full max-w-sm space-y-3"
      >
        <h1 className="text-lg font-bold text-gray-900">{t(lang, "gate_title")}</h1>
        <p className="text-xs text-gray-500">{t(lang, "gate_hint")}</p>
        <label className="block text-sm">
          <span className="text-gray-600">{t(lang, "gate_user")}</span>
          <input
            value={user}
            onChange={(e) => setUser(e.target.value)}
            autoComplete="username"
            className="mt-1 border rounded px-2 py-1.5 text-sm w-full"
          />
        </label>
        <label className="block text-sm">
          <span className="text-gray-600">{t(lang, "gate_password")}</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            className="mt-1 border rounded px-2 py-1.5 text-sm w-full"
          />
        </label>
        {error && <p className="text-sm text-red-700 bg-red-50 border border-red-200 rounded px-2 py-1">{error}</p>}
        <button
          type="submit"
          disabled={busy}
          className="w-full px-4 py-2 rounded-md text-sm font-bold bg-weber-blue text-white hover:opacity-90 disabled:opacity-50"
        >
          {t(lang, "gate_enter")}
        </button>
      </form>
    </div>
  );
}
