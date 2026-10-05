import { useEffect, useMemo, useRef, useState } from "react";
import { type ColumnDef } from "@tanstack/react-table";
import {
  calculate,
  closeOffer,
  createOffer,
  deleteOffer,
  downloadOfferPdf,
  getCustomerDetail,
  getOffer,
  getPrices,
  listAllCustomers,
  listOffers,
  maintenanceDraft,
  updateOffer,
  type Breakdown,
  type Customer,
  type CustomerDetail,
  type Equipment,
  type OfferListItem,
} from "./api";
import FieldRow from "./components/FieldRow";
import DataTable from "./components/DataTable";
import SectionCard from "./components/SectionCard";
import { quoteLinesFromDraft, type CatalogQuoteLine } from "./catalogLines";
import { t, type Lang } from "./i18n";

const num = (v: string, fallback: number) => {
  const n = Number(v);
  return Number.isFinite(n) && n >= 0 ? n : fallback;
};

// ISO day (yyyy-mm-dd) for <input type="date">. Built from local parts, not
// toISOString, which would shift the day for any timezone behind UTC.
const todayIso = () => {
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
};

const GUARDIAN_TYPES = ["Basic Kit", "Audit", "Off-Guardian", "Campaign"];
const LANGUAGES = ["Spanish", "Portuguese"];
const FREQUENCIES = ["Annual", "Semi-annual", "Biennial"];
const STATUSES = ["Draft", "Pending response", "Finished", "Cancelled", "Rejected"];
const RESPONSIBLES = ["", "Xevi Mira", "David"];

type OfferTableRow = {
  id: string;
  pos: number;
  equipment: string;
  module: string;
  amount: number;
  catalogWarning?: CatalogQuoteLine["catalogWarning"];
};

