import { useState } from "react";
import type { CustomerOfferRow, OffersSummary } from "../../api";
import type { Lang } from "../../i18n";
import { statusTone } from "../../statusTone";
import SectionCard from "../SectionCard";

const STR = {
  es: {
    performance: "Rendimiento de ofertas",
    offers: "ofertas",
    customers: "Clientes totales",
    withOffers: "Con ofertas",
    withoutOffers: "Sin ofertas",
    pending: "Ofertas pendientes",
    realized: "Ofertas realizadas",
    monthly: "Rendimiento mensual",
    byArea: "Rendimiento por área",
    area: "Área",
    amount: "Importe",
    count: "Nº",
    ranking: "Ranking de clientes",
    statusBoard: "Estado de las ofertas",
    empty: "Sin datos",
    loading: "Cargando…",
    unknown: "Sin fecha",
    statusLabels: {
      "Pending response": "Pendiente de respuesta",
      Cancelled: "Canceladas",
      Accepted: "Aceptadas",
      "Pending Service": "Servicio pendiente",
      "In progress": "En curso",
      "Pending invoicing": "Pendiente de factura",
      Finished: "Finalizadas",
      Rejected: "Rechazadas",
    },
  },
  en: {
    performance: "Offer performance",
    offers: "offers",
    customers: "Total customers",
    withOffers: "With offers",
    withoutOffers: "Without offers",
    pending: "Pending offers",
    realized: "Realized offers",
    monthly: "Monthly performance",
    byArea: "Performance by area",
    area: "Area",
    amount: "Amount",
    count: "No.",
    ranking: "Customer ranking",
    statusBoard: "Offer status",
    empty: "No data",
    loading: "Loading…",
    unknown: "No date",
    statusLabels: {
      "Pending response": "Pending response",
      Cancelled: "Cancelled",
      Accepted: "Accepted",
      "Pending Service": "Pending service",
      "In progress": "In progress",
      "Pending invoicing": "Pending invoicing",
      Finished: "Finished",
      Rejected: "Rejected",
    },
  },
  de: {
    performance: "Angebotsleistung",
    offers: "Angebote",
    customers: "Kunden gesamt",
    withOffers: "Mit Angeboten",
    withoutOffers: "Ohne Angebote",
    pending: "Offene Angebote",
    realized: "Abgeschlossene Angebote",
    monthly: "Monatliche Leistung",
    byArea: "Leistung nach Bereich",
    area: "Bereich",
    amount: "Betrag",
    count: "Nr.",
    ranking: "Kundenranking",
    statusBoard: "Angebotsstatus",
    empty: "Keine Daten",
    loading: "Wird geladen…",
    unknown: "Ohne Datum",
    statusLabels: {
      "Pending response": "Wartet auf Antwort",
      Cancelled: "Storniert",
      Accepted: "Angenommen",
      "Pending Service": "Service ausstehend",
      "In progress": "In Bearbeitung",
      "Pending invoicing": "Rechnung ausstehend",
      Finished: "Abgeschlossen",
      Rejected: "Abgelehnt",
    },
  },
  pt: {
    performance: "Desempenho de ofertas",
    offers: "ofertas",
    customers: "Clientes totais",
    withOffers: "Com ofertas",
    withoutOffers: "Sem ofertas",
    pending: "Ofertas pendentes",
    realized: "Ofertas realizadas",
    monthly: "Desempenho mensal",
    byArea: "Desempenho por área",
    area: "Área",
    amount: "Valor",
    count: "Nº",
    ranking: "Ranking de clientes",
    statusBoard: "Estado das ofertas",
    empty: "Sem dados",
    loading: "A carregar…",
    unknown: "Sem data",
    statusLabels: {
      "Pending response": "Aguarda resposta",
      Cancelled: "Canceladas",
      Accepted: "Aceites",
      "Pending Service": "Serviço pendente",
      "In progress": "Em curso",
      "Pending invoicing": "Faturação pendente",
      Finished: "Concluídas",
      Rejected: "Rejeitadas",
    },
  },
  it: {
    performance: "Rendimento offerte",
    offers: "offerte",
    customers: "Clienti totali",
    withOffers: "Con offerte",
    withoutOffers: "Senza offerte",
    pending: "Offerte in sospeso",
    realized: "Offerte realizzate",
    monthly: "Rendimento mensile",
    byArea: "Rendimento per area",
    area: "Area",
    amount: "Importo",
    count: "N.",
    ranking: "Classifica clienti",
    statusBoard: "Stato delle offerte",
    empty: "Nessun dato",
    loading: "Caricamento…",
    unknown: "Senza data",
    statusLabels: {
      "Pending response": "In attesa di risposta",
      Cancelled: "Annullate",
      Accepted: "Accettate",
      "Pending Service": "Servizio in sospeso",
      "In progress": "In corso",
      "Pending invoicing": "In attesa di fatturazione",
      Finished: "Completate",
      Rejected: "Rifiutate",
    },
  },
} as const;

