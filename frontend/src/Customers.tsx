import { useEffect, useState } from "react";
import { getDevUser, listCustomers, type Customer } from "./api";
import SectionCard from "./components/SectionCard";
import { t, type Lang } from "./i18n";

const API_URL = "http://localhost:8000/api/v1/customers";
const PAGE_SIZE = 50;

export default function Customers({ lang, externalSearch = "" }: { lang: Lang; externalSearch?: string }) {
  const [rows, setRows] = useState<Customer[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState(externalSearch);
  const [customerId, setCustomerId] = useState("");
  const [accountName, setAccountName] = useState("");
  const [country, setCountry] = useState("");

  async function load(q: string, p: number) {
    setLoading(true);
    setError(null);
    try {
      const res = await listCustomers({ search: q.trim() || undefined, limit: PAGE_SIZE, offset: p * PAGE_SIZE });
      setRows(res.rows);
      setTotal(res.total);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Load failed");
    } finally {
      setLoading(false);
    }
  }

  // Server-side search (debounced) and paging: the grid always reflects
  // the database, never just the loaded page.
  useEffect(() => {
    const timer = setTimeout(() => {
      setPage(0);
      load(search, 0);
    }, 300);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  useEffect(() => {
    load(search, page);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  useEffect(() => {
    setSearch(externalSearch);
  }, [externalSearch]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      const dev = getDevUser();
      if (dev) headers["X-Dev-User"] = dev;
      const res = await fetch(API_URL, {
        method: "POST",
        headers,
        body: JSON.stringify({
          customer_id: customerId,
          account_name: accountName,
          country: country || null,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => null);
        const detail =
          typeof data?.detail === "string"
            ? data.detail
            : JSON.stringify(data?.detail ?? res.statusText);
        throw new Error(`POST failed (${res.status}): ${detail}`);
      }
      setCustomerId("");
      setAccountName("");
      setCountry("");
      setPage(0);
      await load("", 0);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Create failed");
    }
  }

  const input = "border rounded px-2 py-1.5 text-sm w-full";

  return (
    <div className="p-4 space-y-3 w-full">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">{t(lang, "cust_title")}</h1>
        <span className="text-sm text-gray-500">
          {rows.length} / {total.toLocaleString()}
        </span>
      </div>

      {error && <p className="text-sm text-red-600 bg-white rounded-lg shadow p-3">{error}</p>}

      <div className="grid grid-cols-12 gap-3">
        <div className="col-span-4">
          <SectionCard title={t(lang, "cust_create")}>
            <form onSubmit={handleSubmit} className="space-y-2">
              <input
                placeholder={t(lang, "cust_id_ph")}
                value={customerId}
                onChange={(e) => setCustomerId(e.target.value)}
                className={`${input} bg-blue-50 font-mono`}
              />
              <input
                placeholder={t(lang, "cust_name_ph")}
                value={accountName}
                onChange={(e) => setAccountName(e.target.value)}
                className={input}
              />
              <input
                placeholder={t(lang, "cust_country_ph")}
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className={input}
              />
              <button type="submit" className="w-full px-3 py-1.5 rounded text-sm font-medium bg-weber-blue text-white hover:opacity-90">
                {t(lang, "cust_create")}
              </button>
            </form>
          </SectionCard>
        </div>

        <div className="col-span-8">
          <SectionCard title={`${t(lang, "nav_customers")} (${total.toLocaleString()})`}>
            <input
              placeholder={t(lang, "cust_search_ph")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className={`${input} mb-2`}
            />
            <div className="flex items-center justify-between mb-2 text-sm">
              <button
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                className="px-2 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-40"
              >
                ←
              </button>
              <span className="text-gray-500">
                {page * PAGE_SIZE + (rows.length ? 1 : 0)}–{page * PAGE_SIZE + rows.length} / {total.toLocaleString()}
              </span>
              <button
                disabled={(page + 1) * PAGE_SIZE >= total}
                onClick={() => setPage((p) => p + 1)}
                className="px-2 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-40"
              >
                →
              </button>
            </div>
            {loading ? (
              <p className="text-sm text-gray-500">{t(lang, "cust_loading")}</p>
            ) : (
              <div className="overflow-auto max-h-[calc(90vh-220px)] min-h-[400px]">
                <table className="w-full text-sm">
                  <thead className="sticky top-0">
                    <tr className="bg-weber-blue text-white text-left">
                      <th className="px-3 py-2 font-semibold">{t(lang, "cust_col_sap")}</th>
                      <th className="px-3 py-2 font-semibold">{t(lang, "cust_name_ph")}</th>
                      <th className="px-3 py-2 font-semibold">{t(lang, "cust_col_country")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((c, i) => (
                      <tr key={c.id} className={`border-b last:border-0 ${i % 2 ? "bg-gray-50" : "bg-white"} hover:bg-blue-50`}>
                        <td className="px-3 py-1.5 font-mono font-semibold text-weber-blue">{c.customer_id}</td>
                        <td className="px-3 py-1.5">{c.account_name}</td>
                        <td className="px-3 py-1.5 text-gray-600">{c.country ?? "—"}</td>
                      </tr>
                    ))}
                    {rows.length === 0 && (
                      <tr>
                        <td colSpan={3} className="px-3 py-8 text-center text-gray-400">
                          —
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </SectionCard>
        </div>
      </div>
    </div>
  );
}
