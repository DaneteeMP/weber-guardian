// Adapt server-priced maintenance draft rows to the existing offer editor.
// This file deliberately contains no workload resolution or money arithmetic:
// the backend resolves products and computes Decimal amounts with the
// customer's subsidiary technician rate. Offers display hours and amounts
// only; workloads and prices are edited in the Workload Catalog.

import type { MaintenanceDraftRow } from "./api";

export type CatalogWarning = "unpriced" | "unconfirmed";

export type CatalogQuoteLine = {
  equipment: string;
  description: string;
  import_amount: string;
  workload: string;
  catalogWarning?: CatalogWarning;
};

export function lineKey(equipment: string, description: string): string {
  return `${equipment}||${description}`;
}

/** Keep the exact amount returned by the server; never multiply in React. */
export function quoteLinesFromDraft(rows: MaintenanceDraftRow[]): CatalogQuoteLine[] {
  return rows.map((row) => ({
    equipment: row.machine,
    description: row.description ?? "",
    import_amount: row.amount,
    workload: row.workload ?? "0",
    ...(row.needs_review
      ? { catalogWarning: row.match_state === "unconfirmed" ? "unconfirmed" : "unpriced" }
      : {}),
  }));
}
