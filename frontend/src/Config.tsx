import { useEffect, useState } from "react";
import {
  createKit,
  deleteDistance,
  deleteKit,
  deleteMachinePrice,
  listDistances,
  listKits,
  listMachinePrices,
  getPrices,
  updateKit,
  updatePrices,
  upsertDistance,
  upsertMachinePrice,
  type Distance,
  type Kit,
  type MachinePrice,
} from "./api";
import Modal from "./components/Modal";
import SectionCard from "./components/SectionCard";
import { t, type Lang } from "./i18n";

type Section = "rates" | "distances" | "kits" | "machines";
type Editing =
  | { kind: "distance"; province: string; km: string; trip: string }
  | { kind: "kit"; model: string; hours: string; spares: string; isNew: boolean }
  | { kind: "machine"; model: string; price: string; inspections: string; isNew: boolean }
  | null;

const num = (v: string, fallback: number) => {
  const n = Number(v);
  return Number.isFinite(n) && n >= 0 ? n : fallback;
};

// Admin-only per-subsidiary configuration: rates, distances, kits, machines.
// Rows edit in a modal; deletes stay on the row. Every write goes through
// the admin-guarded endpoints; reads need identity.
export default function Config({ lang, isAdmin }: { lang: Lang; isAdmin: boolean }) {
  const [section, setSection] = useState<Section>("rates");
  const [error, setError] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const [editing, setEditing] = useState<Editing>(null);

  const [sub, setSub] = useState("ES");
  const [rates, setRates] = useState({ km_rate: "0.5", tech_rate: "60", diet_full_rate: "40", diet_half_rate: "20", hotel_rate: "80" });

  const [distances, setDistances] = useState<Distance[]>([]);
  const [kits, setKits] = useState<Kit[]>([]);
  const [machines, setMachines] = useState<MachinePrice[]>([]);

  const input = "border rounded px-2 py-1 text-sm";
  const btn = "px-3 py-1 rounded text-sm bg-weber-blue text-white disabled:opacity-40";
  const danger = "text-xs text-red-600 hover:underline";
  const edit = "text-xs text-blue-600 hover:underline mr-2";

  async function refreshTables() {
    try {
      const [d, k, m] = await Promise.all([listDistances(), listKits(), listMachinePrices()]);
      setDistances(d);
      setKits(k);
      setMachines(m);
    } catch (e) {
      setError(String(e));
    }
  }

  useEffect(() => {
    if (isAdmin) refreshTables();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin]);

  async function loadRates() {
    setError(null);
    try {
      const p = await getPrices(sub || "ES");
      setRates({
        km_rate: p.km_rate,
        tech_rate: p.tech_rate,
        diet_full_rate: p.diet_full_rate,
        diet_half_rate: p.diet_half_rate,
        hotel_rate: p.hotel_rate,
      });
    } catch (e) {
      setError(String(e));
    }
  }

  async function saveRates() {
    setError(null);
    setOk(null);
    try {
      await updatePrices(sub || "ES", {
        currency: "EUR",
        km_rate: num(rates.km_rate, 0),
        tech_rate: num(rates.tech_rate, 0),
        diet_full_rate: num(rates.diet_full_rate, 0),
        diet_half_rate: num(rates.diet_half_rate, 0),
        hotel_rate: num(rates.hotel_rate, 0),
      });
      setOk("OK");
    } catch (e) {
      setError(String(e));
    }
  }

  async function saveModal() {
    if (!editing) return;
    setError(null);
    try {
      if (editing.kind === "distance") {
        await upsertDistance(editing.province, num(editing.km, 0), num(editing.trip, 0));
      } else if (editing.kind === "kit") {
        if (editing.isNew) {
          await createKit(editing.model, num(editing.hours, 0), num(editing.spares, 0));
        } else {
          await updateKit(editing.model, num(editing.hours, 0), num(editing.spares, 0));
        }
      } else {
        await upsertMachinePrice(editing.model, num(editing.price, 0), Math.max(1, Math.floor(num(editing.inspections, 1))));
      }
      setEditing(null);
      await refreshTables();
    } catch (e) {
      setError(String(e));
    }
  }

  if (!isAdmin) return <p className="p-4 text-sm text-gray-500">{t(lang, "cfg_admin_only")}</p>;

  const tab = (active: boolean) =>
    `px-3 py-1 rounded text-sm font-medium ${active ? "bg-weber-blue text-white" : "bg-gray-200 hover:bg-gray-300"}`;

  const modalTitle =
    !editing || editing.kind === "distance"
      ? t(lang, "cfg_distances")
      : editing.kind === "kit"
        ? t(lang, "cfg_kits")
        : t(lang, "cfg_machines");

  return (
    <div className="p-4 space-y-3 w-full">
      <h1 className="text-2xl font-bold text-gray-900">{t(lang, "cfg_title")}</h1>
      <div className="flex gap-2">
        {(["rates", "distances", "kits", "machines"] as Section[]).map((s) => (
          <button key={s} onClick={() => setSection(s)} className={tab(section === s)}>
            {t(lang, s === "rates" ? "cfg_rates" : s === "distances" ? "cfg_distances" : s === "kits" ? "cfg_kits" : "cfg_machines")}
          </button>
        ))}
      </div>
      {error && <p className="text-sm text-red-600 bg-white rounded shadow p-2">{error}</p>}
      {ok && <p className="text-sm text-green-700 bg-white rounded shadow p-2">{ok}</p>}

      {section === "rates" && (
        <SectionCard title={t(lang, "cfg_rates")}>
          <div className="flex gap-2 items-center flex-wrap">
            <input value={sub} onChange={(e) => setSub(e.target.value)} placeholder="ES" className={`${input} w-24`} />
            <button onClick={loadRates} className="px-3 py-1 rounded text-sm bg-gray-200 hover:bg-gray-300">Load</button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-2">
            {(Object.keys(rates) as (keyof typeof rates)[]).map((k) => (
              <label key={k} className="text-xs">
                {k}
                <input value={rates[k]} onChange={(e) => setRates({ ...rates, [k]: e.target.value })} className={`${input} w-full`} />
              </label>
            ))}
          </div>
          <button onClick={saveRates} className={`${btn} mt-2`}>
            {t(lang, "cfg_save")}
          </button>
        </SectionCard>
      )}

      {section === "distances" && (
        <SectionCard title={t(lang, "cfg_distances")}>
          <button
            onClick={() => setEditing({ kind: "distance", province: "", km: "", trip: "" })}
            className={`${btn} mb-2`}
          >
            {t(lang, "cfg_add")}
          </button>
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-weber-blue text-white text-left">
                <th className="px-3 py-1.5">Province</th>
                <th className="px-3 py-1.5 text-right">km</th>
                <th className="px-3 py-1.5 text-right">trip h</th>
                <th className="px-3 py-1.5" />
              </tr>
            </thead>
            <tbody>
              {distances.map((d) => (
                <tr key={d.province} className="border-b">
                  <td className="px-3 py-1.5">{d.province}</td>
                  <td className="px-3 py-1.5 text-right font-mono">{d.km}</td>
                  <td className="px-3 py-1.5 text-right font-mono">{d.trip_hours}</td>
                  <td className="px-3 py-1.5 text-right whitespace-nowrap">
                    <button
                      onClick={() => setEditing({ kind: "distance", province: d.province, km: d.km, trip: d.trip_hours })}
                      className={edit}
                    >
                      {t(lang, "cfg_edit")}
                    </button>
                    <button
                      onClick={async () => {
                        await deleteDistance(d.province).catch((e) => setError(String(e)));
                        await refreshTables();
                      }}
                      className={danger}
                    >
                      {t(lang, "cfg_delete")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </SectionCard>
      )}

      {section === "kits" && (
        <SectionCard title={t(lang, "cfg_kits")}>
          <button
            onClick={() => setEditing({ kind: "kit", model: "", hours: "", spares: "", isNew: true })}
            className={`${btn} mb-2`}
          >
            {t(lang, "cfg_add")}
          </button>
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-weber-blue text-white text-left">
                <th className="px-3 py-1.5">Model</th>
                <th className="px-3 py-1.5 text-right">hours</th>
                <th className="px-3 py-1.5 text-right">spare €</th>
                <th className="px-3 py-1.5" />
              </tr>
            </thead>
            <tbody>
              {kits.map((k) => (
                <tr key={k.model} className="border-b">
                  <td className="px-3 py-1.5 font-mono">{k.model}</td>
                  <td className="px-3 py-1.5 text-right font-mono">{k.workload_basic_kit}</td>
                  <td className="px-3 py-1.5 text-right font-mono">{k.spare_parts}</td>
                  <td className="px-3 py-1.5 text-right whitespace-nowrap">
                    <button
                      onClick={() => setEditing({ kind: "kit", model: k.model, hours: k.workload_basic_kit, spares: k.spare_parts, isNew: false })}
                      className={edit}
                    >
                      {t(lang, "cfg_edit")}
                    </button>
                    <button
                      onClick={async () => {
                        await deleteKit(k.model).catch((e) => setError(String(e)));
                        await refreshTables();
                      }}
                      className={danger}
                    >
                      {t(lang, "cfg_delete")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </SectionCard>
      )}

      {section === "machines" && (
        <SectionCard title={t(lang, "cfg_machines")}>
          <button
            onClick={() => setEditing({ kind: "machine", model: "", price: "", inspections: "4", isNew: true })}
            className={`${btn} mb-2`}
          >
            {t(lang, "cfg_add")}
          </button>
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-weber-blue text-white text-left">
                <th className="px-3 py-1.5">Model</th>
                <th className="px-3 py-1.5 text-right">€/year</th>
                <th className="px-3 py-1.5 text-right">insp/year</th>
                <th className="px-3 py-1.5" />
              </tr>
            </thead>
            <tbody>
              {machines.map((m) => (
                <tr key={m.model} className="border-b">
                  <td className="px-3 py-1.5 font-mono">{m.model}</td>
                  <td className="px-3 py-1.5 text-right font-mono">{m.annual_price}</td>
                  <td className="px-3 py-1.5 text-right font-mono">{m.inspections_per_year}</td>
                  <td className="px-3 py-1.5 text-right whitespace-nowrap">
                    <button
                      onClick={() => setEditing({ kind: "machine", model: m.model, price: m.annual_price, inspections: String(m.inspections_per_year), isNew: false })}
                      className={edit}
                    >
                      {t(lang, "cfg_edit")}
                    </button>
                    <button
                      onClick={async () => {
                        await deleteMachinePrice(m.model).catch((e) => setError(String(e)));
                        await refreshTables();
                      }}
                      className={danger}
                    >
                      {t(lang, "cfg_delete")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </SectionCard>
      )}

      {editing && (
        <Modal title={modalTitle} onClose={() => setEditing(null)}>
          <div className="space-y-2">
            {editing.kind === "distance" && (
              <>
                <label className="block text-xs">
                  Province
                  <input value={editing.province} onChange={(e) => setEditing({ ...editing, province: e.target.value })} className={`${input} w-full`} />
                </label>
                <label className="block text-xs">
                  km
                  <input value={editing.km} onChange={(e) => setEditing({ ...editing, km: e.target.value })} className={`${input} w-full`} />
                </label>
                <label className="block text-xs">
                  trip h
                  <input value={editing.trip} onChange={(e) => setEditing({ ...editing, trip: e.target.value })} className={`${input} w-full`} />
                </label>
              </>
            )}
            {editing.kind === "kit" && (
              <>
                <label className="block text-xs">
                  Model
                  <input value={editing.model} disabled={!editing.isNew} onChange={(e) => setEditing({ ...editing, model: e.target.value })} className={`${input} w-full disabled:bg-gray-100`} />
                </label>
                <label className="block text-xs">
                  hours
                  <input value={editing.hours} onChange={(e) => setEditing({ ...editing, hours: e.target.value })} className={`${input} w-full`} />
                </label>
                <label className="block text-xs">
                  spare €
                  <input value={editing.spares} onChange={(e) => setEditing({ ...editing, spares: e.target.value })} className={`${input} w-full`} />
                </label>
              </>
            )}
            {editing.kind === "machine" && (
              <>
                <label className="block text-xs">
                  Model
                  <input value={editing.model} disabled={!editing.isNew} onChange={(e) => setEditing({ ...editing, model: e.target.value })} className={`${input} w-full disabled:bg-gray-100`} />
                </label>
                <label className="block text-xs">
                  €/year
                  <input value={editing.price} onChange={(e) => setEditing({ ...editing, price: e.target.value })} className={`${input} w-full`} />
                </label>
                <label className="block text-xs">
                  insp/year
                  <input value={editing.inspections} onChange={(e) => setEditing({ ...editing, inspections: e.target.value })} className={`${input} w-full`} />
                </label>
              </>
            )}
            <div className="flex justify-end gap-2 pt-2">
              <button onClick={() => setEditing(null)} className="px-3 py-1 rounded text-sm bg-gray-200 hover:bg-gray-300">
                ×
              </button>
              <button onClick={saveModal} className={btn}>
                {t(lang, "cfg_save")}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
