// Display form of a compact machine_type kit key. Equipment rows store the
// key suffix first ("CCL304" = CCL + 304); the admin table spells the same
// machine as "Model  Suffix" ("304 CCL"). The inverse of the backend's
// canonical_model() rule, used by the Basic Kits panel and editable rows.
// Keys that do not embed a variant-code prefix (bare codes such as "KSG",
// names like "Thera 450-650") are returned verbatim.
const VARIANT_CODES = ["UB", "CCS", "CCL", "MLC", "MCS", "SLC", "RCS", "VPM", "CCB", "WSS"];

export function displayKitModel(model: string): string {
  for (const code of VARIANT_CODES) {
    if (model.startsWith(code) && model.length > code.length) {
      return `${model.slice(code.length)} ${code}`;
    }
  }
  return model;
}