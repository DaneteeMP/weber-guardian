import { useCallback, useEffect, useMemo, useState } from "react";
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
import OffersDashboard from "./components/offers/OffersDashboard";
import { statusTone } from "./statusTone";
import { ToastStack, useToasts } from "./components/Toasts";
import PrintPdfModal from "./components/PrintPdfModal";
import { t, type Lang } from "./i18n";
import DataTable from "./components/DataTable";
import type { ColumnDef } from "@tanstack/react-table";

// Monitoring home: the aggregate dashboard is the default view; the full
// offer table (row actions: close, reopen, PDF, delete) lives behind the
// "List" toggle. Editing an existing offer still happens in OfferBuilder.
type OffersView = "dashboard" | "list";

const VIEW_LABEL = {
  es: { overview: "Resumen", list: "Listado" },
  en: { overview: "Overview", list: "List" },
  de: { overview: "Übersicht", list: "Liste" },
  pt: { overview: "Resumo", list: "Lista" },
  it: { overview: "Panoramica", list: "Elenco" },
} as const;
export default function OffersHome({
  lang,
  onNew,
  onEdit,
  onNewForCustomer,
}: {
  lang: Lang;
  onNew: () => void;
  onEdit: (offerId: string) => void;
  onNewForCustomer: (customerId: string) => void;
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
  const [view, setView] = useState<OffersView>("dashboard");
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
          <span className={`whitespace-nowrap rounded-md px-1.5 py-0.5 text-[12px] font-semibold leading-none ${statusTone(row.original.status)}`}>
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
                className="inline-flex items-center justify-center rounded-md border border-line-strong px-1.5 py-0.5 text-ink hover:bg-canvas"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-3.5 h-3.5" aria-hidden="true">
                  <path d="M12 3v12" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M7 10l5 5 5-5" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M4 19h16" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
              <button
                onClick={() => onEdit(o.id)}
                className="rounded-md border border-line-strong px-1.5 py-0.5 text-[11px] hover:bg-canvas"
              >
                {t(lang, "home_edit")}
              </button>
              {o.status === "Finished" ? (
                <button
                  onClick={() => run(setOfferStatus(o.id, "Pending response"), t(lang, "home_updated"))}
                  className="rounded-md border border-line-strong px-1.5 py-0.5 text-[11px] hover:bg-canvas"
                >
                  {t(lang, "home_reopen")}
                </button>
              ) : (
                <button
                  onClick={() => askClose(o)}
                  className="rounded-md border border-line-strong px-1.5 py-0.5 text-[11px] hover:bg-canvas"
                >
                  {t(lang, "home_close")}
                </button>
              )}
              <button
                onClick={() => askDelete(o)}
                className="rounded-md border border-red-200 px-1.5 py-0.5 text-[11px] text-red-700 hover:bg-red-50"
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

  const viewText = VIEW_LABEL[lang];

  return (
    <div className="flex h-full min-h-0 w-full flex-col gap-3 p-4">
      <div className="flex shrink-0 items-center gap-3">
        <h1 className="text-[22px] font-bold leading-tight text-ink">{t(lang, "home_list")}</h1>
        <div className="flex items-center rounded-lg border border-line bg-white p-0.5">
          {(["dashboard", "list"] as const).map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setView(item)}
              title={item === "dashboard" ? viewText.overview : viewText.list}
              aria-label={item === "dashboard" ? viewText.overview : viewText.list}
              aria-pressed={view === item}
              className={`inline-flex h-7 w-7 items-center justify-center rounded-md transition-colors ${
                view === item ? "bg-primary text-white" : "text-muted hover:bg-canvas"
              }`}
            >
              {item === "dashboard" ? (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-4 w-4" aria-hidden="true">
                  <rect x="3" y="3" width="7" height="7" rx="1.5" />
                  <rect x="14" y="3" width="7" height="7" rx="1.5" />
                  <rect x="3" y="14" width="7" height="7" rx="1.5" />
                  <rect x="14" y="14" width="7" height="7" rx="1.5" />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-4 w-4" aria-hidden="true">
                  <path d="M4 6h16M4 12h16M4 18h16" strokeLinecap="round" />
                </svg>
              )}
            </button>
          ))}
        </div>
        <button
          onClick={onNew}
          className="ml-auto h-9 rounded-lg border border-primary bg-primary px-3.5 text-sm font-medium text-white transition hover:bg-primary/90"
        >
          + {t(lang, "home_new")}
        </button>
      </div>

      <ToastStack toasts={toasts} onClose={dismiss} />

      {view === "dashboard" ? (
        <div className="min-h-0 flex-1 overflow-hidden">
          <OffersDashboard
            lang={lang}
            summary={summary}
            loading={loading}
            onStatusSelect={(status) => {
              setStatusFilter(status);
              setView("list");
            }}
            onOfferSelect={onEdit}
            onNewForCustomer={onNewForCustomer}
          />
        </div>
      ) : (
        <>
          <div className="flex shrink-0 flex-wrap items-center gap-3">
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t(lang, "home_search_ph")}
              className="ui-input max-w-md flex-1"
            />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="ui-input"
            >
              <option value="">{t(lang, "home_filter_all")}</option>
              {statuses.map((s) => (
                <option key={s.status} value={s.status}>
                  {s.status} ({s.count})
                </option>
              ))}
            </select>
          </div>
          <DataTable
            data={visible}
            columns={columns}
            loading={loading}
            loadingText={t(lang, "dash_loading")}
            emptyText={t(lang, "home_no_results")}
            getRowId={(o) => o.id}
            className="min-h-0 flex-1 bg-white"
            tableClassName="min-w-[1250px]"
          />
        </>
      )}

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
