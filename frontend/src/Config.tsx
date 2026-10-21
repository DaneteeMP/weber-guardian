import { useEffect, useMemo, useState } from "react";
import type { ColumnDef } from "@tanstack/react-table";
import DistanceImport from "./DistanceImport";
import ImportData from "./ImportData";
import {
  createResponsible,
  createSubsidiaryCountry,
  deleteDistance,
  deleteResponsible,
  getSubsidiaryStats,
  listDistances,
  listResponsibles,
  listSubsidiaryCountries,
  listUnassignedCountries,
  getPrices,
  listSubsidiaries,
  moveSubsidiaryCountry,
  updatePrices,
  updateResponsible,
  upsertDistance,
  type Distance,
  type Responsible,
  type Subsidiary,
  type SubsidiaryCountry,
  type SubsidiaryStats,
  type UnassignedCountry,
} from "./api";
import Button from "./components/Button";
import DataTable from "./components/DataTable";
import IconButton from "./components/IconButton";
import Modal from "./components/Modal";
import SearchInput from "./components/SearchInput";
import SectionCard from "./components/SectionCard";
import { matchesQuery } from "./components/searchQuery";
import { ToastStack, useToasts } from "./components/Toasts";
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

// The import panel lives inside the rates screen (same row), so there is no
// separate "import" section.
type Section = "rates" | "distances" | "countries";
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

