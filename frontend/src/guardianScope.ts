// Guardian service catalog: the six service modules and the services a
// salesperson can really sell. Shared by the OfferBuilder rail and the print
// dialog so the two screens can never drift apart.
//
// Rules encoded here (see backend GUARDIAN_SERVICES for the source of truth):
// - Only real services have a checkbox. Conditions (response times,
//   discounts, account team) are configured elsewhere; the software already
//   knows the inspection content, the equipment and the prices.
// - A module is never selected on its own: its state is derived from the
//   services ticked inside it.
// - Automatic services and the Basic Kit content are shown read-only.

export type GuardianService = {
  id: string;
  label: string;
};

export type GuardianModule = {
  id: string;
  code: string;
  label: string;
  services: readonly GuardianService[];
};

export const GUARDIAN_MODULES: readonly GuardianModule[] = [
  {
    id: "customer_service",
    code: "01",
    label: "Customer Service",
    services: [
      { id: "hotline", label: "Hotline" },
      { id: "remote_support", label: "Remote support" },
      { id: "on_site_assistance", label: "On-site assistance" },
    ],
  },
  {
    id: "spare_parts",
    code: "02",
    label: "Spare Parts & Availability",
    services: [
      { id: "supply_conditions", label: "Supply conditions" },
      { id: "priority_logistics", label: "Priority logistics" },
      { id: "parts_recommendations", label: "Parts recommendations" },
    ],
  },
  {
    id: "academy",
    code: "03",
    label: "Academy",
    services: [
      { id: "operator_training", label: "Operator training" },
      { id: "maintenance_training", label: "Maintenance training" },
    ],
  },
  {
    id: "blade_solutions",
    code: "04",
    label: "Knife & Blade Solutions",
    services: [
      { id: "knife_consulting", label: "Knife consulting" },
      { id: "sharpening", label: "Sharpening" },
      { id: "blade_supply_program", label: "Blade supply programme" },
    ],
  },
  {
    id: "optimization",
    code: "05",
    label: "Optimization & Performance",
    services: [
      { id: "epip_audit", label: "EPIP audit" },
      { id: "line_optimization", label: "Line optimization" },
      { id: "improvement_plan", label: "Improvement plan" },
      { id: "performance_mro_review", label: "Performance & MRO review" },
    ],
  },
  {
    id: "digital_services",
    code: "06",
    label: "Digital Services",
    services: [
      { id: "factory_cockpit", label: "Factory Cockpit" },
      { id: "monitoring", label: "Monitoring" },
    ],
  },
];

export const GUARDIAN_SERVICE_COUNT = GUARDIAN_MODULES.reduce(
  (total, module) => total + module.services.length,
  0,
);

// Always part of the agreement: nobody ticks them, the contract states them.
export const GUARDIAN_AUTO_SERVICES = [
  "Inspection",
  "Machine checklist",
  "Inspection report",
] as const;

// Basic Kit adds these to the maintenance annex without a checkbox.
export const GUARDIAN_BASIC_KIT_SERVICES = [
  "Preventive maintenance",
  "Spare parts / maintenance kit",
] as const;

export function moduleSelectedCount(
  module: GuardianModule,
  selections: readonly string[],
): number {
  return module.services.filter((service) => selections.includes(service.id)).length;
}

export function selectedServiceCount(selections: readonly string[]): number {
  return GUARDIAN_MODULES.reduce(
    (total, module) => total + moduleSelectedCount(module, selections),
    0,
  );
}

// Pure selection update: a service always carries its parent module, so the
// stored shape keeps working with older renders and the backend validator.
export function toggleGuardianService(
  current: string[],
  moduleId: string,
  serviceId: string,
): string[] {
  const next = current.includes(serviceId)
    ? current.filter((key) => key !== serviceId)
    : [...current, serviceId];
  return next.includes(moduleId) ? next : [...next, moduleId];
}
