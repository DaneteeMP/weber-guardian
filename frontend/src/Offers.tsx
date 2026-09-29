import { useCallback, useEffect, useMemo, useState } from "react";
import {
  closeOffer,
  deleteOffer,
  downloadOfferPdf,
  getOffersSummary,
  listAllCustomers,
  listAllOffers,
  setOfferStatus,
  type Customer,
  type OfferListItem,
  type OffersSummary,
} from "./api";
import CustomerRankingChart from "./components/charts/CustomerRankingChart";
import MonthlyOffersChart from "./components/charts/MonthlyOffersChart";
import StatusDonutChart from "./components/charts/StatusDonutChart";
import { t, type Lang } from "./i18n";

// Dense monitoring home: status/monthly/ranking panels on top, full offer table
// below with the whole scope and row actions (close, reopen, PDF, delete).
// Editing an existing offer happens in OfferBuilder, so we only pass the id.
// The charts live in components/charts; this file only feeds them.
export default function OffersHome({
  lang,
  onNew,
  onEdit,
}: {
  lang: Lang;
  onNew: () => void;
  onEdit: (offerId: string) => void;
}) {
  const [offers, setOffers] = useState<OfferListItem[]>([]);
  const [summary, setSummary] = useState<OffersSummary | null>(null);
  const [names, setNames] = useState<Record<string, string>>({});
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    listAllCustomers()
      .then((cs: Customer[]) =>
        setNames(Object.fromEntries(cs.map((c) => [c.customer_id, c.account_name])))
      )
      .catch(() => {});
  }, []);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.all([listAllOffers(200, statusFilter || undefined), getOffersSummary()])
      .then(([rows, s]) => {
        setOffers(rows);
        setSummary(s);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [statusFilter]);

  useEffect(load, [load]);

  const statuses = useMemo(() => summary?.by_status ?? [], [summary]);

  const visible = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return offers;
    return offers.filter(
      (o) =>
        o.id_guardian_offer.toLowerCase().includes(q) ||
        o.customer_id.toLowerCase().includes(q) ||
        (names[o.customer_id] ?? "").toLowerCase().includes(q)
    );
  }, [offers, search, names]);

  const money = (v: string | number | null | undefined) =>
    Number(v ?? 0).toLocaleString("en-GB", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const day = (v: string | null | undefined) => (v ? v.slice(0, 10) : "");

  async function run(action: Promise<unknown>, message: string) {
    setError(null);
    try {
      await action;
      setNotice(message);
      load();
    } catch (e) {
      setError(String(e));
    }
  }

  function askDelete(offer: OfferListItem) {
    const text = t(lang, "home_confirm_delete").replace("{n}", offer.id_guardian_offer);
    if (window.confirm(text)) run(deleteOffer(offer.id), t(lang, "home_deleted"));
  }

  function askClose(offer: OfferListItem) {
    const text = t(lang, "home_confirm_close").replace("{n}", offer.id_guardian_offer);
    if (window.confirm(text)) run(closeOffer(offer.id), t(lang, "home_updated"));
  }

  return (
    <div className="p-3 w-full space-y-3">
      <div className="flex items-center gap-3">
        <h1 className="text-xl font-bold text-gray-900">{t(lang, "home_list")}</h1>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={t(lang, "home_search_ph")}
          className="flex-1 max-w-md px-2.5 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-weber-blue"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-2.5 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-weber-blue"
        >
          <option value="">{t(lang, "home_filter_all")}</option>
          {statuses.map((s) => (
            <option key={s.status} value={s.status}>
              {s.status} ({s.count})
            </option>
          ))}
        </select>
        <button
          onClick={onNew}
          className="ml-auto px-4 py-2 rounded-md text-sm font-bold bg-weber-blue text-white hover:opacity-90"
        >
          + {t(lang, "home_new")}
        </button>
      </div>

      {error && <p className="text-sm text-red-700 bg-red-50 border border-red-200 rounded-md px-3 py-1.5">{error}</p>}
      {notice && <p className="text-sm text-green-700 bg-green-50 border border-green-200 rounded-md px-3 py-1.5">{notice}</p>}

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-3 items-start">
        <div className="lg:col-span-1 bg-white rounded-lg border border-gray-200 p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            {t(lang, "home_panel_donut")}
          </p>
          <StatusDonutChart rows={statuses} selected={statusFilter} onSelect={setStatusFilter} />
        </div>

        <div className="lg:col-span-2 bg-white rounded-lg border border-gray-200 p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            {t(lang, "home_panel_monthly")}
          </p>
          <MonthlyOffersChart rows={(summary?.monthly ?? []).slice(-24)} />
        </div>

        <div className="lg:col-span-2 bg-white rounded-lg border border-gray-200 p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            {t(lang, "home_panel_ranking")}
          </p>
          <CustomerRankingChart
            rows={(summary?.ranking ?? []).slice(0, 8).map((r) => ({
              label: names[r.customer_id] ?? r.customer_id,
              count: r.count,
            }))}
          />
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <div className="overflow-auto" style={{ maxHeight: "calc(100vh - 430px)" }}>
          <table className="w-full text-xs">
            <thead className="sticky top-0 z-10">
              <tr className="bg-weber-blue text-white text-left">
                <th className="px-2 py-1.5 font-semibold">{t(lang, "home_col_number")}</th>
                <th className="px-2 py-1.5 font-semibold">{t(lang, "home_col_date")}</th>
                <th className="px-2 py-1.5 font-semibold">{t(lang, "home_col_customer")}</th>
                <th className="px-2 py-1.5 font-semibold">{t(lang, "home_col_customer_id")}</th>
                <th className="px-2 py-1.5 font-semibold">{t(lang, "home_col_status")}</th>
                <th className="px-2 py-1.5 font-semibold">{t(lang, "home_col_responsible")}</th>
                <th className="px-2 py-1.5 font-semibold">{t(lang, "home_col_language")}</th>
                <th className="px-2 py-1.5 font-semibold">{t(lang, "home_col_frequency")}</th>
                <th className="px-2 py-1.5 font-semibold">{t(lang, "home_col_hours")}</th>
                <th className="px-2 py-1.5 text-right font-semibold">{t(lang, "home_col_total")}</th>
                <th className="px-2 py-1.5 text-right font-semibold text-right">{t(lang, "home_col_actions")}</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((o, i) => (
                <tr
                  key={o.id}
                  className={`border-b border-gray-100 ${i % 2 ? "bg-gray-50" : "bg-white"} hover:bg-blue-50`}
                >
                  <td className="px-2 py-1 font-mono font-semibold text-weber-blue whitespace-nowrap">
                    {o.id_guardian_offer}
                  </td>
                  <td className="px-2 py-1 font-mono whitespace-nowrap text-gray-700">
                    {day(o.offer_date) || day(o.created_at)}
                  </td>
                  <td className="px-2 py-1 text-gray-900">{names[o.customer_id] ?? o.customer_id}</td>
                  <td className="px-2 py-1 font-mono text-gray-600 whitespace-nowrap">{o.customer_id}</td>
                  <td className="px-2 py-1">
                    <span className="px-1.5 py-0.5 rounded bg-gray-100 text-gray-700 whitespace-nowrap">
                      {o.status || "Draft"}
                    </span>
                  </td>
                  <td className="px-2 py-1 text-gray-700">{o.responsible_person ?? ""}</td>
                  <td className="px-2 py-1 text-gray-700">{o.language ?? ""}</td>
                  <td className="px-2 py-1 text-gray-700">{o.inspection_frequency ?? ""}</td>
                  <td className="px-2 py-1 text-right font-mono text-gray-700">
                    {money(o.work_hours)}
                  </td>
                  <td className="px-2 py-1 text-right font-mono font-bold whitespace-nowrap">
                    {money(o.total_end)} {o.currency ?? "EUR"}
                  </td>
                  <td className="px-2 py-1">
                    <div className="flex items-center justify-end gap-1 whitespace-nowrap">
                      <button
                        onClick={() => run(downloadOfferPdf(o.id), t(lang, "common_download"))}
                        title={t(lang, "common_download")}
                        aria-label={t(lang, "common_download")}
                        className="px-1.5 py-0.5 rounded border border-gray-300 text-gray-700 hover:bg-gray-100 inline-flex items-center justify-center"
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-3.5 h-3.5" aria-hidden="true">
                          <path d="M12 3v12" strokeLinecap="round" strokeLinejoin="round" />
                          <path d="M7 10l5 5 5-5" strokeLinecap="round" strokeLinejoin="round" />
                          <path d="M4 19h16" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </button>
                      <button
                        onClick={() => onEdit(o.id)}
                        className="px-1.5 py-0.5 rounded border border-gray-300 text-[11px] hover:bg-gray-100"
                      >
                        {t(lang, "home_edit")}
                      </button>
                      {o.status === "Finished" ? (
                        <button
                          onClick={() => run(setOfferStatus(o.id, "Draft"), t(lang, "home_updated"))}
                          className="px-1.5 py-0.5 rounded border border-gray-300 text-[11px] hover:bg-gray-100"
                        >
                          {t(lang, "home_reopen")}
                        </button>
                      ) : (
                        <button
                          onClick={() => askClose(o)}
                          className="px-1.5 py-0.5 rounded border border-gray-300 text-[11px] hover:bg-gray-100"
                        >
                          {t(lang, "home_close")}
                        </button>
                      )}
                      <button
                        onClick={() => askDelete(o)}
                        className="px-1.5 py-0.5 rounded border border-red-300 text-[11px] text-red-700 hover:bg-red-50"
                      >
                        {t(lang, "home_delete")}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {!loading && visible.length === 0 && (
                <tr>
                  <td colSpan={11} className="px-3 py-6 text-center text-gray-500">
                    {t(lang, "home_no_results")}
                  </td>
                </tr>
              )}
              {loading && (
                <tr>
                  <td colSpan={11} className="px-3 py-6 text-center text-gray-500">
                    {t(lang, "dash_loading")}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
