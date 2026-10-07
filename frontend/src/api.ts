// Typed API wrappers. The only place that knows URLs and response shapes.
// No pricing math here: POST /calculate returns the authoritative breakdown.

// Built by Vite: set VITE_API_BASE to the deployed API URL (no trailing
// slash). Unset locally, where the API runs on localhost:8000.
const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api/v1";

// Dev-only identity (X-Dev-User). In prod behind SharePoint/Entra this
// header disappears and identity travels with the platform token instead.
// The beta has no real login yet, so the shell defaults everyone to the
// admin identity; this goes away with Entra.
let devUser: string | null = localStorage.getItem("devUser");

export function setDevUser(id: string | null) {
  devUser = id;
  if (id) localStorage.setItem("devUser", id);
  else localStorage.removeItem("devUser");
}

export function getDevUser(): string | null {
  return devUser;
}

// The beta has no login UI: every visitor runs as the shared admin
// identity. A stale identity from an older build would pin the app to
// one filial with no visible way out, so boot always resets it. This
// goes away with Entra.
export function ensureDevUser(): string {
  setDevUser("dev-admin");
  return "dev-admin";
}

// View scope ("Filial:" selector). Admins choose which filial's data they
// see; the backend pins everyone else to their own. Kept in localStorage
// so a reload keeps the selected filial. Null = all filials (admin view).
let scopeSubsidiary: string | null = localStorage.getItem("scopeSubsidiary");

export function setScopeSubsidiary(id: string | null) {
  scopeSubsidiary = id;
  if (id) localStorage.setItem("scopeSubsidiary", id);
  else localStorage.removeItem("scopeSubsidiary");
}

export function getScopeSubsidiary(): string | null {
  return scopeSubsidiary;
}

// Shared demo gate (HTTP Basic) in front of the whole API. Kept in
// sessionStorage, not localStorage: it survives a reload but not closing the
// tab, and it is never baked into the bundle. Empty in local dev, where the
// backend gate is disabled and the header is simply ignored.
let gateUser: string | null = sessionStorage.getItem("gateUser");
let gatePassword: string | null = sessionStorage.getItem("gatePassword");

export function hasGateCredentials(): boolean {
  return Boolean(gateUser && gatePassword);
}

export function setGateCredentials(user: string, password: string) {
  gateUser = user;
  gatePassword = password;
  sessionStorage.setItem("gateUser", user);
  sessionStorage.setItem("gatePassword", password);
}

export function clearGateCredentials() {
  gateUser = null;
  gatePassword = null;
  sessionStorage.removeItem("gateUser");
  sessionStorage.removeItem("gatePassword");
}

// The password must be ASCII: btoa rejects anything outside Latin-1.
function basicToken(): string {
  return btoa(`${gateUser}:${gatePassword}`);
}

function authHeaders(): Record<string, string> {
  const h: Record<string, string> = {};
  if (devUser) h["X-Dev-User"] = devUser;
  // URL-encoded: filial names are free text and HTTP headers are not.
  if (scopeSubsidiary) h["X-Scope-Subsidiary"] = encodeURIComponent(scopeSubsidiary);
  if (hasGateCredentials() && gateUser && gatePassword) h["Authorization"] = `Basic ${basicToken()}`;
  return h;
}

function headers(): HeadersInit {
  return { "Content-Type": "application/json", ...authHeaders() };
}

// The app shell subscribes to know when the gate turned us away, so it can
// show the password prompt instead of a generic error.
let gateRequiredListener: (() => void) | null = null;

export function onGateRequired(cb: () => void) {
  gateRequiredListener = cb;
}

// Validates the shared password without needing an app identity: /openapi.json
// sits outside /api/v1 and asks for no user, only the gate. Returns true when
// the credentials are accepted (also true in local dev, where there is no gate).
export async function probeGate(): Promise<boolean> {
  const origin = BASE.replace(/\/api\/v1\/?$/, "");
  const res = await fetch(`${origin}/openapi.json`, { headers: authHeaders() });
  return res.ok;
}