// Admin-only per-subsidiary configuration: rates and distances.
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
  const { toasts, push, dismiss } = useToasts();
  const [editing, setEditing] = useState<Editing>(null);
  const [subsidiaries, setSubsidiaries] = useState<Subsidiary[]>([]);

  const [sub, setSub] = useState(scope ?? "Weber Iberica");
  const [rates, setRates] = useState(EMPTY_RATES);

  const [distances, setDistances] = useState<Distance[]>([]);
  const [distanceSubsidiary, setDistanceSubsidiary] = useState(scope ?? "");
  const [importOpen, setImportOpen] = useState(false);

  const [responsibles, setResponsibles] = useState<Responsible[]>([]);
  const [newResponsible, setNewResponsible] = useState("");
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renamingName, setRenamingName] = useState("");

  // Country supervision mapping: global admins only (backend enforces 403).
  const isGlobalAdmin = isAdmin && scope === null;
  const [countries, setCountries] = useState<SubsidiaryCountry[]>([]);
  const [newCountry, setNewCountry] = useState("");
  const [newCountrySubsidiary, setNewCountrySubsidiary] = useState("");
  // Filter by subsidiary: "" = every country, otherwise only the ones the
  // selected subsidiary has assigned.
  const [countryFilter, setCountryFilter] = useState("");
  const [countryStats, setCountryStats] = useState<SubsidiaryStats[]>([]);
  const [unassigned, setUnassigned] = useState<UnassignedCountry[]>([]);
  // Destination subsidiary for the "assign country to subsidiary" flow:
  // picked once at the top, then every row pushes its country into it.
  const [assignTarget, setAssignTarget] = useState("");
  // First card, two views: counters per subsidiary or the editable country map.
  const [countryView, setCountryView] = useState<"subsidiary" | "country">("country");
  // The country view keeps a button only: the form lives in this modal.
  const [countryAddOpen, setCountryAddOpen] = useState(false);
  // Free-text search over country and subsidiary names in the country view.
  const [countrySearch, setCountrySearch] = useState("");

  const input = "border rounded px-2 py-1 text-sm";

  async function refreshTables() {
    try {
      setDistances(await listDistances());
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
                currency: p.currency ?? "",
                km_rate: p.km_rate ?? "",
                tech_rate: p.tech_rate ?? "",
                diet_full_rate: p.diet_full_rate ?? "",
                diet_half_rate: p.diet_half_rate ?? "",
                hotel_rate: p.hotel_rate ?? "",
                discount_rate: p.discount_rate ?? "",
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
        currency: p.currency ?? "",
        km_rate: p.km_rate ?? "",
        tech_rate: p.tech_rate ?? "",
        diet_full_rate: p.diet_full_rate ?? "",
        diet_half_rate: p.diet_half_rate ?? "",
        hotel_rate: p.hotel_rate ?? "",
        discount_rate: p.discount_rate ?? "",
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
      if (Object.values(rates).some((value) => !String(value ?? "").trim()))
        throw new Error(t(lang, "cfg_rates_required"));
      await updatePrices(sub, rates);
      setOk("OK");
    } catch (e) {
      setError(String(e));
    }
  }

  async function loadResponsibles(target = sub) {
    setError(null);
    try {
      if (!target) throw new Error(t(lang, "cfg_select_subsidiary"));
      setResponsibles(await listResponsibles(target));
    } catch (e) {
      setError(String(e));
    }
  }

  async function addResponsible() {
    setError(null);
    setOk(null);
    try {
      if (!sub) throw new Error(t(lang, "cfg_select_subsidiary"));
      if (!newResponsible.trim()) return;
      await createResponsible(sub, newResponsible.trim());
      setNewResponsible("");
      setOk("OK");
      await loadResponsibles();
    } catch (e) {
      setError(String(e));
    }
  }

  async function renameResponsible(id: string) {
    setError(null);
    setOk(null);
    try {
      if (!renamingName.trim()) return;
      await updateResponsible(id, { name: renamingName.trim() });
      setRenamingId(null);
      setOk("OK");
      await loadResponsibles();
    } catch (e) {
      setError(String(e));
    }
  }

  async function toggleResponsible(row: Responsible) {
    setError(null);
    try {
      await updateResponsible(row.id, { active: !row.active });
      await loadResponsibles();
    } catch (e) {
      setError(String(e));
    }
  }

  async function removeResponsible(id: string) {
    if (!window.confirm(t(lang, "cfg_delete"))) return;
    setError(null);
    try {
      await deleteResponsible(id);
      await loadResponsibles();
    } catch (e) {
      setError(String(e));
    }
  }

  // Loads the whole countries tab: the map, the per-subsidiary counters and
  // the countries outside the map. Re-run after every mutation so the three
  // views never disagree.
  async function loadCountryData() {
    setError(null);
    try {
      const [map, stats, un] = await Promise.all([
        listSubsidiaryCountries(),
        getSubsidiaryStats(),
        listUnassignedCountries(),
      ]);
      setCountries(map);
      setCountryStats(stats);
      setUnassigned(un);
    } catch (e) {
      setError(String(e));
    }
  }

  async function addCountry() {
    setError(null);
    setOk(null);
    try {
      const name = newCountry.trim();
      if (!name) throw new Error(t(lang, "cfg_country_required"));
      if (!newCountrySubsidiary) throw new Error(t(lang, "cfg_select_subsidiary"));
      await createSubsidiaryCountry(name, newCountrySubsidiary);
      setNewCountry("");
      setCountryAddOpen(false);
      setOk(t(lang, "cfg_country_added"));
      await loadCountryData();
    } catch (e) {
      setError(String(e));
    }
  }

  // Cover an unmapped country: extend the map only. Customer rows keep the
  // subsidiary the import tagged them with (retagging is a separate decision).
  // The destination stays selected after success so a batch of countries can
  // be pushed to the same subsidiary one after another.
  async function assignCountry(country: string) {
    if (!assignTarget) return;
    setError(null);
    setOk(null);
    try {
      await createSubsidiaryCountry(country, assignTarget);
      setOk(t(lang, "cfg_country_added"));
      await loadCountryData();
    } catch (e) {
      setError(String(e));
    }
  }

  async function changeCountrySubsidiary(country: string, subsidiary: string) {
    setError(null);
    setOk(null);
    try {
      await moveSubsidiaryCountry(country, subsidiary);
      setOk(t(lang, "cfg_country_updated"));
      await loadCountryData();
    } catch (e) {
      setError(String(e));
    }
  }

  useEffect(() => {
    if (isGlobalAdmin) void loadCountryData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isGlobalAdmin]);

  useEffect(() => {
    if (!isGlobalAdmin && section === "countries") setSection("rates");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isGlobalAdmin, section]);

  useEffect(() => {
    if (isAdmin && section === "rates") void loadResponsibles();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin, section, sub]);

  // Legacy banner states surface as overlay toasts, so call sites stay untouched.
  useEffect(() => {
    if (error) {
      push("error", error);
      setError(null);
    }
  }, [error, push]);
  useEffect(() => {
    if (ok) {
      push("success", ok);
      setOk(null);
    }
  }, [ok, push]);

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

  const countryStatsColumns: ColumnDef<SubsidiaryStats>[] = useMemo(
    () => [
      {
        accessorKey: "short_label",
        header: t(lang, "cfg_country_subsidiary"),
        enableSorting: true,
        cell: ({ row }) => (
          <span>
            <span className="font-semibold">{row.original.short_label}</span>{" "}
            <span className="text-xs text-gray-500">{row.original.name}</span>
          </span>
        ),
      },
      {
        accessorKey: "countries",
        header: () => <span className="block text-right">{t(lang, "cfg_countries_count")}</span>,
        enableSorting: true,
        cell: ({ row }) => (
          <span className="block text-right font-mono">{row.original.countries}</span>
        ),
      },
      {
        accessorKey: "customers",
        header: () => <span className="block text-right">{t(lang, "dash_customers")}</span>,
        enableSorting: true,
        cell: ({ row }) => (
          <span className="block text-right font-mono">{row.original.customers.toLocaleString()}</span>
        ),
      },
    ],
    [lang],
  );

  const unassignedColumns: ColumnDef<UnassignedCountry>[] = useMemo(
    () => [
      {
        accessorKey: "country",
        header: t(lang, "cfg_country"),
        enableSorting: true,
        cell: ({ row }) => <span className="font-medium">{row.original.country}</span>,
      },
      {
        accessorKey: "count",
        header: () => <span className="block text-right">{t(lang, "dash_customers")}</span>,
        enableSorting: true,
        cell: ({ row }) => (
          <span className="block text-right font-mono">{row.original.count.toLocaleString()}</span>
        ),
      },
      {
        id: "actions",
        header: "",
        enableSorting: false,
        cell: ({ row }) => (
          <div className="flex items-center justify-end">
            <Button
              size="sm"
              disabled={!assignTarget}
              title={!assignTarget ? t(lang, "cfg_select_subsidiary") : undefined}
              onClick={() => void assignCountry(row.original.country)}
            >
              {t(lang, "cfg_country_assign")}
            </Button>
          </div>
        ),
      },
    ],
    // assignTarget is part of the render contract: the row button enables with it.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [lang, assignTarget],
  );

  const countryColumns: ColumnDef<SubsidiaryCountry>[] = useMemo(
    () => [
      {
        accessorKey: "country",
        header: t(lang, "cfg_country"),
        enableSorting: true,
        cell: ({ row }) => <span className="font-medium">{row.original.country}</span>,
      },
      {
        accessorKey: "subsidiary",
        header: t(lang, "cfg_country_subsidiary"),
        enableSorting: true,
        cell: ({ row }) => (
          <select
            value={row.original.subsidiary}
            onChange={(event) => changeCountrySubsidiary(row.original.country, event.target.value)}
            className={input}
          >
            {subsidiaries.map((s) => (
              <option key={s.name} value={s.name}>{s.name}</option>
            ))}
          </select>
        ),
      },
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [lang, subsidiaries],
  );

  if (!isAdmin) return <p className="p-4 text-sm text-gray-500">{t(lang, "cfg_admin_only")}</p>;

  const tab = (active: boolean) =>
    `px-3 py-1 rounded text-sm font-medium ${active ? "bg-weber-blue text-white" : "bg-gray-200 hover:bg-gray-300"}`;

  const modalTitle = t(lang, "cfg_distances");
  const visibleDistances = distanceSubsidiary
    ? distances.filter((distance) => distance.subsidiary_id === distanceSubsidiary)
    : distances;
  // Same filter shape as distances: pick a subsidiary to list its countries,
  // then narrow the list by free text (country or subsidiary name).
  const countryQuery = countrySearch.trim();
  const visibleCountries = countries.filter(
    (country) =>
      (!countryFilter || country.subsidiary === countryFilter) &&
      (!countryQuery || matchesQuery(countryQuery, country.country, country.subsidiary)),
  );

  const sectionLabel: Record<Section, string> = {
    rates: t(lang, "cfg_rates"),
    distances: t(lang, "cfg_distances"),
    countries: t(lang, "cfg_countries"),
  };
  const visibleSections: Section[] = isGlobalAdmin
    ? ["rates", "distances", "countries"]
    : ["rates", "distances"];

  return (
    <div className="flex h-full min-h-0 w-full flex-col gap-3 p-4">
      <h1 className="shrink-0 text-2xl font-bold text-gray-900">{t(lang, "cfg_title")}</h1>
      <div className="flex shrink-0 gap-2">
        {visibleSections.map((s) => (
          <button key={s} onClick={() => setSection(s)} className={tab(section === s)}>
            {sectionLabel[s]}
          </button>
        ))}
      </div>
      <ToastStack toasts={toasts} onClose={dismiss} />

      {section === "rates" && (
        <div className="min-h-0 flex-1 overflow-y-auto pb-1">
        <div className="flex flex-col gap-3">
        <div className="flex flex-col gap-3 md:flex-row md:items-start">
        <SectionCard
          title={t(lang, "cfg_rates")}
          className="min-w-0 md:flex-[2]"
        >
          <div className="flex shrink-0 flex-wrap items-center gap-2">
            <span className="min-w-0 flex-1 truncate text-sm font-medium text-gray-700">{sub}</span>
            <Button variant="secondary" size="sm" onClick={loadRates}>
              {t(lang, "cfg_load")}
            </Button>
            <Button size="sm" onClick={saveRates}>
              {t(lang, "cfg_save")}
            </Button>
          </div>
          <div className="mt-3 grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
            {(Object.keys(rates) as (keyof typeof rates)[]).map((k) => (
              <label key={k} className="flex items-center justify-between gap-3 text-xs">
                <span className="truncate text-gray-600">
                  {t(lang, `cfg_${k}` as "cfg_currency" | "cfg_km_rate" | "cfg_tech_rate" | "cfg_diet_full_rate" | "cfg_diet_half_rate" | "cfg_hotel_rate" | "cfg_discount_rate")}
                </span>
                <input
                  type={k === "currency" ? "text" : "number"}
                  min={k === "currency" ? undefined : "0"}
                  step={k === "currency" ? undefined : "any"}
                  value={rates[k]}
                  onChange={(e) => setRates({ ...rates, [k]: e.target.value })}
                  className={`${input} w-28 shrink-0 text-right`}
                />
              </label>
            ))}
          </div>
        </SectionCard>

        <SectionCard
          title={t(lang, "cfg_responsibles")}
          className="min-w-0 md:flex-1"
        >
          <div className="flex gap-2 items-center">
            <input
              value={newResponsible}
              onChange={(e) => setNewResponsible(e.target.value)}
              placeholder={t(lang, "cfg_responsible_name")}
              maxLength={128}
              className={`${input} min-w-0 flex-1`}
            />
            <Button size="sm" onClick={addResponsible}>{t(lang, "cfg_add")}</Button>
          </div>
          <ul className="mt-2 space-y-1">
            {responsibles.map((r) => (
              <li key={r.id} className="flex flex-wrap items-center gap-2 text-sm">
                {renamingId === r.id ? (
                  <>
                    <input
                      value={renamingName}
                      onChange={(e) => setRenamingName(e.target.value)}
                      maxLength={128}
                      className={`${input} min-w-0 flex-1`}
                    />
                    <Button size="sm" onClick={() => renameResponsible(r.id)}>{t(lang, "cfg_save")}</Button>
                    <Button size="sm" variant="secondary" onClick={() => setRenamingId(null)}>{t(lang, "cfg_cancel")}</Button>
                  </>
                ) : (
                  <>
                    <input
                      type="checkbox"
                      checked={r.active}
                      onChange={() => toggleResponsible(r)}
                      title={t(lang, "cfg_active")}
                      className="accent-blue-700"
                    />
                    <span className={`min-w-0 flex-1 truncate ${r.active ? "text-gray-900" : "text-gray-400 line-through"}`}>{r.name}</span>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => {
                        setRenamingId(r.id);
                        setRenamingName(r.name);
                      }}
                    >
                      {t(lang, "cfg_edit")}
                    </Button>
                    <Button size="sm" variant="danger" onClick={() => removeResponsible(r.id)}>
                      {t(lang, "cfg_delete")}
                    </Button>
                  </>
                )}
              </li>
            ))}
          </ul>
        </SectionCard>
        </div>

        {/* Import panel below the rates: it shares the screen but keeps its
            own full-width card, because the format help needs the room. */}
        <ImportData lang={lang} scope={scope} />
        </div>
        </div>
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

      {section === "countries" && isGlobalAdmin && (
        <div className="flex min-h-0 flex-1 flex-col gap-3 md:flex-row">
          <SectionCard
            title={t(lang, "cfg_countries")}
            className="flex min-h-0 min-w-0 flex-1 flex-col md:flex-[2]"
          >
            <div className="mb-2 flex shrink-0 overflow-hidden rounded border text-sm">
              <button
                type="button"
                onClick={() => setCountryView("subsidiary")}
                className={`px-3 py-1.5 ${
                  countryView === "subsidiary"
                    ? "bg-weber-blue font-semibold text-white"
                    : "bg-white hover:bg-gray-50"
                }`}
              >
                {t(lang, "cfg_country_view_subsidiary")}
              </button>
              <button
                type="button"
                onClick={() => setCountryView("country")}
                className={`px-3 py-1.5 ${
                  countryView === "country"
                    ? "bg-weber-blue font-semibold text-white"
                    : "bg-white hover:bg-gray-50"
                }`}
              >
                {t(lang, "cfg_country_view_country")}
              </button>
            </div>

            {countryView === "subsidiary" ? (
              <DataTable
                data={countryStats}
                columns={countryStatsColumns}
                getRowId={(row) => row.name}
                tableClassName="min-w-[480px]"
              />
            ) : (
              <>
                <p className="mb-2 shrink-0 text-xs text-gray-500">{t(lang, "cfg_countries_hint")}</p>
                <div className="mb-2 flex shrink-0 items-center gap-2">
                  <select
                    value={countryFilter}
                    onChange={(e) => setCountryFilter(e.target.value)}
                    aria-label={t(lang, "cfg_country_subsidiary")}
                    className={`${input} w-56`}
                  >
                    <option value="">{t(lang, "cfg_country_filter_all")}</option>
                    {subsidiaries.map((s) => (
                      <option key={s.name} value={s.name}>{s.name}</option>
                    ))}
                  </select>
                  <span className="text-sm text-gray-500">
                    {countryFilter || countryQuery
                      ? `${visibleCountries.length} / ${countries.length}`
                      : countries.length}
                  </span>
                  <span className="flex-1" />
                  <Button size="sm" onClick={() => setCountryAddOpen(true)}>
                    {t(lang, "cfg_country_add")}
                  </Button>
                </div>
                <SearchInput
                  value={countrySearch}
                  onChange={setCountrySearch}
                  placeholder={t(lang, "cfg_country_search")}
                  className="mb-2 shrink-0"
                />
                <DataTable
                  data={visibleCountries}
                  columns={countryColumns}
                  getRowId={(row) => row.country}
                  emptyText={t(lang, "cfg_countries_none")}
                  tableClassName="min-w-[520px]"
                />
              </>
            )}
          </SectionCard>

          <SectionCard
            title={`${t(lang, "cfg_country_unassigned")} (${unassigned.length})`}
            className="flex min-h-0 min-w-0 flex-1 flex-col"
          >
            <div className="mb-2 flex shrink-0 items-center gap-2">
              <span className="shrink-0 text-xs text-gray-500">
                {t(lang, "cfg_country_subsidiary")}
              </span>
              <select
                value={assignTarget}
                onChange={(e) => setAssignTarget(e.target.value)}
                aria-label={t(lang, "cfg_country_subsidiary")}
                className={`${input} min-w-0 flex-1`}
              >
                <option value="">{t(lang, "cfg_select_subsidiary")}</option>
                {subsidiaries.map((s) => (
                  <option key={s.name} value={s.name}>{s.name}</option>
                ))}
              </select>
            </div>
            <DataTable
              data={unassigned}
              columns={unassignedColumns}
              getRowId={(row) => row.country}
              emptyText={t(lang, "cfg_countries_covered")}
              tableClassName="min-w-[340px]"
            />
          </SectionCard>
        </div>
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

      {countryAddOpen && (
        <Modal
          title={t(lang, "cfg_country_add_title")}
          onClose={() => setCountryAddOpen(false)}
          widthClass="max-w-sm"
        >
          <div className="space-y-2">
            <label className="block text-xs">
              {t(lang, "cfg_country_subsidiary")}
              <select
                value={newCountrySubsidiary}
                onChange={(e) => setNewCountrySubsidiary(e.target.value)}
                className={`${input} mt-1 w-full`}
              >
                <option value="">{t(lang, "cfg_select_subsidiary")}</option>
                {subsidiaries.map((s) => (
                  <option key={s.name} value={s.name}>{s.name}</option>
                ))}
              </select>
            </label>
            <label className="block text-xs">
              {t(lang, "cfg_country")}
              <input
                value={newCountry}
                onChange={(e) => setNewCountry(e.target.value)}
                placeholder={t(lang, "cfg_country")}
                maxLength={128}
                autoFocus
                className={`${input} mt-1 w-full`}
              />
            </label>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="secondary" size="sm" onClick={() => setCountryAddOpen(false)}>
                {t(lang, "cfg_cancel")}
              </Button>
              <Button size="sm" onClick={addCountry}>{t(lang, "cfg_country_add")}</Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
