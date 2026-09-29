import { useEffect, useState } from "react";
import {
  assignCountries,
  autoAssignAll,
  getSubsidiaryStats,
  getUnassignedCountries,
  listSubsidiaries,
  type Subsidiary,
  type SubsidiaryStats,
  type UnassignedCountry,
} from "./api";
import SectionCard from "./components/SectionCard";
import { t, type Lang } from "./i18n";

// Admin-only filial management: supervised countries and customers per
// filial, plus assigning ownerless countries. Writes go through the
// admin-guarded endpoints.
export default function Subsidiaries({ lang, isAdmin }: { lang: Lang; isAdmin: boolean }) {
  const [rows, setRows] = useState<SubsidiaryStats[]>([]);
  const [pending, setPending] = useState<UnassignedCountry[]>([]);
  const [all, setAll] = useState<Subsidiary[]>([]);
  const [pick, setPick] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const [autoWarnings, setAutoWarnings] = useState<string[]>([]);

  async function refresh() {
    try {
      const [s, u, a] = await Promise.all([getSubsidiaryStats(), getUnassignedCountries(), listSubsidiaries()]);
      setRows(s);
      setPending(u);
      setAll(a);
    } catch (e) {
      setError(String(e));
    }
  }

  useEffect(() => {
    if (isAdmin) refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin]);

  async function assign(country: string) {
    const subsidiary = pick[country];
    if (!subsidiary) return;
    setError(null);
    setOk(null);
    try {
      const res = await assignCountries([{ country, subsidiary }]);
      setOk(`${res.updated} ✓`);
      await refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  async function autoAssign() {
    setError(null);
    setOk(null);
    setAutoWarnings([]);
    try {
      const res = await autoAssignAll();
      setOk(`${res.updated} ✓`);
      setAutoWarnings(res.warnings);
      await refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  if (!isAdmin) return <p className="p-4 text-sm text-gray-500">{t(lang, "cfg_admin_only")}</p>;

  const input = "border rounded px-2 py-1 text-sm";

  return (
    <div className="p-4 space-y-3 w-full">
      <h1 className="text-2xl font-bold text-gray-900">{t(lang, "sub_title")}</h1>
      <div>
        <button onClick={autoAssign} className="px-4 py-2 rounded-lg text-sm font-bold bg-weber-blue text-white shadow hover:opacity-90">
          {t(lang, "sub_auto")}
        </button>
      </div>
      {error && <p className="text-sm text-red-600 bg-white rounded shadow p-2">{error}</p>}
      {ok && <p className="text-sm text-green-700 bg-white rounded shadow p-2">{ok}</p>}
      {autoWarnings.length > 0 && (
        <ul className="text-xs text-amber-700 bg-white rounded shadow p-2 space-y-1">
          {autoWarnings.map((w, i) => (
            <li key={i}>⚠ {w}</li>
          ))}
        </ul>
      )}

      <SectionCard title={t(lang, "sub_title")}>
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-weber-blue text-white text-left">
              <th className="px-3 py-1.5">Filial</th>
              <th className="px-3 py-1.5 text-right">{t(lang, "sub_countries")}</th>
              <th className="px-3 py-1.5 text-right">{t(lang, "dash_customers")}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.name} className="border-b last:border-0 hover:bg-blue-50">
                <td className="px-3 py-1.5">
                  <span className="font-semibold">{r.short_label}</span>{" "}
                  <span className="text-gray-500 text-xs">{r.name}</span>
                </td>
                <td className="px-3 py-1.5 text-right font-mono">{r.countries}</td>
                <td className="px-3 py-1.5 text-right font-mono">{r.customers.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </SectionCard>

      <SectionCard title={`${t(lang, "sub_unassigned")} (${pending.length})`}>
        {pending.length === 0 ? (
          <p className="text-sm text-gray-500">—</p>
        ) : (
          <table className="w-full text-sm">
            <tbody>
              {pending.map((u) => (
                <tr key={u.country} className="border-b last:border-0">
                  <td className="px-3 py-1.5">{u.country}</td>
                  <td className="px-3 py-1.5 text-right font-mono text-gray-500">{u.count}</td>
                  <td className="px-3 py-1.5 text-right whitespace-nowrap">
                    <select
                      value={pick[u.country] ?? ""}
                      onChange={(e) => setPick({ ...pick, [u.country]: e.target.value })}
                      className={`${input} mr-2`}
                    >
                      <option value="">—</option>
                      {all.map((f) => (
                        <option key={f.name} value={f.name}>
                          {f.short_label}
                        </option>
                      ))}
                    </select>
                    <button onClick={() => assign(u.country)} disabled={!pick[u.country]} className="px-3 py-1 rounded text-xs bg-weber-blue text-white disabled:opacity-40">
                      {t(lang, "sub_assign")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </SectionCard>
    </div>
  );
}