export type Me = {
  external_id: string;
  role: string;
  subsidiary_id: string | null;
  subsidiary_short: string | null;
  scope_subsidiary_id: string | null;
  scope_subsidiary_short: string | null;
};

export function me(): Promise<Me> {
  return fetch(`${BASE}/users/me`, { headers: headers() }).then((r) => checked(r, "GET me"));
}

export type Subsidiary = { name: string; short_label: string };

export function listSubsidiaries(): Promise<Subsidiary[]> {
  return fetch(`${BASE}/subsidiaries`, { headers: headers() }).then((r) => checked(r, "GET subsidiaries"));
}

export type Customer = {
  id: string;
  customer_id: string;
  account_name: string;
  city: string | null;
  province: string | null;
  country: string | null;
  subsidiary_id: string | null;
};

export function createCustomer(payload: {
  customer_id: string;
  account_name: string;
  country?: string | null;
}): Promise<Customer> {
  return fetch(`${BASE}/customers`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(payload),
  }).then((r) => checked(r, "POST customer"));
}

export type Pricing = {
  work_hours: number;
  bk_hours: number;
  report_hours: number;
  trip_hours_base: number;
  km: number;
  km_rate: number;
  tech_rate: number;
  diet_full_rate: number;
  diet_half_rate: number;
  hotel_rate: number;
  discount_rate: number;
  bk_price: number;
  currency: string;
};

export type Breakdown = {
  work_hours: string;
  bk_hours: string;
  report_hours: string;
  total_hours: string;
  num_days: number;
  trip_cost: string;
  trip_hours: string;
  diets: string;
  hotel_nights_cost: string;
  expenses: string;
  hours_import: string;
  discount: string;
  bk_price: string;
  total: string;
  total_end: string;
  currency: string;
};

export type OfferItemIn = {
  equipment?: string;
  description?: string;
  import_amount: number;
  workload: number;
};

async function checked(res: Response, what: string) {
  if (!res.ok) {
    // A Basic challenge is the demo gate, not the identity seam; tell the
    // shell so it can ask for the shared password.
    if (res.status === 401 && res.headers.get("www-authenticate")?.toLowerCase().startsWith("basic")) {
      gateRequiredListener?.();
    }
    const data = await res.json().catch(() => null);
    const detail = typeof data?.detail === "string" ? data.detail : JSON.stringify(data?.detail ?? res.statusText);
    throw new Error(`${what} failed (${res.status}): ${detail}`);
  }
  return res.json();
}

export function listCustomers(opts?: { search?: string; limit?: number; offset?: number }): Promise<{
  rows: Customer[];
  total: number;
}> {
  const params = new URLSearchParams();
  if (opts?.search) params.set("search", opts.search);
  params.set("limit", String(opts?.limit ?? 50));
  params.set("offset", String(opts?.offset ?? 0));
  return fetch(`${BASE}/customers?${params}`, { headers: headers() }).then(async (r) => {
    const rows = (await checked(r, "GET customers")) as Customer[];
    return { rows, total: Number(r.headers.get("X-Total-Count") ?? rows.length) };
  });
}

export async function listAllCustomers(): Promise<Customer[]> {
  // One page at a time until the total: the picker must hold every
  // customer in scope, not just the first page.
  const all: Customer[] = [];
  let offset = 0;
  for (;;) {
    const page = await listCustomers({ limit: 200, offset });
    all.push(...page.rows);
    offset += page.rows.length;
    if (offset >= page.total || page.rows.length === 0) break;
  }
  return all;
}

export type CustomerSite = {
  id: string;
  physical_street: string | null;
  physical_city: string | null;
  physical_postal_code: string | null;
  physical_province: string | null;
  physical_country: string | null;
};

export type CustomerComponent = {
  component_type: string | null;
  material_no: string | null;
  purchase_date: string | null;
};

export type CustomerMachine = {
  equipment_name: string;
  machine_type: string | null;
  site_id: string | null;
  components: CustomerComponent[];
};

export type CustomerDetail = {
  customer: Customer;
  sites: CustomerSite[];
  machines: CustomerMachine[];
};

