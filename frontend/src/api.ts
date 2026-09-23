// Typed API wrappers. The only place that knows URLs and response shapes.
// No pricing math here: POST /calculate returns the authoritative breakdown.

const BASE = "http://localhost:8000/api/v1";

// Dev-only identity (X-Dev-User). In prod behind SharePoint/Entra this
// header disappears and identity travels with the platform token instead.
let devUser: string | null = localStorage.getItem("devUser");

export function setDevUser(id: string | null) {
  devUser = id;
  if (id) localStorage.setItem("devUser", id);
  else localStorage.removeItem("devUser");
}

export function getDevUser(): string | null {
  return devUser;
}

function headers(): HeadersInit {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (devUser) h["X-Dev-User"] = devUser;
  return h;
}

export type Me = { external_id: string; role: string; subsidiary_id: string | null };

export function me(): Promise<Me> {
  return fetch(`${BASE}/users/me`, { headers: headers() }).then((r) => checked(r, "GET me"));
}

export type Customer = {
  id: string;
  customer_id: string;
  account_name: string;
  country: string | null;
};

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
    const data = await res.json().catch(() => null);
    const detail = typeof data?.detail === "string" ? data.detail : JSON.stringify(data?.detail ?? res.statusText);
    throw new Error(`${what} failed (${res.status}): ${detail}`);
  }
  return res.json();
}

export function listCustomers(): Promise<Customer[]> {
  return fetch(`${BASE}/customers`, { headers: headers() }).then((r) => checked(r, "GET customers"));
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
}): Promise<{ id: string; id_guardian_offer: string }> {
  return fetch(`${BASE}/offers`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(payload),
  }).then((r) => checked(r, "POST offer"));
}

export async function downloadOfferPdf(id: string): Promise<{ blob: Blob; filename: string }> {
  const h: Record<string, string> = {};
  const dev = getDevUser();
  if (dev) h["X-Dev-User"] = dev;
  const res = await fetch(`${BASE}/offers/${encodeURIComponent(id)}/pdf`, { headers: h });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`GET pdf failed (${res.status}): ${text}`);
  }
  const cd = res.headers.get("Content-Disposition") ?? "";
  const filename = cd.match(/filename="([^"]+)"/)?.[1] ?? `Offer_${id}.pdf`;
  return { blob: await res.blob(), filename };
}

export type OfferListItem = {
  id: string;
  id_guardian_offer: string;
  date_guardian?: string | null;
  language?: string | null;
  status?: string | null;
  inspection_frequency?: string | null;
  total?: string | number | null;
  total_end?: string | number | null;
};

export function listOffers(customer_id: string): Promise<OfferListItem[]> {
  return fetch(`${BASE}/offers?customer_id=${encodeURIComponent(customer_id)}`, {
    headers: headers(),
  }).then((r) => checked(r, "GET offers"));
}

export function deleteOffer(id: string): Promise<void> {
  return fetch(`${BASE}/offers/${encodeURIComponent(id)}`, {
    method: "DELETE",
    headers: headers(),
  }).then(async (r) => {
    if (!r.ok) throw new Error(`DELETE offer failed (${r.status})`);
  });
}

export function closeOffer(id: string): Promise<OfferListItem> {
  return fetch(`${BASE}/offers/${encodeURIComponent(id)}`, {
    method: "PATCH",
    headers: headers(),
    body: JSON.stringify({ status: "Finished" }),
  }).then((r) => checked(r, "PATCH offer"));
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
};

export function uploadCsv(file: File, dryRun: boolean, subsidiaryId?: string): Promise<ImportReport> {
  const form = new FormData();
  form.append("file", file);
  const h: Record<string, string> = {};
  const dev = getDevUser();
  if (dev) h["X-Dev-User"] = dev;
  let url = `${BASE}/imports/upload?dry_run=${dryRun}`;
  if (subsidiaryId) url += `&subsidiary_id=${encodeURIComponent(subsidiaryId)}`;
  return fetch(url, { method: "POST", headers: h, body: form }).then((r) => checked(r, "POST upload"));
}
