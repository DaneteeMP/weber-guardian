// Guardian contract scope catalog: the six modules and their service options.
//
// Shared by the OfferBuilder right rail and the Print PDF modal, so the two
// screens can never drift apart. The ids are the canonical keys the backend
// validates (GUARDIAN_OPTIONS_BY_MODULE in offers/schemas.py); the labels
// stay English, like the rest of the builder UI.

export type GuardianModule = {
  id: string;
  label: string;
  options: readonly (readonly [string, string])[];
};

export const GUARDIAN_SCOPE: readonly GuardianModule[] = [
  {
    id: "maintenance_inspection",
    label: "Maintenance & Inspection",
    options: [
      ["inspection", "Inspection / Annual Inspection"],
      ["machine_checklist", "Machine Checklist"],
      ["inspection_report", "Inspection Report"],
      ["preventive_maintenance", "Preventive Maintenance"],
      ["maintenance_kit", "Spare Parts / Maintenance Kit"],
    ],
  },
  {
    id: "service_support",
    label: "Service Support",
    options: [
      ["standard_hotline", "Standard Hotline"],
      ["remote_support", "Remote Support"],
      ["priority_response", "Priority Response"],
    ],
  },
  {
    id: "parts_availability",
    label: "Parts & Availability",
    options: [
      ["parts_discount", "Parts Discount"],
      ["priority_handling", "Priority Handling"],
      ["recommended_parts_list", "Recommended Parts List"],
    ],
  },
  {
    id: "blade_solutions",
    label: "Blade Solutions",
    options: [
      ["blade_discount", "Blade Discount"],
      ["stock_agreement", "Stock Agreement"],
      ["sharpening_assessment", "Sharpening Assessment"],
      ["blade_application_review", "Blade Application Review"],
    ],
  },
  {
    id: "training_optimization",
    label: "Training & Optimization",
    options: [
      ["operator_training", "Operator Training"],
      ["maintenance_training", "Maintenance Training"],
      ["line_optimization", "Line Optimization"],
      ["epip_audit", "EPIP Audit"],
    ],
  },
  {
    id: "digital_services",
    label: "Digital Services",
    options: [
      ["factory_cockpit", "Factory Cockpit"],
      ["performance_review", "Performance Review"],
      ["mro_review", "MRO Review"],
      ["dedicated_account_team", "Dedicated Account Team"],
    ],
  },
];

// Pure selection updates that keep the backend invariant: an option always
// carries its parent module, and deselecting a module drops its options.

export function toggleGuardianModule(
  current: string[],
  moduleId: string,
  optionIds: readonly string[],
): string[] {
  if (current.includes(moduleId)) {
    return current.filter((key) => key !== moduleId && !optionIds.includes(key));
  }
  return [...current, moduleId];
}

export function toggleGuardianOption(
  current: string[],
  moduleId: string,
  optionId: string,
): string[] {
  const next = current.includes(optionId)
    ? current.filter((key) => key !== optionId)
    : [...current, optionId];
  return next.includes(moduleId) ? next : [...next, moduleId];
}
