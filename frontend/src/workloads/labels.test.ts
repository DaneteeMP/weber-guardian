import { describe, expect, it } from "vitest";

import { formatHours, reasonKey, stateKey } from "./labels";

describe("workload state and reason labels", () => {
  it("maps every resolution state to its own wording", () => {
    expect(stateKey("resolved")).toBe("workload_state_resolved");
    expect(stateKey("no_rule")).toBe("workload_state_no_rule");
    expect(stateKey("not_in_dictionary")).toBe("workload_state_not_in_dictionary");
    expect(stateKey("slicer")).toBe("workload_state_slicer");
  });

  it("maps every unresolved reason, including conflicts, to a distinct label", () => {
    expect(reasonKey("no_rule")).toBe("workload_state_no_rule");
    expect(reasonKey("no_hours")).toBe("workload_reason_no_hours");
    expect(reasonKey("dictionary_conflict")).toBe("workload_dictionary_conflict");
    expect(reasonKey("not_in_dictionary")).toBe("workload_state_not_in_dictionary");
  });

  it("shows hours with a unit and never invents a value for missing hours", () => {
    expect(formatHours("1.00")).toBe("1.00 h");
    expect(formatHours(null)).toBe("—");
  });
});
