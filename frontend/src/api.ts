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

export type SubsidiaryStats = { name: string; short_label: string; countries: number; customers: number };

export function getSubsidiaryStats(): Promise<SubsidiaryStats[]> {
  return fetch(`${BASE}/subsidiaries/stats`, { headers: headers() }).then((r) =>
    checked(r, "GET subsidiary stats")
  );
}

export type UnassignedCountry = { country: string; count: number };

export function getUnassignedCountries(): Promise<UnassignedCountry[]> {
  return fetch(`${BASE}/subsidiaries/unassigned-countries`, { headers: headers() }).then((r) =>
    checked(r, "GET unassigned countries")
  );
}

export function assignCountries(assignments: { country: string; subsidiary: string }[]): Promise<{ updated: number }> {
  return fetch(`${BASE}/subsidiaries/assign-countries`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ assignments }),
  }).then((r) => checked(r, "POST assign countries"));
}

export function autoAssignAll(): Promise<{ updated: number; warnings: string[] }> {
  return fetch(`${BASE}/subsidiaries/auto-assign`, {
    method: "POST",
    headers: headers(),
  }).then((r) => checked(r, "POST auto assign"));
}

export type Customer = {
  id: string;
  customer_id: string;
  account_name: string;
  country: string | null;
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
};

export function listEquipment(customer_id: string): Promise<Equipment[]> {
  return fetch(`${BASE}/equipment?customer_id=${encodeURIComponent(customer_id)}`, {
    headers: headers(),
  }).then((r) => checked(r, "GET equipment"));
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
  rates: { currency: string; km_rate: number; tech_rate: number; diet_full_rate: number; diet_half_rate: number; hotel_rate: number }
): Promise<Prices> {
  return fetch(`${BASE}/prices/${encodeURIComponent(subsidiary_id)}`, {
    method: "PUT",
    headers: headers(),
    body: JSON.stringify(rates),
  }).then((r) => checked(r, "PUT prices"));
}

export type Distance = { province: string; km: string; trip_hours: string };

export function listDistances(): Promise<Distance[]> {
  return fetch(`${BASE}/distances`, { headers: headers() }).then((r) => checked(r, "GET distances"));
}

export function upsertDistance(province: string, km: number, trip_hours: number): Promise<Distance> {
  return fetch(`${BASE}/distances/${encodeURIComponent(province)}`, {
    method: "PUT",
    headers: headers(),
    body: JSON.stringify({ km, trip_hours }),
  }).then((r) => checked(r, "PUT distance"));
}

export function deleteDistance(province: string): Promise<void> {
  return fetch(`${BASE}/distances/${encodeURIComponent(province)}`, {
    method: "DELETE",
    headers: headers(),
  }).then(async (r) => {
    if (!r.ok) throw new Error(`DELETE distance failed (${r.status})`);
  });
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

export type Dashboard = {
  total_customers: number;
  total_equipment: number;
  total_offers: number;
  total_offer_lines: number;
  countries: { country: string; count: number }[];
};

export function getDashboard(): Promise<Dashboard> {
  return fetch(`${BASE}/dashboard`, { headers: headers() }).then((r) => checked(r, "GET dashboard"));
}

export type ImportReport = {
  dry_run: boolean;
  total_rows: number;
  customers_created: number;
  customers_skipped: number;
  equipment_created: number;
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