// Create or edit one offer. With editingOfferId the form is filled from the
// stored offer (header, lines and the hour snapshot the offer keeps).
export default function OfferBuilder({
  lang,
  editingOfferId,
  onDone,
}: {
  lang: Lang;
  editingOfferId: string | null;
  onDone: () => void;
}) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customerId, setCustomerId] = useState("");
  const [clientSearch, setClientSearch] = useState("");
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [customerDetail, setCustomerDetail] = useState<CustomerDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState<string | null>(null);
  const [calc, setCalc] = useState<Breakdown | null>(null);

  const [reportHours, setReportHours] = useState("0");
  const [tripBase, setTripBase] = useState("0");
  const km = "0";
  const [kmRate, setKmRate] = useState("0");
  const [techRate, setTechRate] = useState("0");
  const [dietFull, setDietFull] = useState("0");
  const [dietHalf, setDietHalf] = useState("0");
  const [hotelRate, setHotelRate] = useState("0");
  const [offerNumber, setOfferNumber] = useState("");
  const [offerDate, setOfferDate] = useState(todayIso());
  const [language, setLanguage] = useState("Spanish");
  const [frequency, setFrequency] = useState("Annual");
  const [status, setStatus] = useState("Pending response");
  const [responsible, setResponsible] = useState("");
  const [guardianType, setGuardianType] = useState("Audit");
  const [comments, setComments] = useState("");
  type QuoteLine = CatalogQuoteLine;
  const [items, setItems] = useState<QuoteLine[]>([]);
  const [offers, setOffers] = useState<OfferListItem[]>([]);
  const [savedOffer, setSavedOffer] = useState<{ id: string; status: string } | null>(null);
  const [equipList, setEquipList] = useState<Equipment[]>([]);
  const [equipmentLoading, setEquipmentLoading] = useState(false);
  const [selectedEquip, setSelectedEquip] = useState<string[]>([]);
  const [editStatus, setEditStatus] = useState<string | null>(null);

  // The selected component workloads are the authoritative work-hours input
  // for the existing offer pricing engine; no manual work-hours box is needed.
  const workHours = useMemo(
    () => items.reduce((sum, item) => sum + num(item.workload, 0), 0).toFixed(2),
    [items],
  );

  // Edit mode: fill the form from the stored offer. Trip inputs (km, rates)
  // are not part of the offer snapshot on purpose: they come from the current
  // subsidiary rates, same as when the offer is created.
  useEffect(() => {
    if (!editingOfferId) return;
    getOffer(editingOfferId)
      .then((o) => {
        setCustomerId(o.customer_id);
        setOfferNumber(o.id_guardian_offer);
        // The API always returns a date; fall back to today only if an old row
        // somehow has no business date at all.
        setOfferDate(o.offer_date || todayIso());
        setStatus(o.status || "Draft");
        setLanguage(o.language || "Spanish");
        setFrequency(o.inspection_frequency || "Annual");
        setResponsible(o.responsible_person || "");
        setComments(o.general_comments || "");
        setReportHours(String(Number(o.report_hours ?? 0)));
        setTripBase(String(Number(o.trip_hours ?? 0)));
        setItems(
          o.items.map((i) => ({
            equipment: i.equipment ?? "",
            description: i.description ?? "",
            import_amount: String(Number(i.import_amount ?? 0)),
            workload: String(Number(i.workload ?? 0)),
          }))
        );
        setEditStatus(o.status || "Draft");
      })
      .catch((e) => setError(String(e)));
  }, [editingOfferId]);

  const equipmentCodes = useMemo(
    () => [...new Set(equipList.map((row) => row.equipment_name).filter((name): name is string => !!name))].sort(),
    [equipList],
  );
  const componentCounts = useMemo(() => {
    const counts = new Map<string, number>();
    for (const row of equipList) {
      if (row.equipment_name) counts.set(row.equipment_name, (counts.get(row.equipment_name) ?? 0) + 1);
    }
    return counts;
  }, [equipList]);

  function toggleEquip(code: string) {
    setSelectedEquip((p) => (p.includes(code) ? p.filter((c) => c !== code) : [...p, code]));
  }

  // Picker drives the quote directly: selecting a machine expands ALL its
  // component rows into lines; deselecting removes the lines it added.
  // Hand-typed lines are never touched. The updater below is pure (reads
  // only closed-over snapshots) so React StrictMode double-invoking it
  // cannot duplicate rows.
  const autoLines = useRef<Set<string>>(new Set());
  const prevSelected = useRef<string[]>([]);
  const selectedEquipRef = useRef(selectedEquip);
  selectedEquipRef.current = selectedEquip;

  const lineKey = (equipment: string, description: string) =>
    `${equipment}||${description}`;

  useEffect(() => {
    const prev = prevSelected.current;
    const added = selectedEquip.filter((c) => !prev.includes(c));
    const removed = prev.filter((c) => !selectedEquip.includes(c));

    prevSelected.current = selectedEquip;

    if (added.length === 0 && removed.length === 0) return;

    // Remove automatically generated lines belonging to machines that
    // have just been deselected. Hand-entered lines are left untouched.
    if (removed.length > 0) {
      const removedKeys = new Set<string>();

      for (const code of removed) {
        for (const key of autoLines.current) {
          if (key.startsWith(`${code}||`)) {
            removedKeys.add(key);
          }
        }
      }

      autoLines.current = new Set(
        [...autoLines.current].filter((key) => !removedKeys.has(key))
      );

      if (removedKeys.size > 0) {
        setItems((lines) =>
          lines.filter(
            (line) => !removedKeys.has(lineKey(line.equipment, line.description))
          )
        );
      }
    }

    if (added.length === 0 || !customerId) return;

    async function loadDraft(): Promise<void> {
      const draft = await maintenanceDraft(customerId, added);

      if (!selectedEquipRef.current.some((code) => added.includes(code))) {
        return;
      }

      const desired = new Map<string, CatalogQuoteLine>();
      for (const line of quoteLinesFromDraft(draft.rows)) {
        if (selectedEquipRef.current.includes(line.equipment)) {
          desired.set(lineKey(line.equipment, line.description), line);
        }
      }

      for (const key of desired.keys()) {
        autoLines.current.add(key);
      }

      setItems((lines) => {
        const have = new Set(
          lines.map((line) => lineKey(line.equipment, line.description))
        );

        const fresh = [...desired.entries()]
          .filter(([key]) => !have.has(key))
          .map(([, line]) => line);

        return [...lines, ...fresh];
      });
    }

    void loadDraft().catch((e) => {
      setError(e instanceof Error ? e.message : String(e));
    });
  }, [selectedEquip, equipList, customerId]);

  // Load the full in-scope customer list once; filial-specific rates are
  // loaded alongside the selected customer's fleet below.
  useEffect(() => {
    listAllCustomers().then(setCustomers).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    let active = true;
    const selectedCustomer = customers.find((c) => c.customer_id === customerId) ?? null;
    setCustomer(selectedCustomer);
    setSavedOffer(null);
    if (customerId) {
      setEquipmentLoading(true);
      setCustomerDetail(null);
      setEquipList([]);
      setSelectedEquip([]);
      setKmRate("0");
      setTechRate("0");
      setDietFull("0");
      setDietHalf("0");
      setHotelRate("0");
      listOffers(customerId).then(setOffers).catch(() => setOffers([]));
      if (selectedCustomer?.subsidiary_id) {
        getPrices(selectedCustomer.subsidiary_id)
          .then((prices) => {
            if (!active) return;
            setKmRate(prices.km_rate);
            setTechRate(prices.tech_rate);
            setDietFull(prices.diet_full_rate);
            setDietHalf(prices.diet_half_rate);
            setHotelRate(prices.hotel_rate);
          })
          .catch((e) => {
            if (active) setError(e instanceof Error ? e.message : String(e));
          });
      }
      getCustomerDetail(customerId)
        .then((detail) => {
          if (!active) return;
          setCustomerDetail(detail);
          const sitesById = new Map(detail.sites.map((site) => [site.id, site]));
          const equipmentRows: Equipment[] = detail.machines.flatMap((machine) =>
            machine.components.map((component, index) => ({
              id: `${machine.equipment_name}:${component.material_no ?? index}`,
              customer_id: detail.customer.customer_id,
              equipment_name: machine.equipment_name,
              machine_type: machine.machine_type,
              component_type: component.component_type,
              material_no: component.material_no,
              purchase_date: component.purchase_date,
              site: machine.site_id ? sitesById.get(machine.site_id) ?? null : null,
            })),
          );
          setEquipList(equipmentRows);
          setSelectedEquip([]);
          setEquipmentLoading(false);
        })
        .catch(() => {
          if (!active) return;
          setCustomerDetail(null);
          setEquipList([]);
          setSelectedEquip([]);
          setEquipmentLoading(false);
        });
    } else {
      setOffers([]);
      setCustomerDetail(null);
      setEquipList([]);
      setSelectedEquip([]);
      setEquipmentLoading(false);
    }
    return () => {
      active = false;
    };
  }, [customerId, customers]);

  // Picking the customer clears the saved offer, so in edit mode we re-attach
  // it once the customer is in place.
  useEffect(() => {
    if (editingOfferId && editStatus && customerId) {
      setSavedOffer({ id: editingOfferId, status: editStatus });
    }
  }, [editStatus, customerId, editingOfferId]);

  const filteredCustomers = useMemo(() => {
    const q = clientSearch.trim().toLowerCase();
    if (!q) return customers;
    return customers.filter(
      (c) =>
        c.account_name.toLowerCase().includes(q) ||
        c.customer_id.toLowerCase().includes(q) ||
        (c.country ?? "").toLowerCase().includes(q)
    );
  }, [customers, clientSearch]);

  // Live preview: authoritative breakdown comes from the backend on every input change.
  useEffect(() => {
    const timer = setTimeout(() => {
      calculate({
        work_hours: num(workHours, 0),
        bk_hours: 0,
        report_hours: num(reportHours, 0),
        trip_hours_base: num(tripBase, 0),
        km: num(km, 0),
        km_rate: num(kmRate, 0),
        tech_rate: num(techRate, 0),
        diet_full_rate: num(dietFull, 0),
        diet_half_rate: num(dietHalf, 0),
        hotel_rate: num(hotelRate, 0),
        discount_rate: 0.15,
        bk_price: 0,
        currency: "EUR",
      })
        .then(setCalc)
        .catch((e) => setError(String(e)));
    }, 300);
    return () => clearTimeout(timer);
  }, [workHours, reportHours, tripBase, km, kmRate, techRate, dietFull, dietHalf, hotelRate]);

  async function refreshOffers() {
    if (customerId) {
      await listOffers(customerId).then(setOffers).catch(() => {});
    }
  }

  async function handleSave() {
    setError(null);
    setSaved(null);
    try {
      if (!customerId) throw new Error(t(lang, "ob_select_first"));
      if (items.some((item) => item.catalogWarning)) throw new Error(t(lang, "ob_resolve_module"));
      const pricing = {
        work_hours: num(workHours, 0),
        bk_hours: 0,
        report_hours: num(reportHours, 0),
        trip_hours_base: num(tripBase, 0),
        km: num(km, 0),
        km_rate: num(kmRate, 0),
        tech_rate: num(techRate, 0),
        diet_full_rate: num(dietFull, 0),
        diet_half_rate: num(dietHalf, 0),
        hotel_rate: num(hotelRate, 0),
        discount_rate: 0.15,
        bk_price: 0,
        currency: "EUR",
      };
      const lines = items.map((i) => ({
        equipment: i.equipment || undefined,
        description: i.description || undefined,
        import_amount: num(i.import_amount, 0),
        workload: num(i.workload, 0),
      }));
      if (editingOfferId) {
        await updateOffer(editingOfferId, {
          status,
          responsible_person: responsible || undefined,
          language,
          inspection_frequency: frequency,
          general_comments: comments || undefined,
          offer_date: offerDate || undefined,
          pricing,
          items: lines,
        });
        setEditStatus(status);
        setSavedOffer({ id: editingOfferId, status });
      } else {
        const created = await createOffer({
          customer_id: customerId,
          id_guardian_offer: offerNumber || undefined,
          status,
          responsible_person: responsible || undefined,
          language,
          inspection_frequency: frequency,
          general_comments: comments || undefined,
          offer_date: offerDate || undefined,
          pricing,
          items: lines,
        });
        setOfferNumber(created.id_guardian_offer);
        setSavedOffer({ id: created.id, status });
      }
      setSaved(t(lang, "ob_saved"));
      await refreshOffers();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    }
  }

  async function handleDelete() {
    if (!savedOffer) return;
    setError(null);
    try {
      await deleteOffer(savedOffer.id);
      setSavedOffer(null);
      setSaved(null);
      await refreshOffers();
      onDone();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    }
  }

  async function handleClose() {
    if (!savedOffer) return;
    setError(null);
    try {
      const closed = await closeOffer(savedOffer.id);
      setSavedOffer({ id: savedOffer.id, status: closed.status ?? "Finished" });
      setStatus("Finished");
      await refreshOffers();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Close failed");
    }
  }

  async function handlePrint() {
    if (!savedOffer) return;
    setError(null);
    try {
      await downloadOfferPdf(savedOffer.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Print failed");
    }
  }

  const input = "border rounded px-2 py-1.5 text-sm w-full";
  const eur = (v: string | number | null | undefined) =>
    `${Number(v ?? 0).toLocaleString("en-GB", { minimumFractionDigits: 2 })} €`;

  const moduleRows: OfferTableRow[] = items.map((item, index) => ({
    id: `${index}:${lineKey(item.equipment, item.description)}`,
    pos: index + 1,
    equipment: item.equipment,
    module: item.description,
    amount: num(item.import_amount, 0),
    catalogWarning: item.catalogWarning,
  }));

  const moduleColumns = useMemo<ColumnDef<OfferTableRow>[]>(
    () => [
      {
        accessorKey: "pos",
        header: t(lang, "ob_col_pos"),
        size: 48,
      },
      {
        accessorKey: "equipment",
        header: t(lang, "ob_col_equipment"),
        cell: ({ getValue }) => <span className="font-semibold">{String(getValue())}</span>,
      },
      {
        accessorKey: "module",
        header: t(lang, "ob_col_module"),
        cell: ({ row }) => (
          <span>
            {row.original.module}
            {row.original.catalogWarning && (
              <span className="ml-2 rounded bg-amber-100 px-1.5 py-0.5 text-[10px] text-amber-800">
                {t(lang, row.original.catalogWarning === "unconfirmed" ? "ob_unconfirmed" : "ob_unpriced")}
              </span>
            )}
          </span>
        ),
      },
      {
        accessorKey: "amount",
        header: () => <span className="block text-right">{t(lang, "ob_col_amount")}</span>,
        cell: ({ getValue }) => <span className="block text-right font-mono">{eur(Number(getValue()))}</span>,
      },
    ],
    [lang],
  );

  return (
    <div className="flex h-full min-h-0 flex-col bg-slate-100 text-slate-800">
      <div className="flex shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4 py-2 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-weber-blue text-white grid place-items-center font-bold">W</div>
          <h1 className="text-lg font-bold tracking-tight text-slate-900">Guardian Offers</h1>
          {editingOfferId && (
            <span className="text-sm text-slate-500">
              {t(lang, "ob_editing")} {offerNumber}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrint}
            disabled={!savedOffer}
            title={t(lang, "ob_print")}
            aria-label={t(lang, "ob_print")}
            className="px-3 py-1.5 border border-blue-200 bg-blue-50 text-blue-900 hover:bg-blue-100 rounded text-xs font-semibold disabled:opacity-40 inline-flex items-center justify-center gap-1.5"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} className="w-4 h-4" aria-hidden="true">
              <path d="M7 8V3h10v5M7 17H5a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M7 14h10v7H7z" strokeLinejoin="round" />
              <path d="M17 11h.01" strokeLinecap="round" />
            </svg>
            {t(lang, "ob_print")}
          </button>
          <button
            onClick={handleSave}
            disabled={!customerId}
            className="px-3 py-1.5 border border-blue-200 bg-blue-50 text-blue-900 hover:bg-blue-100 rounded text-xs font-semibold disabled:opacity-40"
          >
            {editingOfferId ? t(lang, "ob_update") : t(lang, "ob_save")}
          </button>
          <button onClick={handleDelete} disabled={!savedOffer} className="px-3 py-1.5 border border-blue-200 bg-blue-50 text-blue-900 hover:bg-blue-100 rounded text-xs font-semibold disabled:opacity-40">
            {t(lang, "ob_delete_offer")}
          </button>
          <button onClick={handleClose} disabled={!savedOffer} className="px-3 py-1.5 border border-blue-200 bg-blue-50 text-blue-900 hover:bg-blue-100 rounded text-xs font-semibold disabled:opacity-40">
            {t(lang, "ob_close_offer")}
          </button>
          <button onClick={onDone} className="px-3 py-1.5 border border-slate-200 bg-white hover:bg-slate-50 rounded text-xs font-semibold">
            {t(lang, "ob_back")}
          </button>
        </div>
      </div>

      <div className="flex min-h-0 flex-1">
        <aside className="hidden min-h-0 w-[260px] shrink-0 flex-col border-r border-slate-200 bg-white lg:flex">
          <div className="p-3 pb-2">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-sm font-bold text-slate-800">{t(lang, "nav_customers")}</h2>
              <span className="text-xs text-slate-500">{customers.length}</span>
            </div>
            <input
              value={clientSearch}
              onChange={(e) => setClientSearch(e.target.value)}
              placeholder={t(lang, "cust_search_ph")}
              className={`${input} border-slate-300`}
            />
          </div>
          <div className="flex-1 min-h-0 overflow-y-auto px-2 pb-3">
            {filteredCustomers.map((c) => {
              const selected = c.customer_id === customerId;
              return (
                <button
                  key={c.customer_id}
                  type="button"
                  onClick={() => setCustomerId(c.customer_id)}
                  className={`w-full text-left rounded-md border-l-[3px] px-2.5 py-2 mb-1 transition-colors ${
                    selected
                      ? "border-weber-blue bg-blue-50 text-slate-900"
                      : "border-transparent hover:bg-slate-50 text-slate-700"
                  }`}
                >
                  <span className="block text-xs font-semibold truncate">{c.account_name}</span>
                  <span className="block text-[11px] text-slate-500 truncate">
                    {[c.city, c.province, c.country].filter(Boolean).join(", ") || c.customer_id}
                  </span>
                  {selected && offers.length > 0 && (
                    <span className="mt-1 inline-block rounded-full bg-blue-100 px-1.5 py-0.5 text-[10px] font-semibold text-blue-900">
                      {offers.length} {t(lang, "ob_client_offers")}
                    </span>
                  )}
                </button>
              );
            })}
            {filteredCustomers.length === 0 && (
              <p className="px-2 py-5 text-center text-xs text-slate-400">{t(lang, "home_no_results")}</p>
            )}
          </div>
        </aside>

      <main className="flex min-h-0 min-w-0 flex-1 flex-col gap-2 overflow-hidden p-2">
        {error && <p className="text-sm text-red-600 bg-white rounded-lg shadow p-3">{error}</p>}
        {saved && <p className="text-sm text-green-700 bg-white rounded-lg shadow p-3">{saved}</p>}

        <div className="shrink-0 rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
          <div className="grid grid-cols-12 gap-4">
            <div className="col-span-5 border-r border-slate-200 pr-4">
              <div className="text-xs font-bold text-weber-blue uppercase mb-2">{t(lang, "ob_customer_data")}</div>
              <select
                value={customerId}
                onChange={(e) => setCustomerId(e.target.value)}
                className={`${input} mb-2 lg:hidden bg-blue-50`}
              >
                <option value="">{t(lang, "ob_select_client")}</option>
                {customers.map((c) => (
                  <option key={c.customer_id} value={c.customer_id}>
                    {c.customer_id} {c.account_name}
                  </option>
                ))}
              </select>
              {customer ? (
                <div className="rounded border border-slate-200 bg-white p-2.5 text-sm min-h-[84px]">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="rounded border border-slate-200 bg-slate-50 px-2 py-1 font-mono text-xs">{customer.customer_id}</span>
                    <span className="font-bold">{customer.account_name}</span>
                  </div>
                  <div className="text-slate-700">
                    {customerDetail?.sites.length ? (
                      customerDetail.sites.map((site) => (
                        <div key={site.id}>
                          {[
                            site.physical_street,
                            [site.physical_postal_code, site.physical_city].filter(Boolean).join(" "),
                            site.physical_province,
                            site.physical_country,
                          ].filter(Boolean).join(", ")}
                        </div>
                      ))
                    ) : (
                      [customer.city, customer.province, customer.country].filter(Boolean).join(", ") || "—"
                    )}
                  </div>
                </div>
              ) : (
                <div className="rounded border border-dashed border-slate-300 p-3 text-sm text-slate-400 min-h-[84px]">
                  {t(lang, "ob_select_client")}
                </div>
              )}
            </div>

            <div className="col-span-4 border-r border-slate-200 pr-4">
              <div className="space-y-1.5 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 w-28">{t(lang, "ob_offer_no")}</span>
                  <span className="font-mono font-bold">{offerNumber || savedOffer?.id.slice(0, 8) || "-"}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 w-28">{t(lang, "ob_offer_date")}</span>
                  <input
                    type="date"
                    value={offerDate}
                    onChange={(e) => setOfferDate(e.target.value)}
                    className="border rounded px-1 py-0.5 text-sm font-mono"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 w-28">{t(lang, "ob_guardian_type")}</span>
                  <select value={guardianType} onChange={(e) => setGuardianType(e.target.value)} className="border rounded px-1 py-0.5 text-sm bg-blue-50">
                    {GUARDIAN_TYPES.map((g) => (
                      <option key={g}>{g}</option>
                    ))}
                  </select>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 w-28">{t(lang, "ob_offer_no_save")}</span>
                  <input
                    value={offerNumber}
                    onChange={(e) => setOfferNumber(e.target.value)}
                    placeholder="W-02-2026-0001"
                    readOnly={!!editingOfferId}
                    className={`border rounded px-1 py-0.5 text-sm font-mono ${editingOfferId ? "bg-gray-100 text-gray-500" : ""}`}
                  />
                </div>
                {editingOfferId && (
                  <p className="text-[11px] text-gray-500 leading-snug">{t(lang, "ob_pricing_note")}</p>
                )}
              </div>
            </div>

            <div className="col-span-3 space-y-1.5 text-sm">
              <div className="text-xs font-bold text-weber-blue uppercase mb-2">{t(lang, "ob_options")}</div>
              <div className="flex items-center gap-2">
                <span className="text-gray-500">{t(lang, "ob_language")}</span>
                <select value={language} onChange={(e) => setLanguage(e.target.value)} className="border rounded px-1 py-0.5 text-sm bg-blue-50">
                  {LANGUAGES.map((l) => (
                    <option key={l}>{l}</option>
                  ))}
                </select>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-500">{t(lang, "ob_frequency")}</span>
                <select value={frequency} onChange={(e) => setFrequency(e.target.value)} className="border rounded px-1 py-0.5 text-sm bg-blue-50">
                  {FREQUENCIES.map((f) => (
                    <option key={f}>{f}</option>
                  ))}
                </select>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-500">{t(lang, "ob_status")}</span>
                <select value={status} onChange={(e) => setStatus(e.target.value)} className="border rounded px-1 py-0.5 text-sm bg-blue-50">
                  {STATUSES.map((s) => (
                    <option key={s}>{s}</option>
                  ))}
                </select>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-500">{t(lang, "ob_responsible")}</span>
                <select value={responsible} onChange={(e) => setResponsible(e.target.value)} className="border rounded px-1 py-0.5 text-sm bg-blue-50">
                  {RESPONSIBLES.map((r) => (
                    <option key={r} value={r}>
                      {r || "-"}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>

        <div className="grid min-h-0 flex-1 grid-cols-12 gap-2">
          <section className="col-span-2 flex min-h-0 flex-col rounded-lg border border-slate-200 bg-white p-2 shadow-sm">
            <div className="mb-2 flex shrink-0 items-center justify-between gap-1">
              <span className="text-xs font-bold uppercase text-slate-700">
                {t(lang, "ob_machines")} ({selectedEquip.length}/{equipmentCodes.length})
              </span>
              <div className="flex gap-2 text-[10px]">
                <button type="button" onClick={() => setSelectedEquip(equipmentCodes)} className="text-blue-700 hover:underline">{t(lang, "ob_all")}</button>
                <button type="button" onClick={() => setSelectedEquip([])} className="text-slate-600 hover:underline">{t(lang, "ob_none")}</button>
              </div>
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto rounded border border-slate-200">
              {equipmentLoading ? (
                <p className="p-3 text-xs text-slate-500">{t(lang, "dash_loading")}</p>
              ) : equipmentCodes.length === 0 ? (
                <p className="p-3 text-xs text-slate-400">{t(lang, "ob_empty_modules")}</p>
              ) : equipmentCodes.map((code) => (
                <label key={code} className="flex cursor-pointer items-start gap-2 border-b px-2 py-2 text-xs last:border-0 hover:bg-blue-50">
                  <input
                    type="checkbox"
                    checked={selectedEquip.includes(code)}
                    onChange={() => toggleEquip(code)}
                    className="mt-0.5 shrink-0 accent-blue-700"
                  />
                  <span className="min-w-0 flex-1">
                    <span className="block break-words font-medium">{code}</span>
                    <span className="text-[10px] text-slate-500">{componentCounts.get(code) ?? 0}</span>
                  </span>
                </label>
              ))}
            </div>
          </section>

          <section className="col-span-7 flex min-h-0 flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
            <DataTable
              data={moduleRows}
              columns={moduleColumns}
              loading={equipmentLoading}
              loadingText={t(lang, "dash_loading")}
              emptyText={t(lang, "ob_empty_modules")}
              getRowId={(row) => row.id}
              className="min-h-0 flex-1 border-0"
            />
          </section>

          <section className="col-span-3 min-h-0 overflow-y-auto rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
            <div className="text-sm font-bold text-slate-900 pb-2">{t(lang, "ob_estimated_costs")}</div>
            <div className="space-y-1 text-xs">
              <FieldRow label={t(lang, "ob_f_trip")}>€{calc?.trip_cost ?? "—"}</FieldRow>
              <FieldRow label={t(lang, "ob_f_diets")}>€{calc?.diets ?? "—"}</FieldRow>
              <FieldRow label={t(lang, "ob_f_hotels")}>€{calc?.hotel_nights_cost ?? "—"}</FieldRow>
              <FieldRow label={t(lang, "ob_f_trip_hours")}>{calc?.trip_hours ?? "—"}</FieldRow>
              <FieldRow label={t(lang, "ob_f_work")}>{calc ? (Number(calc.work_hours) + Number(calc.bk_hours)).toFixed(1) : "—"}</FieldRow>
              <FieldRow label={t(lang, "ob_f_report")}>{calc?.report_hours ?? "—"}</FieldRow>
              <FieldRow label={t(lang, "ob_f_bk")}>{calc?.bk_hours ?? "—"}</FieldRow>
              <div className="flex justify-between border-t pt-1 font-bold">
                <span>{t(lang, "ob_f_total_hours")}</span>
                <span className="font-mono">{calc?.total_hours ?? "—"}</span>
              </div>
              <div className="flex justify-between text-red-600 font-bold">
                <span>{t(lang, "ob_f_guard_hours")}</span>
                <span className="font-mono">{calc?.total_hours ?? "—"}</span>
              </div>
              <div className="flex justify-between border-t pt-1 font-bold">
                <span>{t(lang, "ob_f_hours_import")}</span>
                <span className="font-mono">€{calc?.hours_import ?? "—"}</span>
              </div>
              <div className="flex justify-between font-bold">
                <span>{t(lang, "ob_f_expenses")}</span>
                <span className="font-mono">€{calc?.expenses ?? "—"}</span>
              </div>
            </div>
          </section>
        </div>

        <div className="grid shrink-0 grid-cols-12 gap-2">
          <div className="col-span-8">
            <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-2">
              <div className="text-xs font-bold text-gray-500 uppercase mb-1">{t(lang, "ob_comments")}</div>
              <textarea value={comments} onChange={(e) => setComments(e.target.value)} className="w-full border rounded p-2 text-sm h-12 resize-none" placeholder={t(lang, "ob_comments_ph")} />
            </div>
          </div>
          <div className="col-span-4">
            <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-3 text-sm space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">{t(lang, "ob_total")}</span>
                <span className="font-mono font-bold">{calc ? eur(calc.total) : "—"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">{t(lang, "ob_spare")}</span>
                <span className="font-mono">{calc ? eur(calc.bk_price) : "—"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">{t(lang, "ob_discount")}</span>
                <span className="font-mono text-red-600">{calc ? eur(calc.discount) : "—"}</span>
              </div>
              <div className="flex justify-between border-t pt-2 text-lg font-bold">
                <span>{t(lang, "ob_total_amount")}</span>
                <span className="font-mono text-blue-700">{calc ? eur(calc.total_end) : "—"}</span>
              </div>
            </div>
          </div>
        </div>

      </main>
      </div>
    </div>
  );
}
