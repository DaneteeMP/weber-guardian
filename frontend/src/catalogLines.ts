// Adapt server-priced maintenance draft rows to the existing offer editor.
// This file deliberately contains no workload resolution or money arithmetic:
// the backend resolves products and computes Decimal amounts with the
// customer's subsidiary technician rate.

import type { MaintenanceDraftRow } from "./api";

export type CatalogWarning = "unpriced" | "unconfirmed";

export type CatalogQuoteLine = {
  equipment: string;
  description: string;
  import_amount: string;
  workload: string;
  catalogWarning?: CatalogWarning;
  // Where to edit the hours from: the legacy module table (type_code) or the
  // product catalog (component_workloads, slicer models).
  workloadKind: "line" | "module" | "product" | null;
  workloadId: string | null;
  lineCode: string | null;
  typeCode: string | null;
  componentType: string | null;
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
    workloadKind: row.workload_kind,
    workloadId: row.workload_id,
    lineCode: row.line_code,
    typeCode: row.type_code,
    componentType: row.component_type,
    ...(row.needs_review
      ? { catalogWarning: row.match_state === "unconfirmed" ? "unconfirmed" : "unpriced" }
      : {}),
  }));
}
