import { describe, expect, it } from "vitest";

import { displayKitModel } from "./kitModels";

describe("displayKitModel", () => {
  it("renders suffix-first codes as 'Model Suffix'", () => {
    expect(displayKitModel("CCL304")).toBe("304 CCL");
    expect(displayKitModel("CCS304")).toBe("304 CCS");
    expect(displayKitModel("UB304")).toBe("304 UB");
    expect(displayKitModel("MCSWLN06042")).toBe("WLN06042 MCS");
    expect(displayKitModel("SLCWLN04051")).toBe("WLN04051 SLC");
  });

  it("keeps codes that do not embed a variant prefix verbatim", () => {
    expect(displayKitModel("KSG")).toBe("KSG");
    expect(displayKitModel("KSG 470")).toBe("KSG 470");
    expect(displayKitModel("WSS")).toBe("WSS");
    expect(displayKitModel("Thera 450-650")).toBe("Thera 450-650");
  });
});