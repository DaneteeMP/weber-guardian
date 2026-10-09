// Unresolved tab: installed materials that are not priced or need a decision.
// Nothing is assigned here. "Open" hands the material to the Material tab.
import { useEffect, useMemo, useState } from "react";
import type { ColumnDef } from "@tanstack/react-table";

import { listUnresolvedMaterials, type UnresolvedMaterial } from "../api";
import DataTable from "../components/DataTable";
import { t, type Lang } from "../i18n";
import { reasonKey } from "./labels";

export default function UnresolvedPanel({
  lang,
  revision,
  onOpen,
}: {
  lang: Lang;
  // Bumped by the parent after a rule or link changed elsewhere.
  revision: number;
  onOpen: (materialNo: string) => void;
}) {
  const [rows, setRows] = useState<UnresolvedMaterial[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    listUnresolvedMaterials({ limit: 500 })
      .then((result) => {
        if (cancelled) return;
        setRows(result.rows);
        setTotal(result.total);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Could not load unresolved materials");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [revision]);

  const columns = useMemo<ColumnDef<UnresolvedMaterial>[]>(
    () => [
      {
        accessorKey: "material_no",
        header: t(lang, "workload_material_no"),
        enableSorting: true,
        cell: ({ row }) => <span className="font-mono font-medium">{row.original.material_no}</span>,
      },
      {
        accessorKey: "name_en",
        header: t(lang, "workload_material_name"),
        enableSorting: true,
        cell: ({ row }) => <span className="text-gray-700">{row.original.name_en ?? "—"}</span>,
      },
      {
        accessorKey: "type_code",
        header: t(lang, "workload_legacy_code"),
        enableSorting: true,
        cell: ({ row }) => <span className="font-mono text-gray-600">{row.original.type_code ?? "—"}</span>,
      },
      {
        accessorKey: "reason",
        header: t(lang, "workload_needs_review"),
        enableSorting: true,
        cell: ({ row }) => (
          <span className="rounded bg-amber-100 px-2 py-0.5 text-xs text-amber-800">
            {t(lang, reasonKey(row.original.reason))}
          </span>
        ),
      },
      {
        accessorKey: "customers",
        header: t(lang, "workload_customers"),
        enableSorting: true,
        cell: ({ row }) => <span className="font-mono">{row.original.customers}</span>,
      },
      {
        id: "actions",
        header: "",
        enableSorting: false,
        cell: ({ row }) => (
          <div className="flex justify-end">
            <button
              type="button"
              onClick={() => onOpen(row.original.material_no)}
              className="text-xs font-medium text-weber-blue hover:underline"
            >
              {t(lang, "workload_open")}
            </button>
          </div>
        ),
      },
    ],
    [lang, onOpen],
  );

  return (
    <>
      <div className="mb-2 flex shrink-0 items-center justify-between gap-3">
        <p className="text-xs text-gray-600">{t(lang, "workload_unresolved_help")}</p>
        <span className="shrink-0 text-sm text-gray-500">{total.toLocaleString()}</span>
      </div>

      {error && (
        <div className="mb-2 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <DataTable
        data={rows}
        columns={columns}
        loading={loading}
        loadingText={t(lang, "dash_loading")}
        emptyText={t(lang, "workload_no_results")}
        getRowId={(row) => row.material_no}
      />
    </>
  );
}
