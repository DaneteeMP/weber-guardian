import { useEffect, useMemo, useState } from "react";
import type { ColumnDef } from "@tanstack/react-table";
import DistanceImport from "./DistanceImport";
import {
  createKit,
  deleteDistance,
  deleteKit,
  listDistances,
  listKits,
  getPrices,
  listSubsidiaries,
  updateKit,
  updatePrices,
  upsertDistance,
  type Distance,
  type Kit,
  type Subsidiary,
} from "./api";
import Button from "./components/Button";
import DataTable from "./components/DataTable";
import IconButton from "./components/IconButton";
import Modal from "./components/Modal";
import SectionCard from "./components/SectionCard";
import { t, type Lang } from "./i18n";

function EditIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z" />
    </svg>
  );
}

function DeleteIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 6h18" />
      <path d="M8 6V4h8v2" />
      <path d="M19 6l-1 14H6L5 6" />
      <path d="M10 11v5" />
      <path d="M14 11v5" />
    </svg>
  );
}

type Section = "rates" | "distances" | "kits";
type Editing =
  | {
      kind: "distance";
      subsidiary_id: string;
      province: string;
      province_code: string;
      region: string;
      capital: string;
      reference_city: string;
      service_center: string;
      origin_city: string;
      km: string;
      driving: string;
      trip: string;
      itinerary: string;
      route_date: string;
    }
  | { kind: "kit"; model: string; hours: string; spares: string; isNew: boolean }
  | null;

const EMPTY_RATES = { currency: "", km_rate: "", tech_rate: "", diet_full_rate: "", diet_half_rate: "", hotel_rate: "", discount_rate: "" };

function formatClock(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "";
  const match = /^(\d+)(?:\.(\d+))?$/.exec(String(value));
  if (!match) return String(value);
  const hours = Number(match[1]);
  const hundredths = Number((match[2] ?? "").padEnd(2, "0").slice(0, 2));
  const minutes = Math.round((hundredths * 60) / 100);
  const totalMinutes = hours * 60 + minutes;
  return `${Math.floor(totalMinutes / 60)}:${String(totalMinutes % 60).padStart(2, "0")}`;
}

function clockToDecimal(value: string): string | null {
  const match = /^(\d{1,3}):([0-5]\d)$/.exec(value.trim());
  if (!match) return null;
  const hours = Number(match[1]);
  const minutes = Number(match[2]);
  const fractionByMinutes: Record<number, string> = { 0: "00", 15: "25", 30: "50", 45: "75" };
  const fraction = fractionByMinutes[minutes];
  return fraction === undefined ? null : `${hours}.${fraction}`;
}

const num = (v: string, fallback: number) => {
  const n = Number(v);
  return Number.isFinite(n) && n >= 0 ? n : fallback;
};

// Admin-only per-subsidiary configuration: rates, distances, kits, machines.
// Rows edit in a modal; deletes stay on the row. Every write goes through
// the admin-guarded endpoints; reads need identity.
const GERMAN_SERVICE_CENTERS = ["Oldenburg", "Werther", "Frankfurt", "Wolfertschwenden"];