function money(lang: Lang, value: string | number): string {
  return Number(value ?? 0).toLocaleString(lang, {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function dateLabel(lang: Lang, value: string | null | undefined): string {
  if (!value) return "";
  const parsed = new Date(`${value.slice(0, 10)}T00:00:00`);
  return Number.isNaN(parsed.getTime())
    ? value.slice(0, 10)
    : parsed.toLocaleDateString(lang, { day: "2-digit", month: "2-digit", year: "numeric" });
}

function monthLabel(lang: Lang, value: string, unknown: string): string {
  if (value === "unknown") return unknown;
  const [year, month] = value.split("-").map(Number);
  if (!year || !month) return value;
  return new Date(Date.UTC(year, month - 1, 1)).toLocaleDateString(lang, { month: "long" });
}

function MetricList({
  title,
  total,
  rows,
  empty,
  onSelect,
}: {
  title: string;
  total: number;
  rows: CustomerOfferRow[];
  empty: string;
  onSelect: (row: CustomerOfferRow) => void;
}) {
  return (
    <div className="flex min-h-0 min-w-0 flex-col">
      <div className="flex items-baseline justify-between gap-2">
        <h3 className="text-[13px] font-medium text-ink">{title}</h3>
        <span className="text-lg font-semibold leading-none text-primary">{total}</span>
      </div>
      <div className="mt-2 min-h-0 flex-1 overflow-auto rounded-lg border border-line">
        {rows.length === 0 ? (
          <p className="p-3 text-xs text-muted">{empty}</p>
        ) : (
          rows.slice(0, 12).map((row) => (
            <button
              key={row.customer_id}
              type="button"
              title={row.account_name}
              onClick={() => onSelect(row)}
              className="flex w-full items-center gap-2 border-b border-soft px-2.5 py-1.5 text-left last:border-0 hover:bg-canvas"
            >
              <span className="min-w-0 flex-1 truncate text-[12px] text-ink">{row.account_name}</span>
              <span className="shrink-0 font-mono text-[11px] text-muted">{row.count}</span>
            </button>
          ))
        )}
      </div>
    </div>
  );
}

function CustomerPanel({
  lang,
  summary,
  onOpenOffer,
  onNewOffer,
}: {
  lang: Lang;
  summary: OffersSummary;
  onOpenOffer: (offerId: string) => void;
  onNewOffer: (customerId: string) => void;
}) {
  const text = STR[lang];
  const [mode, setMode] = useState<"with" | "without">("without");
  const rows = mode === "with" ? summary.customers : summary.customers_without_offers;
  const tab = (active: boolean) =>
    `rounded-md px-1 py-1 text-[11px] font-medium transition-colors ${
      active ? "bg-white text-primary" : "text-muted hover:text-ink"
    }`;

  return (
    <div className="flex min-h-0 min-w-0 flex-col">
      <div className="flex items-baseline justify-between gap-2">
        <h3 className="text-[13px] font-medium text-ink">{text.customers}</h3>
        <span className="text-lg font-semibold leading-none text-primary">{summary.customers_total}</span>
      </div>
      <div className="mt-2 grid grid-cols-2 gap-1 rounded-lg border border-line bg-canvas p-0.5">
        <button type="button" onClick={() => setMode("with")} className={tab(mode === "with")}>
          {text.withOffers} ({summary.customers_with_offers_total})
        </button>
        <button type="button" onClick={() => setMode("without")} className={tab(mode === "without")}>
          {text.withoutOffers} ({summary.customers_without_offers_total})
        </button>
      </div>
      <div className="mt-2 min-h-0 flex-1 overflow-auto rounded-lg border border-line">
        {rows.length === 0 ? (
          <p className="p-3 text-xs text-muted">{text.empty}</p>
        ) : (
          rows.map((row) =>
            mode === "with" ? (
              <button
                key={row.customer_id}
                type="button"
                title={row.account_name}
                onClick={() => row.last_offer_id && onOpenOffer(row.last_offer_id)}
                className="flex w-full items-center gap-2 border-b border-soft px-2.5 py-1.5 text-left last:border-0 hover:bg-canvas"
              >
                <span className="min-w-0 flex-1 truncate text-[12px] text-ink">{row.account_name}</span>
                <span className="shrink-0 font-mono text-[11px] text-muted">{row.count}</span>
              </button>
            ) : (
              <button
                key={row.customer_id}
                type="button"
                title={`${row.account_name} — ${text.withoutOffers}`}
                onClick={() => onNewOffer(row.customer_id)}
                className="block w-full border-b border-soft px-2.5 py-1.5 text-left last:border-0 hover:bg-canvas"
              >
                <span className="block truncate text-[12px] text-ink">{row.account_name}</span>
              </button>
            )
          )
        )}
      </div>
    </div>
  );
}

function MonthlyBars({
  lang,
  rows,
  empty,
}: {
  lang: Lang;
  rows: OffersSummary["monthly"];
  empty: string;
}) {
  const text = STR[lang];
  const visible = rows.slice(-8);
  const max = Math.max(1, ...visible.map((row) => row.count));
  return (
    <div className="min-w-0">
      <p className="ui-sec">{text.monthly}</p>
      {visible.length === 0 ? (
        <p className="text-xs text-muted">{empty}</p>
      ) : (
        <div className="space-y-1.5">
          {visible.map((row) => (
            <div key={row.month} className="flex items-center gap-2 text-[11.5px]">
              <span className="w-16 shrink-0 capitalize text-muted">
                {monthLabel(lang, row.month, text.unknown)}
              </span>
              <div className="h-2 min-w-0 flex-1 rounded-full bg-[#eef2f7]">
                <div
                  className="h-full rounded-full bg-primary"
                  style={{ width: `${Math.max(4, (row.count / max) * 100)}%` }}
                />
              </div>
              <span className="w-6 shrink-0 text-right font-mono font-semibold text-ink">{row.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Ranking({
  lang,
  rows,
  empty,
  onSelect,
}: {
  lang: Lang;
  rows: CustomerOfferRow[];
  empty: string;
  onSelect: (offerId: string) => void;
}) {
  const text = STR[lang];
  return (
    <div className="flex min-h-0 min-w-0 flex-col">
      <p className="ui-sec">{text.ranking}</p>
      {rows.length === 0 ? (
        <p className="text-xs text-muted">{empty}</p>
      ) : (
        <div className="min-h-0 flex-1 space-y-0.5 overflow-auto">
          {rows.slice(0, 10).map((row) => (
            <button
              key={row.customer_id}
              type="button"
              title={row.account_name}
              onClick={() => row.last_offer_id && onSelect(row.last_offer_id)}
              className="flex w-full items-start gap-2 rounded-md px-2 py-1 text-left hover:bg-canvas"
            >
              <span className="min-w-0 flex-1">
                <span className="block truncate text-[12px] text-ink">{row.account_name}</span>
                <span className="mt-0.5 flex flex-wrap items-center gap-1.5 text-[10px] text-muted">
                  <span className="shrink-0 font-mono">{money(lang, row.total_end)}</span>
                  {row.last_offer_date && <span>· {dateLabel(lang, row.last_offer_date)}</span>}
                  {row.last_status && row.last_status !== "Finished" && (
                    <span
                      className={`max-w-28 truncate rounded px-1 py-[1px] text-[9px] font-semibold leading-none ${statusTone(row.last_status)}`}
                    >
                      {text.statusLabels[row.last_status as keyof typeof text.statusLabels] ?? row.last_status}
                    </span>
                  )}
                </span>
              </span>
              <span className="shrink-0 pt-0.5 font-mono text-[12px] font-semibold text-primary">
                {row.count}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function StatusColumn({
  lang,
  row,
  onStatus,
  onOfferSelect,
}: {
  lang: Lang;
  row: OffersSummary["status_details"][number];
  onStatus: (status: string) => void;
  onOfferSelect: (offerId: string) => void;
}) {
  const text = STR[lang];
  const label = text.statusLabels[row.status as keyof typeof text.statusLabels] ?? row.status;
  return (
    <div className="flex min-h-0 min-w-0 flex-col rounded-xl border border-line bg-white p-3">
      <button
        type="button"
        title={label}
        onClick={() => onStatus(row.status)}
        className="flex w-full items-baseline justify-between gap-2 text-left"
      >
        <span className="min-w-0 truncate text-[12px] font-semibold text-ink">{label}</span>
        <span className="shrink-0 text-lg font-semibold leading-none text-primary">{row.count}</span>
      </button>
      <div className="mt-1 font-mono text-[12px] font-semibold text-muted">
        {row.count === 0 ? "—" : money(lang, row.total_end)}
      </div>
      <div className="mt-2 min-h-0 flex-1 overflow-auto border-t border-soft pt-1.5">
        {row.customers.length === 0 ? (
          <p className="py-1 text-[11px] text-muted">—</p>
        ) : (
          row.customers.slice(0, 8).map((customer) => (
            <div key={customer.customer_id} className="flex items-baseline justify-between gap-2 py-0.5 text-[11px]">
              <button
                type="button"
                title={customer.account_name}
                onClick={() => customer.last_offer_id && onOfferSelect(customer.last_offer_id)}
                className="min-w-0 truncate text-left text-ink hover:text-primary"
              >
                {customer.account_name}
              </button>
              <span className="shrink-0 font-mono text-[10px] text-muted">
                {dateLabel(lang, customer.last_offer_date)}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default function OffersDashboard({
  lang,
  summary,
  loading,
  onStatusSelect,
  onOfferSelect,
  onNewForCustomer,
}: {
  lang: Lang;
  summary: OffersSummary | null;
  loading: boolean;
  onStatusSelect: (status: string) => void;
  onOfferSelect: (offerId: string) => void;
  onNewForCustomer: (customerId: string) => void;
}) {
  const text = STR[lang];
  if (!summary) {
    return (
      <SectionCard title={text.performance}>
        <p className="p-4 text-sm text-muted">{loading ? text.loading : text.empty}</p>
      </SectionCard>
    );
  }

  return (
    <div className="flex h-full min-h-0 flex-col gap-3">
      <SectionCard
        title={text.performance}
        subtitle={`${summary.total} ${text.offers}`}
        className="flex min-h-0 flex-1 flex-col"
      >
        <div className="grid min-h-0 flex-1 gap-5 overflow-y-auto md:grid-cols-2 xl:grid-cols-[1.05fr_1.05fr_1.05fr_1.25fr_1.35fr] xl:overflow-hidden">
          <CustomerPanel
            lang={lang}
            summary={summary}
            onOpenOffer={onOfferSelect}
            onNewOffer={onNewForCustomer}
          />
          <MetricList
            title={text.pending}
            total={summary.pending_total}
            rows={summary.pending_customers}
            empty={text.empty}
            onSelect={(row) => row.last_offer_id && onOfferSelect(row.last_offer_id)}
          />
          <MetricList
            title={text.realized}
            total={summary.realized_total}
            rows={summary.realized_customers}
            empty={text.empty}
            onSelect={(row) => row.last_offer_id && onOfferSelect(row.last_offer_id)}
          />
          <div className="flex min-h-0 min-w-0 flex-col overflow-y-auto">
            <MonthlyBars lang={lang} rows={summary.monthly} empty={text.empty} />
          </div>
          <Ranking
            lang={lang}
            rows={summary.ranking}
            empty={text.empty}
            onSelect={onOfferSelect}
          />
        </div>
      </SectionCard>

      <SectionCard title={text.statusBoard} className="flex min-h-0 flex-1 flex-col">
        <div className="grid min-h-0 flex-1 gap-3 overflow-y-auto sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 xl:overflow-hidden">
          {summary.status_details.map((row) => (
            <StatusColumn
              key={row.status}
              lang={lang}
              row={row}
              onStatus={onStatusSelect}
              onOfferSelect={onOfferSelect}
            />
          ))}
        </div>
      </SectionCard>
    </div>
  );
}
