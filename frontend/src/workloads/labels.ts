// Translation keys for the states and reasons the backend returns. The backend
// sends codes; the screen decides the words. Kept here so every panel uses the
// same wording for the same code.
import type { Strings } from "../i18n";

export type StringKey = keyof Strings;

export function stateKey(state: "resolved" | "no_rule" | "not_in_dictionary" | "slicer"): StringKey {
  switch (state) {
    case "resolved":
      return "workload_state_resolved";
    case "no_rule":
      return "workload_state_no_rule";
    case "not_in_dictionary":
      return "workload_state_not_in_dictionary";
    case "slicer":
      return "workload_state_slicer";
  }
}

export function reasonKey(
  reason: "no_rule" | "no_hours" | "dictionary_conflict" | "not_in_dictionary",
): StringKey {
  switch (reason) {
    case "no_rule":
      return "workload_state_no_rule";
    case "no_hours":
      return "workload_reason_no_hours";
    case "dictionary_conflict":
      return "workload_dictionary_conflict";
    case "not_in_dictionary":
      return "workload_state_not_in_dictionary";
  }
}

/** Hours as shown in tables: "1.00 h", or a dash when not configured. */
export function formatHours(value: string | null): string {
  return value === null ? "—" : `${value} h`;
}
