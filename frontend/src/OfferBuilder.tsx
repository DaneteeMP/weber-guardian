import { useEffect, useMemo, useRef, useState } from "react";
import {
  calculate,
  closeOffer,
  createOffer,
  deleteOffer,
  downloadOfferPdf,
  getPrices,
  listCustomers,
  listEquipment,
  listOffers,
  me,
  type Breakdown,
  type Customer,
  type Equipment,
  type OfferListItem,
} from "./api";
import FieldRow from "./components/FieldRow";
import SectionCard from "./components/SectionCard";
import { t, type Lang } from "./i18n";

const num = (v: string, fallback: number) => {
  const n = Number(v);
  return Number.isFinite(n) && n >= 0 ? n : fallback;
};

const GUARDIAN_TYPES = ["Basic Kit", "Audit", "Off-Guardian", "Campaign"];
const LANGUAGES = ["Spanish", "Portuguese"];
const FREQUENCIES = ["Annual", "Semi-annual", "Biennial"];
const STATUSES = ["Draft", "Pending response", "Finished", "Cancelled", "Rejected"];
const RESPONSIBLES = ["", "Xevi Mira", "David"];

const COLORS = ["#e3f2fd", "#fce4ec", "#e8f5e9", "#fff3e0", "#f3e5f5", "#e0f7fa", "#fff9c4", "#efebe9"];

