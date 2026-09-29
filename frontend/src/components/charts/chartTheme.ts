// Shared chart vocabulary. Colours and small helpers live here so every chart
// in the app speaks the same visual language and only the chart files change
// when the palette does.
import type { OffersSummary } from "../../api";

export type StatusCount = OffersSummary["by_status"][number];
export type MonthCount = OffersSummary["monthly"][number];
export type RankingRow = OffersSummary["ranking"][number];

// Weber blue, same as the weber-blue tailwind colour.
export const CHART_BLUE = "#1D4F91";

// Offer statuses are fixed data, not free text, so a fixed palette is safe.
// Anything unexpected falls back to the brand blue instead of a random colour.
export const STATUS_COLORS: Record<string, string> = {
  Draft: "#9ca3af",
  "Pending response": "#f59e0b",
  Finished: "#16a34a",
  Cancelled: "#dc2626",
  Rejected: "#6b7280",
};

export function statusColor(status: string): string {
  return STATUS_COLORS[status] ?? CHART_BLUE;
}

// Y axis labels get a wide column now, so the default cut is generous. Anything
// longer still shows in full on hover, which the axis tick renders as a title.
export function shortName(name: string, max = 30): string {
  return name.length > max ? `${name.slice(0, max - 1)}…` : name;
}

// recharts needs a real DOM height to measure, so charts always sit inside a
// wrapper div with an explicit height class. Never render a chart bare.
export const TOOLTIP_STYLE = {
  fontSize: 11,
  backgroundColor: "#ffffff",
  border: "1px solid #e5e7eb",
  borderRadius: 4,
} as const;

// The tooltip only displays read-only information, so it should not intercept
// pointer events. Chart wrappers also clip its positioned box to prevent it
// from briefly extending the page and introducing scrollbars during hover.
export const TOOLTIP_WRAPPER_STYLE = { pointerEvents: "none" } as const;
