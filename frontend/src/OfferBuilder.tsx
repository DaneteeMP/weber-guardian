import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { type ColumnDef } from "@tanstack/react-table";
import {
  calculate,
  closeOffer,
  createOffer,
  deleteOffer,
  downloadOfferPdf,
  getCustomerDetail,
  getOffer,
  getOffersSummary,
  getPrices,
  listAllCustomers,
  listAllOffers,
  listOffers,
  maintenanceDraft,
  updateOffer,
  type Breakdown,
  type Customer,
  type CustomerDetail,
  type Equipment,
  type OfferListItem,
  type OffersSummary,
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

const money = (v: string | number | null | undefined) =>
  Number(v ?? 0).toLocaleString("en-GB", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

const day = (v: string | null | undefined) => (v ? v.slice(0, 10) : "");

// ISO day (yyyy-mm-dd) for <input type="date">. Built from local parts, not
// toISOString, which would shift the day for any timezone behind UTC.
const todayIso = () => {
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
};

const GUARDIAN_TYPES = ["Basic Kit", "Audit", "Off-Guardian", "Campaign"];
const FREQUENCIES = ["Annual", "Semi-annual", "Biennial"];
const STATUSES = ["Pending response", "Accepted", "In progress", "Pending invoicing", "Finished", "Rejected", "Cancelled", "Pending Service"];
const RESPONSIBLES = ["", "Xevi Mira", "David"];
const GUARDIAN_SCOPE = [
  {
    id: "maintenance_inspection",
    label: "Maintenance & Inspection",
    options: [
      ["inspection", "Inspection / Annual Inspection"],
      ["machine_checklist", "Machine Checklist"],
      ["inspection_report", "Inspection Report"],
      ["preventive_maintenance", "Preventive Maintenance"],
      ["maintenance_kit", "Spare Parts / Maintenance Kit"],
    ],
  },
  {
    id: "service_support",
    label: "Service Support",
    options: [
      ["standard_hotline", "Standard Hotline"],
      ["remote_support", "Remote Support"],
      ["priority_response", "Priority Response"],
    ],
  },
  {
    id: "parts_availability",
    label: "Parts & Availability",
    options: [
      ["parts_discount", "Parts Discount"],
      ["priority_handling", "Priority Handling"],
      ["recommended_parts_list", "Recommended Parts List"],
    ],
  },
  {
    id: "blade_solutions",
    label: "Blade Solutions",
    options: [
      ["blade_discount", "Blade Discount"],
      ["stock_agreement", "Stock Agreement"],
      ["sharpening_assessment", "Sharpening Assessment"],
      ["blade_application_review", "Blade Application Review"],
    ],
  },
  {
    id: "training_optimization",
    label: "Training & Optimization",
    options: [
      ["operator_training", "Operator Training"],
      ["maintenance_training", "Maintenance Training"],
      ["line_optimization", "Line Optimization"],
      ["epip_audit", "EPIP Audit"],
    ],
  },
  {
    id: "digital_services",
    label: "Digital Services",
    options: [
      ["factory_cockpit", "Factory Cockpit"],
      ["performance_review", "Performance Review"],
      ["mro_review", "MRO Review"],
      ["dedicated_account_team", "Dedicated Account Team"],
    ],
  },
] as const;

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
  onEdit,
  onNew,
}: {
  lang: Lang;
  editingOfferId: string | null;
  onDone: () => void;
  onEdit?: (offerId: string) => void;
  onNew?: () => void;
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
  const [discountRate, setDiscountRate] = useState("0");
  const [offerNumber, setOfferNumber] = useState("");
  const [offerDate, setOfferDate] = useState(todayIso());
  const [frequency, setFrequency] = useState("Annual");
  const [status, setStatus] = useState("Pending response");
  const [responsible, setResponsible] = useState("");
  const [guardianType, setGuardianType] = useState("Audit");
  const [guardianSelections, setGuardianSelections] = useState<string[]>([]);
  const [comments, setComments] = useState("");
  type QuoteLine = CatalogQuoteLine;
  const [items, setItems] = useState<QuoteLine[]>([]);
  const [offers, setOffers] = useState<OfferListItem[]>([]);
  const [savedOffer, setSavedOffer] = useState<{ id: string; status: string } | null>(null);
  const [equipList, setEquipList] = useState<Equipment[]>([]);
  const [equipmentLoading, setEquipmentLoading] = useState(false);
  const [selectedEquip, setSelectedEquip] = useState<string[]>([]);
  const [editStatus, setEditStatus] = useState<string | null>(null);
  // Sidebar offers panel: every offer in scope, filterable by status. Selecting
  // one hands the id back to App, which reopens OfferBuilder in edit mode.
  const [offerList, setOfferList] = useState<OfferListItem[]>([]);
  const [offerListLoading, setOfferListLoading] = useState(false);
  const [offerStatusFilter, setOfferStatusFilter] = useState("");
  const [offerSummary, setOfferSummary] = useState<OffersSummary | null>(null);
  // Machines to tick in the picker once the customer's fleet finishes loading
  // in edit mode, so an existing offer reopens with the machines it was made
  // with instead of an empty selection.
  const restoreEquipRef = useRef<string[] | null>(null);

  // The selected component workloads are the authoritative work-hours input
  // for the existing offer pricing engine; no manual work-hours box is needed.
  const workHours = useMemo(
    () => items.reduce((sum, item) => sum + num(item.workload, 0), 0).toFixed(2),
    [items],
  );

  // Fill the form from the stored offer. Trip inputs are reloaded from the
  // current subsidiary rates, while the remaining values come from the offer.
  useEffect(() => {
    if (!editingOfferId) return;
    getOffer(editingOfferId)
      .then((o) => {
        setCustomerId(o.customer_id);
        setOfferNumber(o.id_guardian_offer);
        // The API always returns a date; fall back to today only if an old row
        // somehow has no business date at all.
        setOfferDate(o.offer_date || todayIso());
        setStatus(o.status || "Pending response");
        setFrequency(o.inspection_frequency || "Annual");
        setResponsible(o.responsible_person || "");
        setComments(o.general_comments || "");
        setGuardianSelections(o.guardian_selections || []);
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
        // Remember the offer's machines so the picker re-ticks them once the
        // fleet loads, and treat their lines as picker-generated so unticking
        // one removes exactly the lines it brought in.
        const offerMachines = [
          ...new Set(o.items.map((i) => i.equipment).filter((name): name is string => !!name)),
        ];
        restoreEquipRef.current = offerMachines;
        prevSelected.current = offerMachines;
        setSelectedEquip(offerMachines);
        autoLines.current = new Set();
        for (const item of o.items) {
          if (item.equipment) autoLines.current.add(lineKey(item.equipment, item.description ?? ""));
        }
        setEditStatus(o.status || "Pending response");
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

  function toggleGuardianModule(moduleId: string, optionIds: readonly string[]) {
    setGuardianSelections((current) => {
      if (current.includes(moduleId)) {
        return current.filter((key) => key !== moduleId && !optionIds.includes(key));
      }
      return [...current, moduleId];
    });
  }

  function toggleGuardianOption(moduleId: string, optionId: string) {
    setGuardianSelections((current) => {
      const next = current.includes(optionId)
        ? current.filter((key) => key !== optionId)
        : [...current, optionId];
      return next.includes(moduleId) ? next : [...next, moduleId];
    });
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

  // Blank the offer-specific fields so the next save creates a new offer. The
  // selected customer is deliberately kept: choosing a customer IS starting a
  // new offer, and its fleet/rates load from the customer effect.
  function resetOfferFields() {
    setOfferNumber("");
    setOfferDate(todayIso());
    setStatus("Pending response");
    setFrequency("Annual");
    setResponsible("");
    setGuardianType("Audit");
    setComments("");
    setGuardianSelections([]);
    setReportHours("0");
    setTripBase("0");
    setItems([]);
    setSelectedEquip([]);
    setEditStatus(null);
    setSavedOffer(null);
    restoreEquipRef.current = null;
    autoLines.current = new Set();
    prevSelected.current = [];
  }

  // Picking a customer and picking an offer are mutually exclusive: the former
  // starts a new offer, the latter loads an existing one. Re-clicking the same
  // customer while already in new mode is a no-op so nothing is lost by accident.
  function selectCustomer(id: string) {
    if (id === customerId && !editingOfferId) return;
    setCustomerId(id);
    resetOfferFields();
    if (editingOfferId) onNew?.();
  }

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

  // Fleet of the selected customer. Keyed only by customerId, so a later
  // refresh of the customer list can never wipe a restored machine selection.
  useEffect(() => {
    let active = true;
    setSavedOffer(null);
    setKmRate("0");
    setTechRate("0");
    setDietFull("0");
    setDietHalf("0");
    setHotelRate("0");
    if (!customerId) {
      setCustomerDetail(null);
      setEquipList([]);
      setSelectedEquip([]);
      setEquipmentLoading(false);
      return () => {
        active = false;
      };
    }
    setEquipmentLoading(true);
    setCustomerDetail(null);
    setEquipList([]);
    setSelectedEquip([]);
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
        const restored = restoreEquipRef.current;
        if (restored) {
          // Reopening an offer: tick the machines it was made with and sync
          // the picker's baseline so the draft merge does not re-run for them.
          const available = new Set(equipmentRows.map((row) => row.equipment_name));
          const restoredAvailable = restored.filter((name) => available.has(name));
          prevSelected.current = restoredAvailable;
          setSelectedEquip(restoredAvailable);
          restoreEquipRef.current = null;
        } else {
          setSelectedEquip([]);
        }
        setEquipmentLoading(false);
      })
      .catch(() => {
        if (!active) return;
        setCustomerDetail(null);
        setEquipList([]);
        setSelectedEquip([]);
        setEquipmentLoading(false);
      });
    return () => {
      active = false;
    };
  }, [customerId]);

  // Customer identity, its offer history and the subsidiary rates. Re-runs when
  // the customer list arrives so the rates can be fetched once the filial is known.
  useEffect(() => {
    const selectedCustomer = customers.find((c) => c.customer_id === customerId) ?? null;
    setCustomer(selectedCustomer);
    if (!customerId) {
      setOffers([]);
      return;
    }
    listOffers(customerId).then(setOffers).catch(() => setOffers([]));
    if (!selectedCustomer?.subsidiary_id) return;
    let active = true;
    getPrices(selectedCustomer.subsidiary_id)
      .then((prices) => {
        if (!active) return;
        setKmRate(prices.km_rate);
        setTechRate(prices.tech_rate);
        setDietFull(prices.diet_full_rate);
        setDietHalf(prices.diet_half_rate);
        setHotelRate(prices.hotel_rate);
        setDiscountRate(prices.discount_rate);
      })
      .catch((e) => {
        if (active) setError(e instanceof Error ? e.message : String(e));
      });
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

  const customerNames = useMemo(
    () => Object.fromEntries(customers.map((c) => [c.customer_id, c.account_name])),
    [customers],
  );
  const offerStatuses = useMemo(() => offerSummary?.by_status ?? [], [offerSummary]);

  // Sidebar offers panel: the status options come from the same summary the
  // dashboard uses, so the dropdown reflects the real statuses in scope.
  useEffect(() => {
    getOffersSummary()
      .then(setOfferSummary)
      .catch(() => setOfferSummary(null));
  }, []);

  const loadOfferList = useCallback(() => {
    setOfferListLoading(true);
    listAllOffers(200, offerStatusFilter || undefined)
      .then(setOfferList)
      .catch(() => setOfferList([]))
      .finally(() => setOfferListLoading(false));
  }, [offerStatusFilter]);

  useEffect(loadOfferList, [loadOfferList]);

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
        discount_rate: num(discountRate, 0),
        bk_price: 0,
        currency: "EUR",
      })
        .then(setCalc)
        .catch((e) => setError(String(e)));
    }, 300);
    return () => clearTimeout(timer);
  }, [workHours, reportHours, tripBase, km, kmRate, techRate, dietFull, dietHalf, hotelRate, discountRate]);

  async function refreshOffers() {
    if (customerId) {
      await listOffers(customerId).then(setOffers).catch(() => {});
    }
    loadOfferList();
  }

  async function handleSave() {
    setError(null);
    setSaved(null);
    try {
      if (!customerId) throw new Error(t(lang, "ob_select_first"));
      // Unresolved modules stay flagged in the table and priced at 0.00; they
      // must not block saving the whole offer.
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
        discount_rate: num(discountRate, 0),
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
          inspection_frequency: frequency,
          general_comments: comments || undefined,
          offer_date: offerDate || undefined,
          guardian_selections: guardianSelections,
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
          inspection_frequency: frequency,
          general_comments: comments || undefined,
          offer_date: offerDate || undefined,
          guardian_selections: guardianSelections,
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

  // UI-only state: sidebar tab / visibility and the offers search box.
  const [sideTab, setSideTab] = useState<"offers" | "customers">(editingOfferId ? "offers" : "customers");
  const [sideOpen, setSideOpen] = useState(true);
  const [offerSearch, setOfferSearch] = useState("");

  const filteredOffers = useMemo(() => {
    const q = offerSearch.trim().toLowerCase();
    if (!q) return offerList;
    return offerList.filter(
      (o) =>
        (o.id_guardian_offer ?? "").toLowerCase().includes(q) ||
        (customerNames[o.customer_id] ?? o.customer_id).toLowerCase().includes(q),
    );
  }, [offerList, offerSearch, customerNames]);

  // The "saved" banner is a toast: it disappears on its own.
  useEffect(() => {
    if (!saved) return;
    const id = setTimeout(() => setSaved(null), 3000);
    return () => clearTimeout(id);
  }, [saved]);

  // Ctrl/Cmd+S saves. The ref keeps the listener registered once while always
  // calling the latest handleSave (it closes over the current form state).
  const saveRef = useRef(handleSave);
  saveRef.current = handleSave;
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        void saveRef.current();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  // Shared dense styles.
  const ctl =
    "h-7 w-full rounded border border-slate-300 bg-white px-1.5 text-xs focus:border-weber-blue focus:outline-none focus:ring-1 focus:ring-weber-blue";
  const btn =
    "inline-flex h-7 items-center gap-1.5 rounded border px-2.5 text-xs font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-40";
  const btnSoft = `${btn} border-slate-300 bg-white text-slate-700 hover:bg-slate-50`;
  const btnPrimary = `${btn} border-weber-blue bg-weber-blue text-white hover:opacity-90`;
  const btnDanger = `${btn} border-red-200 bg-white text-red-700 hover:bg-red-50`;

  const statusTone = (s: string | null | undefined) => {
    switch (s) {
      case "Finished":
        return "bg-green-100 text-green-800";
      case "Pending response":
        return "bg-amber-100 text-amber-800";
      case "Accepted":
      case "In progress":
        return "bg-blue-100 text-blue-800";
      case "Pending invoicing":
        return "bg-violet-100 text-violet-800";
      case "Pending Service":
        return "bg-cyan-100 text-cyan-800";
      case "Cancelled":
      case "Rejected":
        return "bg-red-100 text-red-800";
      default:
        return "bg-slate-100 text-slate-600";
    }
  };

  // Plain function (not a component) so inputs are not remounted on each render.
  const field = (label: string, control: ReactNode, span = "") => (
    <div className={`flex min-w-0 flex-col gap-0.5 ${span}`}>
      <span className="truncate text-[11px] font-medium text-slate-500">{label}</span>
      {control}
    </div>
  );

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
  const linesTotal = moduleRows.reduce((sum, r) => sum + r.amount, 0);
  const warningCount = moduleRows.filter((r) => r.catalogWarning).length;

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
              <span
                title={t(lang, "workload_title")}
                className="ml-2 rounded bg-amber-100 px-1.5 py-0.5 text-[10px] text-amber-800"
              >
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

  const customerAddress = customerDetail?.sites.length
    ? customerDetail.sites
        .map((site) =>
          [
            site.physical_street,
            [site.physical_postal_code, site.physical_city].filter(Boolean).join(" "),
            site.physical_province,
            site.physical_country,
          ]
            .filter(Boolean)
            .join(", "),
        )
        .join(" · ")
    : [customer?.city, customer?.province, customer?.country].filter(Boolean).join(", ") || "—";

  const scopeCount = GUARDIAN_SCOPE.filter((module) => guardianSelections.includes(module.id)).length;

  return (
    <div className="flex h-full min-h-0 flex-col bg-slate-100 text-xs text-slate-800">
      {/* ── Top bar: identity, live total and actions ─────────────────────── */}
      <header className="flex shrink-0 items-center justify-between gap-3 border-b border-slate-200 bg-white px-3 py-1.5 shadow-sm">
        <div className="flex min-w-0 items-center gap-2">
          <button
            type="button"
            onClick={() => setSideOpen((v) => !v)}
            aria-label="Toggle sidebar"
            aria-pressed={sideOpen}
            className="hidden h-7 w-7 items-center justify-center rounded border border-slate-300 text-slate-600 hover:bg-slate-50 lg:inline-flex"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} className="h-4 w-4" aria-hidden="true">
              <path d="M4 6h16M4 12h16M4 18h16" strokeLinecap="round" />
            </svg>
          </button>
          <h1 className="truncate text-base font-bold tracking-tight text-slate-900">Guardian Offers</h1>
          {editingOfferId && (
            <span className="truncate text-slate-500">
              {t(lang, "ob_editing")} <span className="font-mono font-semibold text-slate-700">{offerNumber}</span>
            </span>
          )}
          <span className={`shrink-0 rounded px-1.5 py-0.5 text-[11px] font-semibold ${statusTone(status)}`}>{status}</span>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <div className="mr-2 text-right leading-tight">
            <div className="text-[11px] text-slate-500">{t(lang, "ob_total_amount")}</div>
            <div className="font-mono text-sm font-bold text-blue-700">{calc ? eur(calc.total_end) : "—"}</div>
          </div>
          <button onClick={handlePrint} disabled={!savedOffer} title={t(lang, "ob_print")} aria-label={t(lang, "ob_print")} className={btnSoft}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} className="h-4 w-4" aria-hidden="true">
              <path d="M7 8V3h10v5M7 17H5a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M7 14h10v7H7z" strokeLinejoin="round" />
              <path d="M17 11h.01" strokeLinecap="round" />
            </svg>
            {t(lang, "ob_print")}
          </button>
          <button onClick={handleClose} disabled={!savedOffer} className={btnSoft}>
            {t(lang, "ob_close_offer")}
          </button>
          <button
            onClick={() => {
              if (window.confirm(`${t(lang, "ob_delete_offer")}: ${offerNumber}?`)) void handleDelete();
            }}
            disabled={!savedOffer}
            className={btnDanger}
          >
            {t(lang, "ob_delete_offer")}
          </button>
          <button onClick={handleSave} disabled={!customerId} title="Ctrl+S" className={btnPrimary}>
            {editingOfferId ? t(lang, "ob_update") : t(lang, "ob_save")}
          </button>
          <button onClick={onDone} className={btnSoft}>
            {t(lang, "ob_back")}
          </button>
        </div>
      </header>

      {/* ── Toasts: overlay, so they never push the layout around ─────────── */}
      <div className="pointer-events-none fixed bottom-3 right-3 z-50 flex max-w-sm flex-col gap-2">
        {error && (
          <div role="alert" className="pointer-events-auto flex items-start gap-2 rounded-lg border border-red-200 bg-white p-3 text-sm text-red-700 shadow-lg">
            <span className="min-w-0 flex-1 break-words">{error}</span>
            <button type="button" onClick={() => setError(null)} aria-label="Close" className="text-red-400 hover:text-red-700">✕</button>
          </div>
        )}
        {saved && (
          <div role="status" className="pointer-events-auto rounded-lg border border-green-200 bg-white p-3 text-sm text-green-700 shadow-lg">
            {saved}
          </div>
        )}
      </div>

      <div className="flex min-h-0 flex-1 gap-2 p-2">
        {/* ── Sidebar: one list at a time, each gets the full height ──────── */}
        {sideOpen && (
          <aside className="hidden min-h-0 w-[250px] shrink-0 flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm lg:flex">
            <div className="flex shrink-0 border-b border-slate-200 text-xs font-semibold">
              {(
                [
                  ["offers", t(lang, "home_list"), offerList.length],
                  ["customers", t(lang, "nav_customers"), customers.length],
                ] as const
              ).map(([id, label, count]) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => setSideTab(id)}
                  className={`flex-1 border-b-2 px-2 py-2 transition-colors ${
                    sideTab === id
                      ? "border-weber-blue text-weber-blue"
                      : "border-transparent text-slate-500 hover:bg-slate-50"
                  }`}
                >
                  {label} <span className="font-normal text-slate-400">{count}</span>
                </button>
              ))}
            </div>

            {sideTab === "offers" ? (
              <>
                <div className="flex shrink-0 flex-col gap-1 p-2">
                  <select
                    value={offerStatusFilter}
                    onChange={(e) => setOfferStatusFilter(e.target.value)}
                    className={ctl}
                  >
                    <option value="">{t(lang, "home_filter_all")}</option>
                    {offerStatuses.map((s) => (
                      <option key={s.status} value={s.status}>
                        {s.status} ({s.count})
                      </option>
                    ))}
                  </select>
                  <input
                    value={offerSearch}
                    onChange={(e) => setOfferSearch(e.target.value)}
                    placeholder={t(lang, "cust_search_ph")}
                    className={ctl}
                  />
                </div>
                <div className="min-h-0 flex-1 overflow-y-auto px-2 pb-2">
                  {offerListLoading ? (
                    <p className="px-2 py-5 text-center text-slate-400">{t(lang, "dash_loading")}</p>
                  ) : filteredOffers.length === 0 ? (
                    <p className="px-2 py-5 text-center text-slate-400">{t(lang, "home_no_results")}</p>
                  ) : (
                    filteredOffers.map((o) => {
                      const selected = o.id === editingOfferId;
                      return (
                        <button
                          key={o.id}
                          type="button"
                          onClick={() => onEdit?.(o.id)}
                          title={`${day(o.offer_date) || day(o.created_at)}`}
                          className={`mb-0.5 w-full rounded-md border-l-[3px] px-2 py-1.5 text-left transition-colors ${
                            selected
                              ? "border-weber-blue bg-blue-50 text-slate-900"
                              : "border-transparent text-slate-700 hover:bg-slate-50"
                          }`}
                        >
                          <span className="flex items-center justify-between gap-1">
                            <span className="truncate font-mono text-xs font-semibold">{o.id_guardian_offer}</span>
                            <span className={`shrink-0 rounded px-1 py-0.5 text-[10px] font-semibold ${statusTone(o.status)}`}>
                              {o.status || "Pending response"}
                            </span>
                          </span>
                          <span className="flex items-center justify-between gap-1 text-[11px] text-slate-500">
                            <span className="truncate">{customerNames[o.customer_id] ?? o.customer_id}</span>
                            <span className="shrink-0 font-mono text-slate-600">{money(o.total_end)}</span>
                          </span>
                        </button>
                      );
                    })
                  )}
                </div>
              </>
            ) : (
              <>
                <div className="shrink-0 p-2">
                  <input
                    value={clientSearch}
                    onChange={(e) => setClientSearch(e.target.value)}
                    placeholder={t(lang, "cust_search_ph")}
                    className={ctl}
                  />
                </div>
                <div className="min-h-0 flex-1 overflow-y-auto px-2 pb-2">
                  {filteredCustomers.map((c) => {
                    const selected = c.customer_id === customerId;
                    return (
                      <button
                        key={c.customer_id}
                        type="button"
                        onClick={() => selectCustomer(c.customer_id)}
                        className={`mb-0.5 w-full rounded-md border-l-[3px] px-2 py-1.5 text-left transition-colors ${
                          selected
                            ? "border-weber-blue bg-blue-50 text-slate-900"
                            : "border-transparent text-slate-700 hover:bg-slate-50"
                        }`}
                      >
                        <span className="block truncate text-xs font-semibold">{c.account_name}</span>
                        <span className="block truncate text-[11px] text-slate-500">
                          {[c.city, c.province, c.country].filter(Boolean).join(", ") || c.customer_id}
                        </span>
                      </button>
                    );
                  })}
                  {filteredCustomers.length === 0 && (
                    <p className="px-2 py-5 text-center text-slate-400">{t(lang, "home_no_results")}</p>
                  )}
                </div>
              </>
            )}
          </aside>
        )}

        <main className="flex min-h-0 min-w-0 flex-1 flex-col gap-2 overflow-hidden">
          {/* ── Header card: customer + offer fields in two compact rows ─── */}
          <div className="shrink-0 rounded-lg border border-slate-200 bg-white p-2 shadow-sm">
            <div className="grid grid-cols-[minmax(220px,1fr)_minmax(0,2.4fr)] gap-3">
              <div className="flex min-w-0 flex-col gap-1">
                <select
                  value={customerId}
                  onChange={(e) => selectCustomer(e.target.value)}
                  className={`${ctl} bg-blue-50 lg:hidden`}
                >
                  <option value="">{t(lang, "ob_select_client")}</option>
                  {customers.map((c) => (
                    <option key={c.customer_id} value={c.customer_id}>
                      {c.customer_id} {c.account_name}
                    </option>
                  ))}
                </select>
                {customer ? (
                  <div className="flex-1 rounded border border-slate-200 bg-slate-50 px-2 py-1.5">
                    <div className="flex items-center gap-2">
                      <span className="shrink-0 rounded border border-slate-200 bg-white px-1.5 py-0.5 font-mono text-[11px]">
                        {customer.customer_id}
                      </span>
                      <span className="truncate text-sm font-bold">{customer.account_name}</span>
                      {offers.length > 0 && (
                        <span className="ml-auto shrink-0 rounded-full bg-blue-100 px-1.5 py-0.5 text-[10px] font-semibold text-blue-900">
                          {offers.length} {t(lang, "ob_client_offers")}
                        </span>
                      )}
                    </div>
                    <div className="mt-1 line-clamp-2 text-slate-600" title={customerAddress}>
                      {customerAddress}
                    </div>
                  </div>
                ) : (
                  <div className="flex min-h-[56px] flex-1 items-center justify-center rounded border border-dashed border-slate-300 px-2 text-center text-slate-400">
                    {t(lang, "ob_select_client")}
                  </div>
                )}
              </div>

              <div className="grid grid-cols-4 content-start gap-x-2 gap-y-1.5">
                {field(
                  t(lang, "ob_offer_no_save"),
                  <input
                    value={offerNumber}
                    onChange={(e) => setOfferNumber(e.target.value)}
                    placeholder="W-02-2026-0001"
                    readOnly={!!editingOfferId}
                    className={`${ctl} font-mono ${editingOfferId ? "bg-slate-100 text-slate-500" : ""}`}
                  />,
                )}
                {field(
                  t(lang, "ob_offer_date"),
                  <input type="date" value={offerDate} onChange={(e) => setOfferDate(e.target.value)} className={`${ctl} font-mono`} />,
                )}
                {field(
                  t(lang, "ob_guardian_type"),
                  <select value={guardianType} onChange={(e) => setGuardianType(e.target.value)} className={ctl}>
                    {GUARDIAN_TYPES.map((g) => (
                      <option key={g}>{g}</option>
                    ))}
                  </select>,
                )}
                {field(
                  t(lang, "ob_frequency"),
                  <select value={frequency} onChange={(e) => setFrequency(e.target.value)} className={ctl}>
                    {FREQUENCIES.map((f) => (
                      <option key={f}>{f}</option>
                    ))}
                  </select>,
                )}
                {field(
                  t(lang, "ob_status"),
                  <select value={status} onChange={(e) => setStatus(e.target.value)} className={ctl}>
                    {STATUSES.map((s) => (
                      <option key={s}>{s}</option>
                    ))}
                  </select>,
                )}
                {field(
                  t(lang, "ob_responsible"),
                  <select value={responsible} onChange={(e) => setResponsible(e.target.value)} className={ctl}>
                    {RESPONSIBLES.map((r) => (
                      <option key={r} value={r}>
                        {r || "-"}
                      </option>
                    ))}
                  </select>,
                )}
                {/* Contract scope opens as a floating panel: zero layout height. */}
                {field(
                  t(lang, "ob_contract_scope"),
                  <details className="relative">
                    <summary
                      className={`${ctl} flex cursor-pointer list-none items-center justify-between font-medium [&::-webkit-details-marker]:hidden`}
                    >
                      <span>
                        {scopeCount}/{GUARDIAN_SCOPE.length}
                        {guardianSelections.length - scopeCount > 0 && (
                          <span className="ml-1 text-slate-400">(+{guardianSelections.length - scopeCount})</span>
                        )}
                      </span>
                      <span aria-hidden="true" className="text-slate-400">▾</span>
                    </summary>
                    <div className="absolute right-0 top-full z-30 mt-1 w-[640px] max-w-[80vw] rounded-lg border border-slate-200 bg-white p-2 shadow-xl">
                      <p className="mb-2 text-[11px] leading-snug text-slate-500">{t(lang, "ob_scope_help")}</p>
                      <div className="grid grid-cols-3 gap-2">
                        {GUARDIAN_SCOPE.map((module) => {
                          const moduleSelected = guardianSelections.includes(module.id);
                          return (
                            <fieldset
                              key={module.id}
                              className={`rounded border p-1.5 ${moduleSelected ? "border-blue-200 bg-blue-50/40" : "border-slate-200 bg-white"}`}
                            >
                              <label className="flex cursor-pointer items-center gap-1.5 text-[11px] font-semibold text-slate-800">
                                <input
                                  type="checkbox"
                                  checked={moduleSelected}
                                  onChange={() => toggleGuardianModule(module.id, module.options.map(([id]) => id))}
                                  className="accent-blue-700"
                                />
                                {module.label}
                              </label>
                              {moduleSelected && (
                                <div className="ml-5 mt-1 space-y-0.5">
                                  {module.options.map(([optionId, optionLabel]) => (
                                    <label key={optionId} className="flex cursor-pointer items-center gap-1.5 text-[11px] text-slate-600">
                                      <input
                                        type="checkbox"
                                        checked={guardianSelections.includes(optionId)}
                                        onChange={() => toggleGuardianOption(module.id, optionId)}
                                        className="accent-blue-700"
                                      />
                                      {optionLabel}
                                    </label>
                                  ))}
                                </div>
                              )}
                            </fieldset>
                          );
                        })}
                      </div>
                    </div>
                  </details>,
                  "col-span-2",
                )}
                {editingOfferId && (
                  <p className="col-span-4 text-[11px] leading-snug text-slate-500">{t(lang, "ob_pricing_note")}</p>
                )}
              </div>
            </div>
          </div>

          {/* ── Work area: machines | lines table | costs + totals + notes ── */}
          <div className="grid min-h-0 flex-1 grid-cols-[180px_minmax(0,1fr)_270px] gap-2">
            <section className="flex min-h-0 flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
              <div className="flex shrink-0 items-center justify-between gap-1 border-b border-slate-200 px-2 py-1.5">
                <span className="font-semibold text-slate-700">
                  {t(lang, "ob_machines")} ({selectedEquip.length}/{equipmentCodes.length})
                </span>
                <div className="flex gap-2 text-[11px]">
                  <button type="button" onClick={() => setSelectedEquip(equipmentCodes)} className="text-blue-700 hover:underline">
                    {t(lang, "ob_all")}
                  </button>
                  <button type="button" onClick={() => setSelectedEquip([])} className="text-slate-600 hover:underline">
                    {t(lang, "ob_none")}
                  </button>
                </div>
              </div>
              <div className="min-h-0 flex-1 overflow-y-auto">
                {equipmentLoading ? (
                  <p className="p-3 text-slate-500">{t(lang, "dash_loading")}</p>
                ) : equipmentCodes.length === 0 ? (
                  <p className="p-3 text-slate-400">{t(lang, "ob_empty_modules")}</p>
                ) : (
                  equipmentCodes.map((code) => {
                    const checked = selectedEquip.includes(code);
                    return (
                      <label
                        key={code}
                        className={`flex cursor-pointer items-center gap-2 border-b border-slate-100 px-2 py-1 last:border-0 hover:bg-blue-50 ${
                          checked ? "bg-blue-50/60" : ""
                        }`}
                      >
                        <input type="checkbox" checked={checked} onChange={() => toggleEquip(code)} className="shrink-0 accent-blue-700" />
                        <span className="min-w-0 flex-1 break-words font-medium">{code}</span>
                        <span className="shrink-0 rounded-full bg-slate-100 px-1.5 text-[10px] text-slate-500">
                          {componentCounts.get(code) ?? 0}
                        </span>
                      </label>
                    );
                  })
                )}
              </div>
            </section>

            <section className="flex min-h-0 flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
              <div className="flex shrink-0 items-center justify-between gap-2 border-b border-slate-200 px-3 py-1.5">
                <span className="font-semibold text-slate-700">
                  {t(lang, "ob_col_module")} <span className="font-normal text-slate-400">{moduleRows.length}</span>
                  {warningCount > 0 && (
                    <span
                      title={t(lang, "workload_title")}
                      className="ml-2 rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold text-amber-800"
                    >
                      ⚠ {warningCount}
                    </span>
                  )}
                </span>
                <span className="font-mono font-semibold text-slate-700">{eur(linesTotal)}</span>
              </div>
              <DataTable
                data={moduleRows}
                columns={moduleColumns}
                loading={equipmentLoading}
                loadingText={t(lang, "dash_loading")}
                emptyText={t(lang, "ob_empty_modules")}
                getRowId={(row) => row.id}
                className="min-h-0 flex-1 border-0"
                tableClassName=""
              />
              <div className="shrink-0 border-t border-blue-200 bg-blue-50 px-3 py-2 text-base">
                <div className="flex justify-between py-0.5">
                  <span className="text-slate-600">{t(lang, "ob_total")}</span>
                  <span className="font-mono font-semibold">{calc ? eur(calc.total) : "—"}</span>
                </div>
                <div className="flex justify-between py-0.5">
                  <span className="text-slate-600">{t(lang, "ob_spare")}</span>
                  <span className="font-mono">{calc ? eur(calc.bk_price) : "—"}</span>
                </div>
                <div className="flex justify-between py-0.5">
                  <span className="text-slate-600">{t(lang, "ob_discount")}</span>
                  <span className="font-mono text-red-600">{calc ? eur(calc.discount) : "—"}</span>
                </div>
                <div className="mt-1 flex items-baseline justify-between border-t border-blue-200 pt-1">
                  <span className="font-bold">{t(lang, "ob_total_amount")}</span>
                  <span className="font-mono text-lg font-bold text-blue-700">{calc ? eur(calc.total_end) : "—"}</span>
                </div>
              </div>
            </section>

            <div className="flex min-h-0 flex-col gap-2 overflow-y-auto">
              <section className="shrink-0 rounded-lg border border-slate-200 bg-white p-2.5 shadow-sm">
                <div className="mb-1 font-semibold text-slate-700">{t(lang, "ob_estimated_costs")}</div>
                <div className="space-y-0.5">
                  <FieldRow label={t(lang, "ob_f_trip")}>€{calc?.trip_cost ?? "—"}</FieldRow>
                  <FieldRow label={t(lang, "ob_f_diets")}>€{calc?.diets ?? "—"}</FieldRow>
                  <FieldRow label={t(lang, "ob_f_hotels")}>€{calc?.hotel_nights_cost ?? "—"}</FieldRow>
                  <FieldRow label={t(lang, "ob_f_trip_hours")}>{calc?.trip_hours ?? "—"}</FieldRow>
                  <FieldRow label={t(lang, "ob_f_work")}>
                    {calc ? (Number(calc.work_hours) + Number(calc.bk_hours)).toFixed(1) : "—"}
                  </FieldRow>
                  <FieldRow label={t(lang, "ob_f_report")}>{calc?.report_hours ?? "—"}</FieldRow>
                  <FieldRow label={t(lang, "ob_f_bk")}>{calc?.bk_hours ?? "—"}</FieldRow>
                  <FieldRow label={t(lang, "ob_f_total_hours")}>{calc?.total_hours ?? "—"}</FieldRow>
                  <FieldRow label={t(lang, "ob_f_guard_hours")}>{calc?.total_hours ?? "—"}</FieldRow>
                  <FieldRow label={t(lang, "ob_f_hours_import")}>€{calc?.hours_import ?? "—"}</FieldRow>
                  <FieldRow label={t(lang, "ob_f_expenses")}>€{calc?.expenses ?? "—"}</FieldRow>
                </div>
              </section>

              <section className="flex min-h-[72px] flex-1 flex-col rounded-lg border border-slate-200 bg-white p-2 shadow-sm">
                <div className="mb-1 font-semibold text-slate-700">{t(lang, "ob_comments")}</div>
                <textarea
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
                  placeholder={t(lang, "ob_comments_ph")}
                  className="w-full flex-1 resize-none rounded border border-slate-300 p-1.5 text-sm focus:border-weber-blue focus:outline-none focus:ring-1 focus:ring-weber-blue"
                />
              </section>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}