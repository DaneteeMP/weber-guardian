// Shared status badge palette for offer statuses. One mapping for the whole
// app (table badges, builder header, sidebar) so colours never drift between
// pages. Mirrors STATUS_COLORS in components/charts/chartTheme.ts.
export function statusTone(s: string | null | undefined): string {
  switch (s) {
    case "Finished":
      return "bg-green-100 text-green-800";
    case "Pending response":
      return "bg-amber-100 text-amber-800";
    case "Accepted":
    case "In progress":
      return "bg-blue-100 text-blue-800";
    case "Pending invoicing":
      return "bg-violet-100 text-violet-800";
    case "Pending Service":
      return "bg-cyan-100 text-cyan-800";
    case "Cancelled":
    case "Rejected":
      return "bg-red-100 text-red-800";
    default:
      return "bg-slate-100 text-slate-600";
  }
}
