// Typed API wrappers. The only place that knows URLs and response shapes.
// No pricing math here: POST /calculate returns the authoritative breakdown.

const BASE = "http://localhost:8000/api/v1";

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
  return fetch(`${BASE}/customers`).then((r) => checked(r, "GET customers"));
}

export function calculate(pricing: Pricing): Promise<Breakdown> {
  return fetch(`${BASE}/offers/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(pricing),
  }).then((r) => checked(r, "POST calculate"));
}

export function createOffer(payload: {
  customer_id: string;
  id_guardian_offer?: string;
  status: string;
  pricing: Pricing;
  items: OfferItemIn[];
  general_comments?: string;
}): Promise<unknown> {
  return fetch(`${BASE}/offers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then((r) => checked(r, "POST offer"));
}

export function listOffers(customer_id: string): Promise<unknown[]> {
  return fetch(`${BASE}/offers?customer_id=${encodeURIComponent(customer_id)}`).then((r) =>
    checked(r, "GET offers")
  );
}
