import { describe, expect, it } from "vitest";

import { matchesQuery } from "./searchQuery";

describe("matchesQuery", () => {
  it("matches everything on an empty or whitespace query", () => {
    expect(matchesQuery("", "Infeeder CCA")).toBe(true);
    expect(matchesQuery("   ", "Infeeder CCA")).toBe(true);
  });

  it("is a case-insensitive substring test", () => {
    expect(matchesQuery("cca", "Infeeder CCA")).toBe(true);
    expect(matchesQuery("FEED", "Infeeder CCA")).toBe(true);
    expect(matchesQuery("cca", "Turntable CCU")).toBe(false);
  });

  it("matches when any field hits, including numbers", () => {
    expect(matchesQuery("1549", "wrong", "CCW-1549")).toBe(true);
    expect(matchesQuery("902", 902)).toBe(true);
  });

  it("ignores null and undefined fields instead of crashing", () => {
    expect(matchesQuery("x", null, undefined, "xray")).toBe(true);
    expect(matchesQuery("x", null, undefined)).toBe(false);
  });

  it("trims the query before comparing", () => {
    expect(matchesQuery("  CCA  ", "Infeeder CCA")).toBe(true);
  });
});