/** Addresses and the whole machine list for one customer.
 *
 * Deliberately not listEquipment(): that endpoint pages at 50 rows, which
 * silently hid 104 of the 154 machines of a real Italian customer.
 */
export function getCustomerDetail(customerId: string): Promise<CustomerDetail> {
  return fetch(`${BASE}/customers/${encodeURIComponent(customerId)}/detail`, { headers: headers() }).then((r) =>
    checked(r, "GET customer detail"),
  );
}

export type ComponentWorkload = {
  id: string;
  name: string;
  component_type: string;
  workload: string | null;
  needs_review: boolean;
  legacy_type_code: string | null;
  created_at: string;
};

export type WorkloadImportReport = {
  encoding: string;
  rows_read: number;
  rows_blank: number;
  rows_without_material_no: number;
  source_entries: number;
  source_conflicts: number;
  products_discovered: number;
  workloads_created: number;
  workloads_preserved: number;
  workloads_needing_review_created: number;
  rows_without_component_type: number;
};

export function listComponentWorkloads(opts?: {
  search?: string;
  component_type?: string;
  needs_review?: boolean;
  limit?: number;
  offset?: number;
}): Promise<{ rows: ComponentWorkload[]; total: number }> {
  const params = new URLSearchParams();
  if (opts?.search) params.set("search", opts.search);
  if (opts?.component_type) params.set("component_type", opts.component_type);
  if (opts?.needs_review !== undefined) params.set("needs_review", String(opts.needs_review));
  params.set("limit", String(opts?.limit ?? 200));
  params.set("offset", String(opts?.offset ?? 0));
  return fetch(`${BASE}/component-workloads?${params}`, { headers: headers() }).then(async (r) => {
    const rows = (await checked(r, "GET component workloads")) as ComponentWorkload[];
    return { rows, total: Number(r.headers.get("X-Total-Count") ?? rows.length) };
  });
}

/** Import SAP CSV, refresh internal product mappings and add newly discovered
 * workload products without changing existing manual workload values. */
export function importWorkloadCsv(file: File): Promise<WorkloadImportReport> {
  const form = new FormData();
  form.append("file", file);

  return fetch(`${BASE}/component-workloads/import`, {
    method: "POST",
    headers: authHeaders(),
    body: form,
  }).then((r) => checked(r, "POST workload catalog import"));
}

export function createComponentWorkload(payload: {
  name: string;
  component_type: string;
  workload: string | null;
  needs_review?: boolean;
}): Promise<ComponentWorkload> {
  return fetch(`${BASE}/component-workloads`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(payload),
  }).then((r) => checked(r, "POST component workload"));
}

export function updateComponentWorkload(
  id: string,
  changes: { name?: string; workload?: string | null; needs_review?: boolean },
): Promise<ComponentWorkload> {
  return fetch(`${BASE}/component-workloads/${encodeURIComponent(id)}`, {
    method: "PATCH",
    headers: headers(),
    body: JSON.stringify(changes),
  }).then((r) => checked(r, "PATCH component workload"));
}