export default function Config({
  lang,
  isAdmin,
  scope,
}: {
  lang: Lang;
  isAdmin: boolean;
  scope: string | null;
}) {
  const [section, setSection] = useState<Section>("rates");
  const [error, setError] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const [editing, setEditing] = useState<Editing>(null);
  const [subsidiaries, setSubsidiaries] = useState<Subsidiary[]>([]);

  const [sub, setSub] = useState(scope ?? "Weber Iberica");
  const [rates, setRates] = useState(EMPTY_RATES);

  const [distances, setDistances] = useState<Distance[]>([]);
  const [distanceSubsidiary, setDistanceSubsidiary] = useState(scope ?? "");
  const [kits, setKits] = useState<Kit[]>([]);
  const [importOpen, setImportOpen] = useState(false);

  const input = "border rounded px-2 py-1 text-sm";

  async function refreshTables() {
    try {
      const [d, k] = await Promise.all([listDistances(), listKits()]);
      setDistances(d);
      setKits(k);
    } catch (e) {
      setError(String(e));
    }
  }

  useEffect(() => {
    if (!isAdmin) return;

    refreshTables();
    listSubsidiaries()
      .then((subs) => {
        setSubsidiaries(subs);

        const selected = scope ?? "Weber Iberica";
        const exists = subs.some((s) => s.name === selected);
        const nextSub = exists ? selected : subs[0]?.name ?? "";

        setSub(nextSub);

        if (nextSub) {
          getPrices(nextSub)
            .then((p) =>
              setRates({
                currency: p.currency,
                km_rate: p.km_rate,
                tech_rate: p.tech_rate,
                diet_full_rate: p.diet_full_rate,
                diet_half_rate: p.diet_half_rate,
                hotel_rate: p.hotel_rate,
                discount_rate: p.discount_rate,
              }),
            )
            .catch((e) => setError(String(e)));
        }
      })
      .catch((e) => setError(String(e)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin, scope]);

  async function loadRates() {
    setError(null);
    setRates(EMPTY_RATES);
    try {
      if (!sub) throw new Error(t(lang, "cfg_select_subsidiary"));
      const p = await getPrices(sub);
      setRates({
        currency: p.currency,
        km_rate: p.km_rate,
        tech_rate: p.tech_rate,
        diet_full_rate: p.diet_full_rate,
        diet_half_rate: p.diet_half_rate,
        hotel_rate: p.hotel_rate,
        discount_rate: p.discount_rate,
      });
    } catch (e) {
      setError(String(e));
    }
  }

  async function saveRates() {
    setError(null);
    setOk(null);
    try {
      if (!sub) throw new Error(t(lang, "cfg_select_subsidiary"));
      if (Object.values(rates).some((value) => !value.trim())) throw new Error(t(lang, "cfg_rates_required"));
      await updatePrices(sub, rates);
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
        if (!editing.subsidiary_id) throw new Error("Choose a subsidiary for this distance.");
        if (!editing.province.trim() || !editing.km.trim()) throw new Error(t(lang, "cfg_route_required"));
        const tripHours = clockToDecimal(editing.trip);
        const drivingHours = editing.driving.trim() ? clockToDecimal(editing.driving) : null;
        if (tripHours === null || (editing.driving.trim() && drivingHours === null)) {
          throw new Error(t(lang, "cfg_time_invalid"));
        }
        await upsertDistance(
          editing.subsidiary_id,
          editing.province,
          {
            province_code: editing.province_code.trim() || null,
            region: editing.region.trim() || null,
            capital: editing.capital.trim() || null,
            reference_city: editing.reference_city.trim() || null,
            service_center: editing.service_center.trim() || null,
            origin_city: editing.origin_city.trim() || null,
            km: editing.km.trim(),
            driving_hours: drivingHours,
            trip_hours: tripHours,
            itinerary: editing.itinerary.trim() || null,
            route_data_date: editing.route_date || null,
          }
        );
      } else if (editing.kind === "kit") {
        if (editing.isNew) {
          await createKit(editing.model, num(editing.hours, 0), num(editing.spares, 0));
        } else {
          await updateKit(editing.model, num(editing.hours, 0), num(editing.spares, 0));
        }
      }
      setEditing(null);
      await refreshTables();
    } catch (e) {
      setError(String(e));
    }
  }

  function newDistance() {
    setEditing({
      kind: "distance",
      subsidiary_id: scope ?? distanceSubsidiary,
      province: "",
      province_code: "",
      region: "",
      capital: "",
      reference_city: "",
      service_center: "",
      origin_city: "",
      km: "",
      driving: "",
      trip: "",
      itinerary: "",
      route_date: "",
    });
  }

  function editDistance(d: Distance) {
    setEditing({
      kind: "distance",
      subsidiary_id: d.subsidiary_id,
      province: d.province,
      province_code: d.province_code ?? "",
      region: d.region ?? "",
      capital: d.capital ?? "",
      reference_city: d.reference_city ?? "",
      service_center: d.service_center ?? "",
      origin_city: d.origin_city ?? "",
      km: String(d.km),
      driving: formatClock(d.driving_hours),
      trip: formatClock(d.trip_hours),
      itinerary: d.itinerary ?? "",
      route_date: d.route_data_date ?? "",
    });
  }

  async function removeDistance(d: Distance) {
    await deleteDistance(d.subsidiary_id, d.province).catch((e) => setError(String(e)));
    await refreshTables();
  }

  const distanceColumns = useMemo<ColumnDef<Distance, any>[]>(
    () => [
      { accessorKey: "subsidiary_id", header: t(lang, "cfg_subsidiary") },
      { accessorKey: "province", header: t(lang, "cfg_province") },
      {
        accessorKey: "province_code",
        header: t(lang, "cfg_province_code"),
        cell: ({ getValue }) => <span className="font-mono">{getValue<string>() ?? "—"}</span>,
      },
      {
        accessorKey: "region",
        header: t(lang, "cfg_region"),
        cell: ({ getValue }) => getValue<string>() ?? "—",
      },
      {
        id: "reference_city",
        header: t(lang, "cfg_reference_city"),
        cell: ({ row }) => row.original.reference_city ?? row.original.capital ?? "—",
      },
      {
        id: "origin_city",
        header: t(lang, "cfg_origin_city"),
        cell: ({ row }) => row.original.origin_city ?? row.original.service_center ?? "—",
      },
      {
        accessorKey: "km",
        header: t(lang, "cfg_road_km"),
        cell: ({ getValue }) => <span className="font-mono">{String(getValue())}</span>,
      },
      {
        accessorKey: "driving_hours",
        header: t(lang, "cfg_driving_time"),
        cell: ({ getValue }) => (
          <span className="font-mono">{formatClock(getValue<string>() || null) || "—"}</span>
        ),
      },
      {
        accessorKey: "trip_hours",
        header: t(lang, "cfg_total_trip_time"),
        cell: ({ getValue }) => <span className="font-mono">{formatClock(getValue<string>() || null)}</span>,
      },
      {
        accessorKey: "itinerary",
        header: t(lang, "cfg_itinerary"),
        cell: ({ getValue }) => (
          <span className="block max-w-60 truncate" title={String(getValue() ?? "")}>
            {getValue<string>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "route_data_date",
        header: t(lang, "cfg_route_date"),
        cell: ({ getValue }) => getValue<string>() ?? "—",
      },
      {
        id: "actions",
        header: "",
        enableSorting: false,
        cell: ({ row }) => (
          <div className="flex justify-end gap-1">
            <IconButton
              label={t(lang, "cfg_edit")}
              onClick={() => editDistance(row.original)}
              icon={<EditIcon />}
            />
            <IconButton
              label={t(lang, "cfg_delete")}
              variant="danger"
              onClick={() => void removeDistance(row.original)}
              icon={<DeleteIcon />}
            />
          </div>
        ),
      },
    ],
    [lang],
  );

  if (!isAdmin) return <p className="p-4 text-sm text-gray-500">{t(lang, "cfg_admin_only")}</p>;

  const tab = (active: boolean) =>
    `px-3 py-1 rounded text-sm font-medium ${active ? "bg-weber-blue text-white" : "bg-gray-200 hover:bg-gray-300"}`;

  const modalTitle = editing?.kind === "kit" ? t(lang, "cfg_kits") : t(lang, "cfg_distances");
  const visibleDistances = distanceSubsidiary
    ? distances.filter((distance) => distance.subsidiary_id === distanceSubsidiary)
    : distances;

  return (
    <div className="flex h-full min-h-0 w-full flex-col gap-3 p-4">
      <h1 className="shrink-0 text-2xl font-bold text-gray-900">{t(lang, "cfg_title")}</h1>
      <div className="flex shrink-0 gap-2">
        {(["rates", "distances", "kits"] as Section[]).map((s) => (
          <button key={s} onClick={() => setSection(s)} className={tab(section === s)}>
            {t(lang, s === "rates" ? "cfg_rates" : s === "distances" ? "cfg_distances" : "cfg_kits")}
          </button>
        ))}
      </div>
      {error && <p className="shrink-0 text-sm text-red-600 bg-white rounded shadow p-2">{error}</p>}
      {ok && <p className="shrink-0 text-sm text-green-700 bg-white rounded shadow p-2">{ok}</p>}

      {section === "rates" && (
        <SectionCard title={t(lang, "cfg_rates")}>
          <div className="flex gap-2 items-center flex-wrap">
            <select
              value={sub}
              onChange={(e) => {
                setSub(e.target.value);
                setRates(EMPTY_RATES);
                setError(null);
                setOk(null);
              }}
              className={input}
            >
              <option value="">{t(lang, "cfg_select_subsidiary")}</option>
              {subsidiaries.map((subsidiary) => (
                <option key={subsidiary.name} value={subsidiary.name}>
                  {subsidiary.name}
                </option>
              ))}
            </select>
            <Button variant="secondary" size="sm" onClick={loadRates}>Load</Button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-2">
            {(Object.keys(rates) as (keyof typeof rates)[]).map((k) => (
              <label key={k} className="text-xs">
                {t(lang, `cfg_${k}` as "cfg_currency" | "cfg_km_rate" | "cfg_tech_rate" | "cfg_diet_full_rate" | "cfg_diet_half_rate" | "cfg_hotel_rate" | "cfg_discount_rate")}
                <input
                  type={k === "currency" ? "text" : "number"}
                  min={k === "currency" ? undefined : "0"}
                  step={k === "currency" ? undefined : "any"}
                  value={rates[k]}
                  onChange={(e) => setRates({ ...rates, [k]: e.target.value })}
                  className={`${input} w-full`}
                />
              </label>
            ))}
          </div>
          <Button size="sm" className="mt-2" onClick={saveRates}>
            {t(lang, "cfg_save")}
          </Button>
        </SectionCard>
      )}

      {section === "distances" && (
        <SectionCard className="flex min-h-0 flex-1 flex-col" title={t(lang, "cfg_distances")}>
          <div className="mb-2 flex shrink-0 flex-wrap items-center gap-2">
            <label className="text-xs font-medium text-gray-600">
              Subsidiary
              <select
                value={distanceSubsidiary}
                onChange={(e) => setDistanceSubsidiary(e.target.value)}
                disabled={scope !== null}
                className={`${input} ml-2 disabled:bg-gray-100`}
              >
                <option value="">All subsidiaries</option>
                {subsidiaries.map((subsidiary) => (
                  <option key={subsidiary.name} value={subsidiary.name}>
                    {subsidiary.name}
                  </option>
                ))}
              </select>
            </label>
            <Button size="sm" onClick={newDistance}>
              {t(lang, "cfg_add")}
            </Button>
            {distanceSubsidiary === "Weber Italy" && (
              <Button size="sm" variant="secondary" onClick={() => setImportOpen(true)}>
                {t(lang, "cfg_distance_import")}
              </Button>
            )}
          </div>
          <DataTable
            data={visibleDistances}
            columns={distanceColumns}
            getRowId={(d) => `${d.subsidiary_id}:${d.province}`}
            tableClassName="min-w-[1250px]"
            className="min-h-0 flex-1"
          />
        </SectionCard>
      )}

      {section === "kits" && (
        <SectionCard title={t(lang, "cfg_kits")}>
          <Button
            size="sm"
            className="mb-2"
            onClick={() => setEditing({ kind: "kit", model: "", hours: "", spares: "", isNew: true })}
          >
            {t(lang, "cfg_add")}
          </Button>
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
                  <td className="px-3 py-1.5">
                    <div className="flex justify-end gap-1">
                      <IconButton
                        label={t(lang, "cfg_edit")}
                        onClick={() => setEditing({ kind: "kit", model: k.model, hours: k.workload_basic_kit, spares: k.spare_parts, isNew: false })}
                        icon={<EditIcon />}
                      />
                      <IconButton
                        label={t(lang, "cfg_delete")}
                        variant="danger"
                        onClick={async () => {
                          await deleteKit(k.model).catch((e) => setError(String(e)));
                          await refreshTables();
                        }}
                        icon={<DeleteIcon />}
                      />
                    </div>
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
                  {t(lang, "cfg_subsidiary")}
                  <select
                    value={editing.subsidiary_id}
                    disabled={scope !== null}
                    onChange={(e) => setEditing({ ...editing, subsidiary_id: e.target.value })}
                    className={`${input} w-full disabled:bg-gray-100`}
                  >
                    <option value="">Select subsidiary</option>
                    {subsidiaries.map((subsidiary) => (
                      <option key={subsidiary.name} value={subsidiary.name}>
                        {subsidiary.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="block text-xs">
                  {t(lang, "cfg_province")}
                  <input required value={editing.province} onChange={(e) => setEditing({ ...editing, province: e.target.value })} className={`${input} w-full`} />
                </label>
                <label className="block text-xs">
                  {t(lang, "cfg_province_code")}
                  <input value={editing.province_code} onChange={(e) => setEditing({ ...editing, province_code: e.target.value })} className={`${input} w-full`} />
                </label>
                <label className="block text-xs">
                  {t(lang, "cfg_region")}
                  <input value={editing.region} onChange={(e) => setEditing({ ...editing, region: e.target.value })} className={`${input} w-full`} />
                </label>
                {editing.subsidiary_id === "Weber Italy" ? (
                  <>
                    <label className="block text-xs">
                      {t(lang, "cfg_reference_city")}
                      <input value={editing.reference_city} onChange={(e) => setEditing({ ...editing, reference_city: e.target.value })} className={`${input} w-full`} />
                    </label>
                    <label className="block text-xs">
                      {t(lang, "cfg_origin_city")}
                      <input value={editing.origin_city} onChange={(e) => setEditing({ ...editing, origin_city: e.target.value })} className={`${input} w-full`} />
                    </label>
                  </>
                  ) : (
                  <>
                    <label className="block text-xs">
                      {t(lang, "cfg_reference_city")}
                      <input value={editing.capital} onChange={(e) => setEditing({ ...editing, capital: e.target.value })} className={`${input} w-full`} />
                    </label>
                    <label className="block text-xs">
                      {t(lang, "cfg_origin_city")}
                      {editing.subsidiary_id === "Weber Germany" ? (
                        <select
                          value={editing.service_center}
                          onChange={(e) => setEditing({ ...editing, service_center: e.target.value })}
                          className={`${input} w-full`}
                        >
                          <option value="">Select service center</option>
                          {GERMAN_SERVICE_CENTERS.map((center) => (
                            <option key={center} value={center}>{center}</option>
                          ))}
                        </select>
                      ) : (
                        <input value={editing.service_center} onChange={(e) => setEditing({ ...editing, service_center: e.target.value })} className={`${input} w-full`} />
                      )}
                    </label>
                  </>
                )}
                <label className="block text-xs">
                  {t(lang, "cfg_road_km")}
                  <input required type="number" min="0" step="0.1" value={editing.km} onChange={(e) => setEditing({ ...editing, km: e.target.value })} className={`${input} w-full`} />
                </label>
                <label className="block text-xs">
                  {t(lang, "cfg_driving_time")}
                  <input placeholder="h:mm" value={editing.driving} onChange={(e) => setEditing({ ...editing, driving: e.target.value })} className={`${input} w-full`} />
                </label>
                <label className="block text-xs">
                  {t(lang, "cfg_total_trip_time")}
                  <input required placeholder="h:mm" value={editing.trip} onChange={(e) => setEditing({ ...editing, trip: e.target.value })} className={`${input} w-full`} />
                </label>
                <label className="block text-xs">
                  {t(lang, "cfg_itinerary")}
                  <input maxLength={255} value={editing.itinerary} onChange={(e) => setEditing({ ...editing, itinerary: e.target.value })} className={`${input} w-full`} />
                </label>
                <label className="block text-xs">
                  {t(lang, "cfg_route_date")}
                  <input type="date" value={editing.route_date} onChange={(e) => setEditing({ ...editing, route_date: e.target.value })} className={`${input} w-full`} />
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
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="secondary" size="sm" onClick={() => setEditing(null)}>
                {t(lang, "cfg_cancel")}
              </Button>
              <Button size="sm" onClick={saveModal}>
                {t(lang, "cfg_save")}
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {importOpen && (
        <Modal
          title={t(lang, "cfg_distance_import")}
          onClose={() => setImportOpen(false)}
          widthClass="max-w-xl"
        >
          <DistanceImport
            lang={lang}
            subsidiaryId={distanceSubsidiary}
            onImported={refreshTables}
          />
        </Modal>
      )}
    </div>
  );
}
