import { describe, expect, it } from "vitest";

import type { MaintenanceDraftRow } from "./api";
import { quoteLinesFromDraft } from "./catalogLines";

function row(overrides: Partial<MaintenanceDraftRow> = {}): MaintenanceDraftRow {
  return {
    machine: "602-837 MLC",
    kind: "module",
    description: "Checkweigher",
    material_no: "CCW04001",
    type_code: "CCW",
    workload_kind: "module",
    workload_id: null,
    line_code: null,
    component_type: "Checkweigher",
    workload: "1.50",
    amount: "87.00",
    match_state: "confirmed",
    needs_review: false,
    ...overrides,
  };
}

describe("maintenance draft row adapter", () => {
  it("preserves server workload and amount without recalculating money", () => {
    expect(quoteLinesFromDraft([row()])).toEqual([
      {
        equipment: "602-837 MLC",
        description: "Checkweigher",
        workload: "1.50",
        import_amount: "87.00",
        workloadKind: "module",
        workloadId: null,
        lineCode: null,
        typeCode: "CCW",
        componentType: "Checkweigher",
      },
    ]);
  });

  it("marks unknown workload rows for review and keeps the server's zero amount", () => {
    const lines = quoteLinesFromDraft([
      row({ workload: null, amount: "0.00", match_state: "unknown", needs_review: true }),
    ]);

    expect(lines[0].workload).toBe("0");
    expect(lines[0].import_amount).toBe("0.00");
    expect(lines[0].catalogWarning).toBe("unpriced");
  });

  it("marks an unconfirmed product mapping separately", () => {
    const lines = quoteLinesFromDraft([
      row({ match_state: "unconfirmed", needs_review: true }),
    ]);

    expect(lines[0].catalogWarning).toBe("unconfirmed");
    expect(lines[0].import_amount).toBe("87.00");
  });
});
