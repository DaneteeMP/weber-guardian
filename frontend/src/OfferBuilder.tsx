import { useEffect, useState } from "react";
import { calculate, createOffer, listCustomers, listOffers, type Breakdown, type Customer } from "./api";
import FieldRow from "./components/FieldRow";
import SectionCard from "./components/SectionCard";
import { t, type Lang } from "./i18n";

const num = (v: string, fallback: number) => {
  const n = Number(v);
  return Number.isFinite(n) && n >= 0 ? n : fallback;
};

export default function OfferBuilder({ lang }: { lang: Lang }) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customerId, setCustomerId] = useState("");
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
  const [items, setItems] = useState([{ equipment: "304-565", description: "Slicer", import_amount: "100", workload: "6" }]);
  const [offersCount, setOffersCount] = useState(0);

  useEffect(() => {
    listCustomers().then(setCustomers).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    if (customerId) {
      listOffers(customerId).then((o) => setOffersCount(o.length)).catch(() => setOffersCount(0));
    }
  }, [customerId, saved]);

  // Live preview: authoritative breakdown comes from the backend on every input change.
  useEffect(() => {
    const t = setTimeout(() => {
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
    return () => clearTimeout(t);
  }, [workHours, reportHours, tripBase, km, kmRate, techRate, dietFull, dietHalf, hotelRate]);

  async function handleSave() {
    setError(null);
    setSaved(null);
    try {
      if (!customerId) throw new Error(t(lang, "ob_select_first"));
      await createOffer({
        customer_id: customerId,
        id_guardian_offer: offerNumber || undefined,
        status: "Draft",
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
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    }
  }

  const input = "border rounded px-2 py-1 text-sm w-full";

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="text-white px-6 py-3 flex items-center justify-between" style={{ background: "linear-gradient(135deg, #1D4F91, #2563EB)" }}>
        <h1 className="text-xl font-bold tracking-wide">{t(lang, "ob_title")}</h1>
        <button onClick={handleSave} className="px-3 py-1 bg-white/20 hover:bg-white/30 rounded text-sm font-medium">
          {t(lang, "ob_save")}
        </button>
      </div>

      <div className="p-4 space-y-3 max-w-6xl mx-auto">
        {error && <p className="text-sm text-red-600 bg-white rounded shadow p-2">{error}</p>}
        {saved && <p className="text-sm text-green-700 bg-white rounded shadow p-2">{saved}</p>}

        <SectionCard title={t(lang, "ob_customer_offer")}>
          <div className="grid grid-cols-2 gap-4">
            <select value={customerId} onChange={(e) => setCustomerId(e.target.value)} className={`${input} bg-blue-50`}>
              <option value="">{t(lang, "ob_select_client")}</option>
              {customers.map((c) => (
                <option key={c.customer_id} value={c.customer_id}>
                  {c.customer_id} — {c.account_name}
                </option>
              ))}
            </select>
            <input value={offerNumber} onChange={(e) => setOfferNumber(e.target.value)} placeholder="Offer no. (optional, e.g. W-02-2026-0001)" className={input} />
          </div>
          {offersCount > 0 && <p className="text-xs text-gray-500 mt-1">This customer already has {offersCount} offer(s).</p>}
        </SectionCard>

        <div className="grid grid-cols-12 gap-3">
          <div className="col-span-5">
            <SectionCard title={t(lang, "ob_hours_travel")}>
              <div className="grid grid-cols-2 gap-2">
                <label className="text-xs">Work hours<input value={workHours} onChange={(e) => setWorkHours(e.target.value)} className={input} /></label>
                <label className="text-xs">Report hours<input value={reportHours} onChange={(e) => setReportHours(e.target.value)} className={input} /></label>
                <label className="text-xs">Trip base h<input value={tripBase} onChange={(e) => setTripBase(e.target.value)} className={input} /></label>
                <label className="text-xs">Km<input value={km} onChange={(e) => setKm(e.target.value)} className={input} /></label>
                <label className="text-xs">€/km<input value={kmRate} onChange={(e) => setKmRate(e.target.value)} className={input} /></label>
                <label className="text-xs">€/tech-hour<input value={techRate} onChange={(e) => setTechRate(e.target.value)} className={input} /></label>
                <label className="text-xs">Full diet €<input value={dietFull} onChange={(e) => setDietFull(e.target.value)} className={input} /></label>
                <label className="text-xs">Half diet €<input value={dietHalf} onChange={(e) => setDietHalf(e.target.value)} className={input} /></label>
                <label className="text-xs">Hotel €<input value={hotelRate} onChange={(e) => setHotelRate(e.target.value)} className={input} /></label>
              </div>
            </SectionCard>
          </div>

          <div className="col-span-4">
            <SectionCard title={t(lang, "ob_breakdown")}>
              {!calc ? (
                <p className="text-xs text-gray-400">Type inputs to preview…</p>
              ) : (
                <div>
                  <FieldRow label="Trip">€{calc.trip_cost}</FieldRow>
                  <FieldRow label="Diets">€{calc.diets}</FieldRow>
                  <FieldRow label="Hotels">€{calc.hotel_nights_cost}</FieldRow>
                  <FieldRow label="Trip hours">{calc.trip_hours}</FieldRow>
                  <FieldRow label="Total hours">{calc.total_hours}</FieldRow>
                  <FieldRow label="Hours import">€{calc.hours_import}</FieldRow>
                  <FieldRow label="Expenses">€{calc.expenses}</FieldRow>
                  <div className="border-t mt-1 pt-1 font-bold">
                    <FieldRow label="Total">€{calc.total}</FieldRow>
                    <FieldRow label="Discount">€{calc.discount}</FieldRow>
                    <FieldRow label="Total amount">€{calc.total_end}</FieldRow>
                  </div>
                </div>
              )}
            </SectionCard>
          </div>

          <div className="col-span-3">
            <SectionCard title={t(lang, "ob_items")}>
              {items.map((it, i) => (
                <div key={i} className="grid grid-cols-2 gap-1 mb-2 border-b pb-2">
                  <input value={it.equipment} onChange={(e) => setItems((p) => p.map((x, j) => (j === i ? { ...x, equipment: e.target.value } : x)))} placeholder="Equipment" className={input} />
                  <input value={it.workload} onChange={(e) => setItems((p) => p.map((x, j) => (j === i ? { ...x, workload: e.target.value } : x)))} placeholder="Workload" className={input} />
                  <input value={it.description} onChange={(e) => setItems((p) => p.map((x, j) => (j === i ? { ...x, description: e.target.value } : x)))} placeholder="Description" className={`${input} col-span-2`} />
                  <input value={it.import_amount} onChange={(e) => setItems((p) => p.map((x, j) => (j === i ? { ...x, import_amount: e.target.value } : x)))} placeholder="Amount" className={input} />
                  <button onClick={() => setItems((p) => p.filter((_, j) => j !== i))} className="text-xs text-red-600 hover:underline">{t(lang, "ob_remove")}</button>
                </div>
              ))}
              <button
                onClick={() => setItems((p) => [...p, { equipment: "", description: "", import_amount: "0", workload: "0" }])}
                className="text-xs text-blue-600 hover:underline"
              >
                {t(lang, "ob_add_line")}
              </button>
            </SectionCard>
          </div>
        </div>
      </div>
    </div>
  );
}