export default function OfferBuilder({ lang }: { lang: Lang }) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customerId, setCustomerId] = useState("");
  const [clientSearch, setClientSearch] = useState("");
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState<string | null>(null);
  const [calc, setCalc] = useState<Breakdown | null>(null);

  const [workHours, setWorkHours] = useState("10");
  const [reportHours, setReportHours] = useState("2");
  const [tripBase, setTripBase] = useState("3");
  const [km, setKm] = useState("50");
  const [kmRate, setKmRate] = useState("0.5");
  const [techRate, setTechRate] = useState("60");
  const [dietFull, setDietFull] = useState("40");
  const [dietHalf, setDietHalf] = useState("20");
  const [hotelRate, setHotelRate] = useState("80");
  const [offerNumber, setOfferNumber] = useState("");
  const [language, setLanguage] = useState("Spanish");
  const [frequency, setFrequency] = useState("Annual");
  const [status, setStatus] = useState("Pending response");
  const [responsible, setResponsible] = useState("");
  const [guardianType, setGuardianType] = useState("Audit");
  const [comments, setComments] = useState("");
  type QuoteLine = { equipment: string; description: string; import_amount: string; workload: string };
  const [items, setItems] = useState<QuoteLine[]>([]);
  const [offers, setOffers] = useState<OfferListItem[]>([]);
  const [savedOffer, setSavedOffer] = useState<{ id: string; status: string } | null>(null);
  const [equipList, setEquipList] = useState<Equipment[]>([]);
  const [selectedEquip, setSelectedEquip] = useState<string[]>([]);

  const availableCodes = useMemo(
    () =>
      [...new Set(equipList.map((e) => e.equipment_name).filter((x): x is string => !!x))].filter(
        (c) => !selectedEquip.includes(c)
      ),
    [equipList, selectedEquip]
  );

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
  const lineKey = (equipment: string, description: string) => `${equipment}||${description}`;
  useEffect(() => {
    const prev = prevSelected.current;
    const added = selectedEquip.filter((c) => !prev.includes(c));
    const removed = prev.filter((c) => !selectedEquip.includes(c));
    prevSelected.current = selectedEquip;
    if (added.length === 0 && removed.length === 0) return;
    const rowsOf = (code: string) => equipList.filter((e) => e.equipment_name === code);
    const wasAuto = new Set(autoLines.current);
    const removedKeys = new Set<string>();
    for (const code of removed) {
      for (const row of rowsOf(code)) {
        const key = lineKey(code, row.component_type ?? "");
        if (wasAuto.has(key)) removedKeys.add(key);
      }
    }
    const desired = new Map<string, { equipment: string; description: string }>();
    for (const code of added) {
      for (const row of rowsOf(code)) {
        const description = row.component_type ?? "";
        if (!desired.has(lineKey(code, description))) {
          desired.set(lineKey(code, description), { equipment: code, description });
        }
      }
    }
    autoLines.current = new Set([...autoLines.current].filter((k) => !removedKeys.has(k)));
    for (const key of desired.keys()) autoLines.current.add(key);
    setItems((lines) => {
      const have = new Set(lines.map((l) => lineKey(l.equipment, l.description)));
      const fresh = [...desired.entries()]
        .filter(([key]) => !have.has(key))
        .map(([, v]) => ({ ...v, import_amount: "0", workload: "0" }));
      // Drop lines the picker added for deselected machines; keep
      // everything else, including hand-typed lines.
      const dropped = (l: { equipment: string; description: string }) =>
        removedKeys.has(lineKey(l.equipment, l.description)) && wasAuto.has(lineKey(l.equipment, l.description));
      return [...lines.filter((l) => !dropped(l)), ...fresh];
    });
  }, [selectedEquip, equipList]);

  useEffect(() => {
    listCustomers().then((res) => setCustomers(res.rows)).catch((e) => setError(String(e)));
    me()
      .then((mine) => (mine.subsidiary_id ? getPrices(mine.subsidiary_id) : null))
      .then((p) => {
        if (!p) return;
        setKmRate(p.km_rate);
        setTechRate(p.tech_rate);
        setDietFull(p.diet_full_rate);
        setDietHalf(p.diet_half_rate);
        setHotelRate(p.hotel_rate);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    setCustomer(customers.find((c) => c.customer_id === customerId) ?? null);
    setSavedOffer(null);
    if (customerId) {
      listOffers(customerId).then(setOffers).catch(() => setOffers([]));
      listEquipment(customerId)
        .then((eq) => {
          setEquipList(eq);
          setSelectedEquip([]);
        })
        .catch(() => {
          setEquipList([]);
          setSelectedEquip([]);
        });
    } else {
      setOffers([]);
      setEquipList([]);
      setSelectedEquip([]);
    }
  }, [customerId, customers]);

  // Server-side client search: the dropdown only holds one page.
  useEffect(() => {
    const timer = setTimeout(() => {
      listCustomers({ search: clientSearch.trim() || undefined })
        .then((res) => setCustomers(res.rows))
        .catch((e) => setError(String(e)));
    }, 300);
    return () => clearTimeout(timer);
  }, [clientSearch]);

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
    setSavedOffer(null);
    try {
      if (!customerId) throw new Error(t(lang, "ob_select_first"));
      const created = await createOffer({
        customer_id: customerId,
        id_guardian_offer: offerNumber || undefined,
        status,
        responsible_person: responsible || undefined,
        language,
        inspection_frequency: frequency,
        general_comments: comments || undefined,
        pricing: {
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
        },
        items: items.map((i) => ({
          equipment: i.equipment || undefined,
          description: i.description || undefined,
          import_amount: num(i.import_amount, 0),
          workload: num(i.workload, 0),
        })),
      });
      setSaved(t(lang, "ob_saved"));
      setSavedOffer({ id: created.id, status });
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
    setError(null);
    try {
      if (!savedOffer) return;
      const { blob, filename } = await downloadOfferPdf(savedOffer.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Print failed");
    }
  }

  const input = "border rounded px-2 py-1.5 text-sm w-full";
  const today = new Date().toLocaleDateString("en-GB");

  const moduleRows = items.map((m, i) => ({ pos: i + 1, equipment: m.equipment, module: m.description, amount: num(m.import_amount, 0) }));
  const colorMap: Record<string, string> = {};
  [...new Set(items.map((m) => m.equipment))].forEach((eq, i) => {
    colorMap[eq] = COLORS[i % COLORS.length];
  });

  const eur = (v: string | number | null | undefined) =>
    `${Number(v ?? 0).toLocaleString("en-GB", { minimumFractionDigits: 2 })} €`;

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <div className="bg-weber-blue text-white px-6 py-3 flex items-center justify-between shadow">
        <h1 className="text-xl font-bold tracking-wide">{t(lang, "ob_title")}</h1>
        <div className="flex gap-2">
          <button onClick={handlePrint} disabled={!savedOffer} className="px-3 py-1 bg-white/20 hover:bg-white/30 rounded text-sm font-medium disabled:opacity-40">
            {t(lang, "ob_print")}
          </button>
          <button onClick={handleDelete} disabled={!savedOffer} className="px-3 py-1 bg-white/20 hover:bg-white/30 rounded text-sm font-medium disabled:opacity-40">
            {t(lang, "ob_delete_offer")}
          </button>
          <button onClick={handleClose} disabled={!savedOffer} className="px-3 py-1 bg-white/20 hover:bg-white/30 rounded text-sm font-medium disabled:opacity-40">
            {t(lang, "ob_close_offer")}
          </button>
        </div>
      </div>

      <div className="flex-1 p-4 space-y-3 w-full">
        {error && <p className="text-sm text-red-600 bg-white rounded-lg shadow p-3">{error}</p>}
        {saved && <p className="text-sm text-green-700 bg-white rounded-lg shadow p-3">{saved}</p>}

        <div className="bg-white rounded-lg shadow p-4">
          <div className="grid grid-cols-12 gap-4">
            <div className="col-span-5 border-r pr-4">
              <div className="text-xs font-bold text-gray-500 uppercase mb-2">{t(lang, "ob_customer_data")}</div>
              <input
                value={clientSearch}
                onChange={(e) => setClientSearch(e.target.value)}
                placeholder={t(lang, "cust_search_ph")}
                className={`${input} mb-1`}
              />
              <select value={customerId} onChange={(e) => setCustomerId(e.target.value)} className={`${input} bg-blue-50 mb-2`}>
                <option value="">{t(lang, "ob_select_client")}</option>
                {customers.map((c) => (
                  <option key={c.customer_id} value={c.customer_id}>
                    {c.customer_id} {c.account_name}
                  </option>
                ))}
              </select>
              {customer && (
                <div className="text-sm">
                  <div className="font-semibold">{customer.account_name}</div>
                  <div className="text-gray-600">{customer.country ?? ""}</div>
                </div>
              )}
            </div>

            <div className="col-span-4 border-r pr-4">
              <div className="space-y-1.5 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 w-28">{t(lang, "ob_offer_no")}</span>
                  <span className="font-mono font-bold">{offerNumber || savedOffer?.id.slice(0, 8) || "-"}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 w-28">{t(lang, "ob_offer_date")}</span>
                  <span>{today}</span>
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
                  <input value={offerNumber} onChange={(e) => setOfferNumber(e.target.value)} placeholder="W-02-2026-0001" className="border rounded px-1 py-0.5 text-sm font-mono" />
                </div>
              </div>
            </div>

            <div className="col-span-3 space-y-1.5 text-sm">
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

        <div className="grid grid-cols-12 gap-3">
          <div className="col-span-2 space-y-3">
            <div className="bg-white rounded shadow p-2">
              <div className="text-xs font-bold text-gray-500 uppercase mb-1">{t(lang, "ob_no_selected")}</div>
              <div className="border rounded h-56 overflow-y-auto bg-gray-50">
                {availableCodes.length === 0 ? (
                  <div className="p-2 text-xs text-gray-400">Empty</div>
                ) : (
                  availableCodes.map((c) => (
                    <div key={c} onClick={() => toggleEquip(c)} className="px-2 py-1 text-xs hover:bg-blue-100 cursor-pointer border-b last:border-0">
                      {c}
                    </div>
                  ))
                )}
              </div>
            </div>
            <div className="bg-white rounded shadow p-2">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-gray-500 uppercase">{t(lang, "ob_selected")}</span>
                <div className="flex gap-1">
                  <button onClick={() => setSelectedEquip(availableCodes.concat(selectedEquip))} className="text-[10px] text-blue-600 hover:underline">
                    {t(lang, "ob_all")}
                  </button>
                  <button onClick={() => setSelectedEquip([])} className="text-[10px] text-red-600 hover:underline">
                    {t(lang, "ob_none")}
                  </button>
                </div>
              </div>
              <div className="border rounded h-56 overflow-y-auto bg-blue-50">
                {selectedEquip.length === 0 ? (
                  <div className="p-2 text-xs text-gray-400">None</div>
                ) : (
                  selectedEquip.map((c) => (
                    <div key={c} onClick={() => toggleEquip(c)} className="px-2 py-1 text-xs cursor-pointer border-b last:border-0 font-medium hover:bg-red-100 bg-blue-200">
                      {c}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="col-span-6">
            <div className="bg-white rounded shadow h-full min-h-[420px] max-h-[640px] flex flex-col">
              <div className="overflow-auto flex-1 min-h-0">
                <table className="w-full text-xs">
                  <thead className="bg-gray-700 text-white sticky top-0">
                    <tr>
                      <th className="px-2 py-2 text-left w-10">{t(lang, "ob_col_pos")}</th>
                      <th className="px-2 py-2 text-left">{t(lang, "ob_col_equipment")}</th>
                      <th className="px-2 py-2 text-left">{t(lang, "ob_col_module")}</th>
                      <th className="px-2 py-2 text-right w-24">{t(lang, "ob_col_amount")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {moduleRows.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="px-4 py-8 text-center text-gray-400">
                          {t(lang, "ob_empty_modules")}
                        </td>
                      </tr>
                    ) : (
                      moduleRows.map((row) => (
                        <tr key={row.pos} style={{ backgroundColor: colorMap[row.equipment] || "#fff" }} className="border-b">
                          <td className="px-2 py-1.5 font-medium">{row.pos}</td>
                          <td className="px-2 py-1.5 font-semibold">{row.equipment}</td>
                          <td className="px-2 py-1.5">{row.module}</td>
                          <td className="px-2 py-1.5 text-right font-mono">{eur(row.amount)}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
              <div className="p-2 border-t">
                <div className="text-xs font-bold text-gray-500 uppercase mb-1">{t(lang, "ob_items")}</div>
                <div className="grid grid-cols-12 gap-1 mb-1 text-[10px] font-bold text-gray-500 uppercase">
                  <span className="col-span-3">Equipment</span>
                  <span className="col-span-4">Module</span>
                  <span className="col-span-2 text-right">Amount €</span>
                  <span className="col-span-2 text-right">Hours</span>
                  <span className="col-span-1" />
                </div>
                {items.map((it, i) => (
                  <div key={i} className="grid grid-cols-12 gap-1 mb-1">
                    <input value={it.equipment} onChange={(e) => setItems((p) => p.map((x, j) => (j === i ? { ...x, equipment: e.target.value } : x)))} placeholder="304-565" className="col-span-3 border rounded px-1 py-0.5 text-xs" />
                    <input value={it.description} onChange={(e) => setItems((p) => p.map((x, j) => (j === i ? { ...x, description: e.target.value } : x)))} placeholder="—" className="col-span-4 border rounded px-1 py-0.5 text-xs" />
                    <input value={it.import_amount} onChange={(e) => setItems((p) => p.map((x, j) => (j === i ? { ...x, import_amount: e.target.value } : x)))} placeholder="0.00" className="col-span-2 border rounded px-1 py-0.5 text-xs text-right" />
                    <input value={it.workload} onChange={(e) => setItems((p) => p.map((x, j) => (j === i ? { ...x, workload: e.target.value } : x)))} placeholder="0.0" className="col-span-2 border rounded px-1 py-0.5 text-xs text-right" />
                    <button onClick={() => setItems((p) => p.filter((_, j) => j !== i))} className="col-span-1 text-xs text-red-600 hover:underline">
                      ×
                    </button>
                  </div>
                ))}
                <button
                  onClick={() => setItems((p) => [...p, { equipment: "", description: "", import_amount: "0", workload: "0" }])}
                  className="text-xs text-blue-600 hover:underline"
                >
                  {t(lang, "ob_add_lines")}
                </button>
              </div>
            </div>
          </div>

          <div className="col-span-4">
            <div className="bg-white rounded shadow p-3 text-xs space-y-1">
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
              <div className="grid grid-cols-2 gap-2 pt-1">
                <label className="text-xs">{t(lang, "ob_in_work")}<input value={workHours} onChange={(e) => setWorkHours(e.target.value)} className="border rounded px-1 py-0.5 text-xs w-full" /></label>
                <label className="text-xs">{t(lang, "ob_in_report")}<input value={reportHours} onChange={(e) => setReportHours(e.target.value)} className="border rounded px-1 py-0.5 text-xs w-full" /></label>
                <label className="text-xs">{t(lang, "ob_in_trip_base")}<input value={tripBase} onChange={(e) => setTripBase(e.target.value)} className="border rounded px-1 py-0.5 text-xs w-full" /></label>
                <label className="text-xs">{t(lang, "ob_in_km")}<input value={km} onChange={(e) => setKm(e.target.value)} className="border rounded px-1 py-0.5 text-xs w-full" /></label>
                <label className="text-xs">{t(lang, "ob_in_km_rate")}<input value={kmRate} onChange={(e) => setKmRate(e.target.value)} className="border rounded px-1 py-0.5 text-xs w-full" /></label>
                <label className="text-xs">{t(lang, "ob_in_tech")}<input value={techRate} onChange={(e) => setTechRate(e.target.value)} className="border rounded px-1 py-0.5 text-xs w-full" /></label>
                <label className="text-xs">{t(lang, "ob_in_diet_full")}<input value={dietFull} onChange={(e) => setDietFull(e.target.value)} className="border rounded px-1 py-0.5 text-xs w-full" /></label>
                <label className="text-xs">{t(lang, "ob_in_diet_half")}<input value={dietHalf} onChange={(e) => setDietHalf(e.target.value)} className="border rounded px-1 py-0.5 text-xs w-full" /></label>
                <label className="text-xs col-span-2">{t(lang, "ob_in_hotel")}<input value={hotelRate} onChange={(e) => setHotelRate(e.target.value)} className="border rounded px-1 py-0.5 text-xs w-full" /></label>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-12 gap-3">
          <div className="col-span-8">
            <div className="bg-white rounded shadow p-3">
              <div className="text-xs font-bold text-gray-500 uppercase mb-1">{t(lang, "ob_comments")}</div>
              <textarea value={comments} onChange={(e) => setComments(e.target.value)} className="w-full border rounded p-2 text-sm h-16 resize-none" placeholder={t(lang, "ob_comments_ph")} />
            </div>
          </div>
          <div className="col-span-4">
            <div className="bg-white rounded shadow p-3 text-sm space-y-2">
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

        {offers.length > 0 && (
          <div className="bg-white rounded shadow p-3">
            <div className="text-xs font-bold text-gray-500 uppercase mb-2">{t(lang, "ob_client_offers")} ({offers.length})</div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-2 py-1.5 text-left">ID</th>
                    <th className="px-2 py-1.5 text-left">Language</th>
                    <th className="px-2 py-1.5 text-left">Status</th>
                    <th className="px-2 py-1.5 text-left">Frequency</th>
                    <th className="px-2 py-1.5 text-right">Total</th>
                    <th className="px-2 py-1.5 text-right">Total End</th>
                  </tr>
                </thead>
                <tbody>
                  {offers.map((o) => (
                    <tr key={o.id_guardian_offer} className="border-b hover:bg-gray-50">
                      <td className="px-2 py-1.5 font-mono font-bold text-blue-600">{o.id_guardian_offer}</td>
                      <td className="px-2 py-1.5">{o.language || "-"}</td>
                      <td className="px-2 py-1.5">{o.status || "Draft"}</td>
                      <td className="px-2 py-1.5">{o.inspection_frequency || "-"}</td>
                      <td className="px-2 py-1.5 text-right font-mono">{eur(o.total)}</td>
                      <td className="px-2 py-1.5 text-right font-mono font-bold">{eur(o.total_end)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