export async function deleteComponentWorkload(id: string): Promise<void> {
  const response = await fetch(`${BASE}/component-workloads/${encodeURIComponent(id)}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!response.ok) await checked(response, "DELETE component workload");
}

// Legacy module workloads, keyed by type_code (the restored TblWorkLoad).
// Ordinary maintenance modules price from here; slicers from component_workloads.
export type ModuleWorkload = {
  type_code: string;
  label: string;
  workload: string | null;
  needs_review: boolean;
};

export function listModuleWorkloads(opts?: {
  search?: string;
  needs_review?: boolean;
  limit?: number;
  offset?: number;
}): Promise<{ rows: ModuleWorkload[]; total: number }> {
  const params = new URLSearchParams();
  if (opts?.search) params.set("search", opts.search);
  if (opts?.needs_review !== undefined) params.set("needs_review", String(opts.needs_review));
  params.set("limit", String(opts?.limit ?? 200));
  params.set("offset", String(opts?.offset ?? 0));
  return fetch(`${BASE}/module-workloads?${params}`, { headers: headers() }).then(async (r) => {
    const rows = (await checked(r, "GET module workloads")) as ModuleWorkload[];
    return { rows, total: Number(r.headers.get("X-Total-Count") ?? rows.length) };
  });
}

export function updateModuleWorkload(
  typeCode: string,
  changes: { workload: string | null; needs_review?: boolean; label?: string },
): Promise<ModuleWorkload> {
  return fetch(`${BASE}/module-workloads/${encodeURIComponent(typeCode)}`, {
    method: "PUT",
    headers: headers(),
    body: JSON.stringify(changes),
  }).then((r) => checked(r, "PUT module workload"));
}

// Machine-line workloads (equipment_catalog), keyed by machine_type. The line
// is the machine itself (family price), e.g. "40x" for the 402/404/405 slicers.
export type LineWorkload = {
  id: string;
  kind: "line";
  label: string;
  workload: string | null;
  matches: { id: string; match_field: "machine_type"; match_value: string; is_confirmed: boolean }[];
  created_at: string;
};

export function updateLineWorkload(
  machineType: string,
  changes: { workload: string | null; label?: string },
): Promise<LineWorkload> {
  return fetch(`${BASE}/line-workloads/${encodeURIComponent(machineType)}`, {
    method: "PUT",
    headers: headers(),
    body: JSON.stringify(changes),
  }).then((r) => checked(r, "PUT line workload"));
}

export function calculate(pricing: Pricing): Promise<Breakdown> {
  return fetch(`${BASE}/offers/calculate`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(pricing),
  }).then((r) => checked(r, "POST calculate"));
}

export function createOffer(payload: {
  customer_id: string;
  id_guardian_offer?: string;
  status: string;
  responsible_person?: string;
  language?: string;
  inspection_frequency?: string;
  pricing: Pricing;
  items: OfferItemIn[];
  general_comments?: string;
  offer_date?: string;
  guardian_selections?: string[];
}): Promise<{ id: string; id_guardian_offer: string }> {
  return fetch(`${BASE}/offers`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(payload),
  }).then((r) => checked(r, "POST offer"));
}

export async function downloadOfferPdf(id: string): Promise<void> {
  const res = await fetch(`${BASE}/offers/${encodeURIComponent(id)}/pdf`, { headers: authHeaders() });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`GET pdf failed (${res.status}): ${text}`);
  }
  const cd = res.headers.get("Content-Disposition") ?? "";
  const filename = cd.match(/filename="([^"]+)"/)?.[1] ?? `Offer_${id}.pdf`;
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export type OfferListItem = {
  id: string;
  id_guardian_offer: string;
  customer_id: string;
  created_at?: string | null;
  offer_date?: string | null;
  currency?: string | null;
  language?: string | null;
  status?: string | null;
  inspection_frequency?: string | null;
  responsible_person?: string | null;
  work_hours?: string | number | null;
  total?: string | number | null;
  total_end?: string | number | null;
};

export function listOffers(customer_id: string): Promise<OfferListItem[]> {
  return fetch(`${BASE}/offers?customer_id=${encodeURIComponent(customer_id)}`, {
    headers: headers(),
  }).then((r) => checked(r, "GET offers"));
}

export function listAllOffers(limit = 200, status?: string): Promise<OfferListItem[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (status) params.set("status", status);
  return fetch(`${BASE}/offers?${params}`, { headers: headers() }).then((r) =>
    checked(r, "GET offers")
  );
}

export function getOffer(id: string): Promise<OfferOut> {
  return fetch(`${BASE}/offers/${encodeURIComponent(id)}`, { headers: headers() }).then((r) =>
    checked(r, "GET offer")
  );
}

export type OfferOut = OfferListItem & {
  responsible_person: string | null;
  language: string | null;
  inspection_frequency: string | null;
  general_comments: string | null;
  guardian_selections: string[];
  work_hours: string | number;
  report_hours: string | number;
  trip_hours: string | number;
  items: { equipment: string | null; description: string | null; import_amount: string | number; workload: string | number }[];
};

export function updateOffer(
  id: string,
  payload: {
    status: string;
    responsible_person?: string;
    language?: string;
    inspection_frequency?: string;
    general_comments?: string;
    offer_date?: string;
    guardian_selections?: string[];
    pricing: Pricing;
    items: OfferItemIn[];
  }
): Promise<OfferListItem> {
  return fetch(`${BASE}/offers/${encodeURIComponent(id)}`, {
    method: "PUT",
    headers: headers(),
    body: JSON.stringify(payload),
  }).then((r) => checked(r, "PUT offer"));
}

export type OffersSummary = {
  total: number;
  by_status: { status: string; count: number }[];
  monthly: { month: string; count: number }[];
  ranking: { customer_id: string; count: number; total_end: string }[];
};

export function getOffersSummary(): Promise<OffersSummary> {
  return fetch(`${BASE}/offers/summary`, { headers: headers() }).then((r) =>
    checked(r, "GET offers summary")
  );
}

export function deleteOffer(id: string): Promise<void> {
  return fetch(`${BASE}/offers/${encodeURIComponent(id)}`, {
    method: "DELETE",
    headers: headers(),
  }).then(async (r) => {
    if (!r.ok) throw new Error(`DELETE offer failed (${r.status})`);
  });
}

export function setOfferStatus(id: string, status: string): Promise<OfferListItem> {
  return fetch(`${BASE}/offers/${encodeURIComponent(id)}`, {
    method: "PATCH",
    headers: headers(),
    body: JSON.stringify({ status }),
  }).then((r) => checked(r, "PATCH offer"));
}

export function closeOffer(id: string): Promise<OfferListItem> {
  return setOfferStatus(id, "Finished");
}

export type Equipment = {
  id: string;
  customer_id: string;
  equipment_name: string | null;
  machine_type: string | null;
  component_type: string | null;
  material_no: string | null;
  purchase_date: string | null;
  site: {
    id: string;
    physical_street: string | null;
    physical_city: string | null;
    physical_postal_code: string | null;
    physical_province: string | null;
    physical_country: string | null;
  } | null;
};

export function listEquipment(customer_id: string): Promise<Equipment[]> {
  return fetch(`${BASE}/equipment?customer_id=${encodeURIComponent(customer_id)}`, {
    headers: headers(),
  }).then((r) => checked(r, "GET equipment"));
}

// Migration 0019: the catalog prices nothing. An entry carries hours only;
// the amount is workload × the branch technician rate, computed server-side.
export type EquipmentCatalogKind = "line";
export type EquipmentCatalogMatch = {
  id: string;
  match_field: "machine_type";
  match_value: string;
  is_confirmed: boolean;
};
export type EquipmentCatalogEntry = {
  id: string;
  kind: EquipmentCatalogKind;
  label: string;
  workload: string | number | null;
  matches: EquipmentCatalogMatch[];
  created_at: string;
};
export type EquipmentCatalogEntryInput = {
  kind: EquipmentCatalogKind;
  label: string;
  workload: string | null;
  matches: {
    match_field: "machine_type";
    match_value: string;
    is_confirmed: boolean;
  }[];
};

export function listEquipmentCatalog(): Promise<EquipmentCatalogEntry[]> {
  return fetch(`${BASE}/equipment-catalog`, { headers: headers() }).then((r) =>
    checked(r, "GET equipment catalog")
  );
}

export type MaintenanceDraftRow = {
  machine: string;
  kind: "line" | "module";
  description: string | null;
  material_no: string | null;
  type_code: string | null;
  workload_kind: "line" | "module" | "product" | null;
  workload_id: string | null;
  line_code: string | null;
  component_type: string | null;
  workload: string | null;
  amount: string;
  match_state: "confirmed" | "unconfirmed" | "unknown";
  needs_review: boolean;
};

export type MaintenanceDraft = {
  customer_id: string;
  subsidiary_id: string | null;
  currency: string;
  tech_rate: string;
  rows: MaintenanceDraftRow[];
  total_workload: string;
  total_amount: string;
};

/** Priced draft rows for the selected machines.
 *
 * The backend multiplies each row's workload by the customer's branch rate
 * with Decimal; React never does money math (AGENTS rule 6). Rows flagged
 * needs_review carry hours nobody verified and must be typed by hand.
 */
export function maintenanceDraft(customerId: string, machineNames: string[]): Promise<MaintenanceDraft> {
  return fetch(`${BASE}/offers/maintenance-draft`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ customer_id: customerId, machine_names: machineNames }),
  }).then((r) => checked(r, "POST maintenance draft"));
}

export function createEquipmentCatalogEntry(payload: EquipmentCatalogEntryInput): Promise<EquipmentCatalogEntry> {
  return fetch(`${BASE}/equipment-catalog`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(payload),
  }).then((r) => checked(r, "POST equipment catalog entry"));
}

export function updateEquipmentCatalogEntry(
  id: string,
  payload: EquipmentCatalogEntryInput
): Promise<EquipmentCatalogEntry> {
  return fetch(`${BASE}/equipment-catalog/${encodeURIComponent(id)}`, {
    method: "PUT",
    headers: headers(),
    body: JSON.stringify(payload),
  }).then((r) => checked(r, "PUT equipment catalog entry"));
}

export async function deleteEquipmentCatalogEntry(id: string): Promise<void> {
  const response = await fetch(`${BASE}/equipment-catalog/${encodeURIComponent(id)}`, {
    method: "DELETE",
    headers: headers(),
  });
  if (!response.ok) await checked(response, "DELETE equipment catalog entry");
}

export type Prices = {
  subsidiary_id: string;
  currency: string;
  km_rate: string;
  tech_rate: string;
  diet_full_rate: string;
  diet_half_rate: string;
  hotel_rate: string;
};

export function getPrices(subsidiary_id: string): Promise<Prices> {
  return fetch(`${BASE}/prices/${encodeURIComponent(subsidiary_id)}`, {
    headers: headers(),
  }).then((r) => checked(r, "GET prices"));
}

export function updatePrices(
  subsidiary_id: string,
  rates: {
    currency: string;
    km_rate: string;
    tech_rate: string;
    diet_full_rate: string;
    diet_half_rate: string;
    hotel_rate: string;
  }
): Promise<Prices> {
  return fetch(`${BASE}/prices/${encodeURIComponent(subsidiary_id)}`, {
    method: "PUT",
    headers: headers(),
    body: JSON.stringify(rates),
  }).then((r) => checked(r, "PUT prices"));
}

export type Distance = {
  subsidiary_id: string;
  province: string;
  province_code: string | null;
  region: string | null;
  capital: string | null;
  reference_city: string | null;
  service_center: string | null;
  origin_city: string | null;
  km: string | number;
  driving_hours: string | number | null;
  trip_hours: string | number;
  itinerary: string | null;
  route_data_date: string | null;
};

export type DistanceInput = {
  province_code: string | null;
  region: string | null;
  capital: string | null;
  reference_city: string | null;
  service_center: string | null;
  origin_city: string | null;
  km: string;
  driving_hours: string | null;
  trip_hours: string;
  itinerary: string | null;
  route_data_date: string | null;
};

export function listDistances(): Promise<Distance[]> {
  const params = new URLSearchParams({ limit: "200" });
  return fetch(`${BASE}/distances?${params}`, { headers: headers() }).then((r) =>
    checked(r, "GET distances")
  );
}

export function upsertDistance(
  subsidiaryId: string,
  province: string,
  distance: DistanceInput
): Promise<Distance> {
  const params = new URLSearchParams({ subsidiary_id: subsidiaryId });
  return fetch(`${BASE}/distances/${encodeURIComponent(province)}?${params}`, {
    method: "PUT",
    headers: headers(),
    body: JSON.stringify(distance),
  }).then((r) => checked(r, "PUT distance"));
}

export function deleteDistance(subsidiaryId: string, province: string): Promise<void> {
  const params = new URLSearchParams({ subsidiary_id: subsidiaryId });
  return fetch(`${BASE}/distances/${encodeURIComponent(province)}?${params}`, {
    method: "DELETE",
    headers: headers(),
  }).then(async (r) => {
    if (!r.ok) throw new Error(`DELETE distance failed (${r.status})`);
  });
}

export type DistanceImportReport = {
  dry_run: boolean;
  total_rows: number;
  created: number;
  updated: number;
  errors: { line: number; reason: string }[];
};

export async function importDistanceRoutes(
  file: File,
  subsidiaryId: string,
  originCity: string,
  routeDataDate: string,
  dryRun: boolean
): Promise<DistanceImportReport> {
  const params = new URLSearchParams({
    subsidiary_id: subsidiaryId,
    origin_city: originCity,
    route_data_date: routeDataDate,
    dry_run: String(dryRun),
  });
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${BASE}/distances/import?${params}`, {
    method: "POST",
    headers: authHeaders(),
    body: form,
  });
  if (response.status === 422) {
    const payload = await response.json().catch(() => null);
    if (payload?.detail && Array.isArray(payload.detail.errors)) return payload.detail as DistanceImportReport;
    return checked(new Response(JSON.stringify(payload), { status: 422 }), "POST distance import");
  }
  return checked(response, "POST distance import");
}

