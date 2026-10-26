import { Suspense, lazy, useCallback, useEffect, useMemo, useState } from "react";
import {
  closeOffer,
  deleteOffer,
  getOffersSummary,
  listAllCustomers,
  listAllOffers,
  setOfferStatus,
  type Customer,
  type OfferListItem,
  type OffersSummary,
} from "./api";
// Charts (and all of recharts) load on demand: they are hidden behind
// SHOW_CHARTS and must not weigh down the first paint.
const CustomerRankingChart = lazy(() => import("./components/charts/CustomerRankingChart"));
const MonthlyOffersChart = lazy(() => import("./components/charts/MonthlyOffersChart"));
const StatusDonutChart = lazy(() => import("./components/charts/StatusDonutChart"));
import { statusTone } from "./statusTone";
import { ToastStack, useToasts } from "./components/Toasts";
import PrintPdfModal from "./components/PrintPdfModal";
import { t, type Lang } from "./i18n";
import DataTable from "./components/DataTable";
import type { ColumnDef } from "@tanstack/react-table";

// Dense monitoring home: status/monthly/ranking panels on top, full offer table
// below with the whole scope and row actions (close, reopen, PDF, delete).
// Editing an existing offer happens in OfferBuilder, so we only pass the id.
// The charts live in components/charts; this file only feeds them.
//
// Charts are hidden for now (they add visual noise on the home screen); the
// JSX stays behind a flag so restoring them is flipping one constant.
const SHOW_CHARTS = false;
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
  // Print PDF dialog for the row's PDF action (scope/language/annexes+preview).
  const [printOfferId, setPrintOfferId] = useState<string | null>(null);
  const { toasts, push, dismiss } = useToasts();

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

  const run = useCallback(
    async (action: Promise<unknown>, message: string) => {
      setError(null);
      try {
        await action;
        setNotice(message);
        load();
      } catch (e) {
        setError(String(e));
      }
    },
    [load]
  );

  const askDelete = useCallback(
    (offer: OfferListItem) => {
      const text = t(lang, "home_confirm_delete").replace("{n}", offer.id_guardian_offer);
      if (window.confirm(text)) run(deleteOffer(offer.id), t(lang, "home_deleted"));
    },
    [lang, run]
  );

  const askClose = useCallback(
    (offer: OfferListItem) => {
      const text = t(lang, "home_confirm_close").replace("{n}", offer.id_guardian_offer);
      if (window.confirm(text)) run(closeOffer(offer.id), t(lang, "home_updated"));
    },
    [lang, run]
  );

  // Same columns as the hand-rolled table, now sortable via the shared DataTable.
  const columns = useMemo<ColumnDef<OfferListItem>[]>(
    () => [
      {
        accessorKey: "id_guardian_offer",
        header: t(lang, "home_col_number"),
        cell: ({ row }) => (
          <button
            type="button"
            onClick={() => onEdit(row.original.id)}
            title={t(lang, "home_edit")}
            className="font-mono font-semibold text-weber-blue hover:underline whitespace-nowrap"
          >
            {row.original.id_guardian_offer}
          </button>
        ),
      },
      {
        id: "date",
        accessorFn: (o) => day(o.offer_date) || day(o.created_at),
        header: t(lang, "home_col_date"),
        cell: ({ row }) => (
          <span className="font-mono whitespace-nowrap text-gray-700">
            {day(row.original.offer_date) || day(row.original.created_at)}
          </span>
        ),
      },
      {
        id: "customer",
        accessorFn: (o) => names[o.customer_id] ?? o.customer_id,
        header: t(lang, "home_col_customer"),
        cell: ({ row }) => (
          <span className="text-gray-900">{names[row.original.customer_id] ?? row.original.customer_id}</span>
        ),
      },
      {
        accessorKey: "customer_id",
        header: t(lang, "home_col_customer_id"),
        cell: ({ row }) => (
          <span className="font-mono text-gray-600 whitespace-nowrap">{row.original.customer_id}</span>
        ),
      },
      {
        accessorKey: "status",
        header: t(lang, "home_col_status"),
        cell: ({ row }) => (
          <span className={`px-1.5 py-0.5 rounded font-semibold whitespace-nowrap ${statusTone(row.original.status)}`}>
            {row.original.status || "Pending response"}
          </span>
        ),
      },
      {
        id: "responsible",
        accessorFn: (o) => o.responsible_person ?? "",
        header: t(lang, "home_col_responsible"),
        cell: ({ row }) => <span className="text-gray-700">{row.original.responsible_person ?? ""}</span>,
      },
      {
        id: "language",
        accessorFn: (o) => o.language ?? "",
        header: t(lang, "home_col_language"),
        cell: ({ row }) => <span className="text-gray-700">{row.original.language ?? ""}</span>,
      },
      {
        id: "frequency",
        accessorFn: (o) => o.inspection_frequency ?? "",
        header: t(lang, "home_col_frequency"),
        cell: ({ row }) => <span className="text-gray-700">{row.original.inspection_frequency ?? ""}</span>,
      },
      {
        id: "hours",
        accessorFn: (o) => Number(o.work_hours ?? 0),
        header: () => <span className="block text-right">{t(lang, "home_col_hours")}</span>,
        cell: ({ row }) => (
          <span className="block text-right font-mono text-gray-700">{money(row.original.work_hours)}</span>
        ),
      },
      {
        id: "total",
        accessorFn: (o) => Number(o.total_end ?? 0),
        header: () => <span className="block text-right">{t(lang, "home_col_total")}</span>,
        cell: ({ row }) => (
          <span className="block text-right font-mono font-bold whitespace-nowrap">
            {money(row.original.total_end)} {row.original.currency ?? "EUR"}
          </span>
        ),
      },
      {
        id: "actions",
        header: () => <span className="block text-right">{t(lang, "home_col_actions")}</span>,
        enableSorting: false,
        cell: ({ row }) => {
          const o = row.original;
  // Legacy banner states surface as overlay toasts, so call sites stay untouched.
  useEffect(() => {
    if (error) {
      push("error", error);
      setError(null);
    }
  }, [error, push]);
  useEffect(() => {
    if (notice) {
      push("success", notice);
      setNotice(null);
    }
  }, [notice, push]);

  return (
            <div className="flex items-center justify-end gap-1 whitespace-nowrap">
              <button
                onClick={() => setPrintOfferId(o.id)}
                title={t(lang, "mp_title")}
                aria-label={t(lang, "mp_title")}
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
                  onClick={() => run(setOfferStatus(o.id, "Pending response"), t(lang, "home_updated"))}
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
          );
        },
      },
    ],
    [lang, names, onEdit, run, askClose, askDelete]
  );

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

      <ToastStack toasts={toasts} onClose={dismiss} />

      {SHOW_CHARTS && (
        <Suspense fallback={<p className="p-3 text-sm text-gray-500">{t(lang, "dash_loading")}</p>}>
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-3 items-stretch">
          <div className="bg-white rounded-lg border border-gray-200 p-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
              {t(lang, "home_panel_donut")}
            </p>
            <StatusDonutChart rows={statuses} selected={statusFilter} onSelect={setStatusFilter} />
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
              {t(lang, "home_panel_monthly")}
            </p>
            <MonthlyOffersChart rows={(summary?.monthly ?? []).slice(-24)} />
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-3">
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
        </Suspense>
      )}

      <DataTable
        data={visible}
        columns={columns}
        loading={loading}
        loadingText={t(lang, "dash_loading")}
        emptyText={t(lang, "home_no_results")}
        getRowId={(o) => o.id}
        className="max-h-[calc(100vh-430px)] rounded-lg border-gray-200 bg-white"
        tableClassName="min-w-[1250px]"
      />

      {printOfferId && (
        <PrintPdfModal
          open
          offerId={printOfferId}
          lang={lang}
          onClose={() => setPrintOfferId(null)}
        />
      )}
    </div>
  );
}