export type Kit = { model: string; workload_basic_kit: string; spare_parts: string };

export function listKits(): Promise<Kit[]> {
  return fetch(`${BASE}/basic-kit`, { headers: headers() }).then((r) => checked(r, "GET kits"));
}

export function createKit(model: string, workload_basic_kit: number, spare_parts: number): Promise<Kit> {
  return fetch(`${BASE}/basic-kit`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ model, workload_basic_kit, spare_parts }),
  }).then((r) => checked(r, "POST kit"));
}

export function deleteKit(model: string): Promise<void> {
  return fetch(`${BASE}/basic-kit/${encodeURIComponent(model)}`, {
    method: "DELETE",
    headers: headers(),
  }).then(async (r) => {
    if (!r.ok) throw new Error(`DELETE kit failed (${r.status})`);
  });
}

export function updateKit(model: string, workload_basic_kit: number, spare_parts: number): Promise<Kit> {
  return fetch(`${BASE}/basic-kit/${encodeURIComponent(model)}`, {
    method: "PUT",
    headers: headers(),
    body: JSON.stringify({ workload_basic_kit, spare_parts }),
  }).then((r) => checked(r, "PUT kit"));
}

export type MachinePrice = { model: string; annual_price: string; inspections_per_year: number; currency: string };

export function listMachinePrices(): Promise<MachinePrice[]> {
  return fetch(`${BASE}/machine-prices`, { headers: headers() }).then((r) => checked(r, "GET machine prices"));
}

export function upsertMachinePrice(model: string, annual_price: number, inspections_per_year: number): Promise<MachinePrice> {
  return fetch(`${BASE}/machine-prices/${encodeURIComponent(model)}`, {
    method: "PUT",
    headers: headers(),
    body: JSON.stringify({ annual_price, inspections_per_year }),
  }).then((r) => checked(r, "PUT machine price"));
}

export function deleteMachinePrice(model: string): Promise<void> {
  return fetch(`${BASE}/machine-prices/${encodeURIComponent(model)}`, {
    method: "DELETE",
    headers: headers(),
  }).then(async (r) => {
    if (!r.ok) throw new Error(`DELETE machine price failed (${r.status})`);
  });
}

export type ImportReport = {
  dry_run: boolean;
  total_rows: number;
  customers_created: number;
  customers_skipped: number;
  sites_created: number;
  sites_skipped: number;
  equipment_created: number;
  equipment_updated: number;
  equipment_skipped: number;
  errors: { line: number; reason: string }[];
  warnings: string[];
};

export function uploadCsv(file: File, dryRun: boolean, subsidiaryId?: string): Promise<ImportReport> {
  const form = new FormData();
  form.append("file", file);
  let url = `${BASE}/imports/upload?dry_run=${dryRun}`;
  if (subsidiaryId) url += `&subsidiary_id=${encodeURIComponent(subsidiaryId)}`;
  return fetch(url, { method: "POST", headers: authHeaders(), body: form }).then((r) =>
    checked(r, "POST upload")
  );
}
