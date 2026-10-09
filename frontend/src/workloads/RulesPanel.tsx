// Rules tab: one row per global workload rule, with its real name, legacy
// code, hours and how many materials use it. Opening a row shows RuleModal.
import { useEffect, useMemo, useState } from "react";
import type { ColumnDef } from "@tanstack/react-table";

import { listWorkloadRules, type WorkloadRule } from "../api";
import DataTable from "../components/DataTable";
import { t, type Lang } from "../i18n";
import { formatHours } from "./labels";

const LOAD_LIMIT = 500;

export default function RulesPanel({
  lang,
  canEdit,
  revision,
  onOpen,
  onCreate,
}: {
  lang: Lang;
  canEdit: boolean;
  // Bumped by the parent after a change in another tab or in the modal.
  revision: number;
  onOpen: (rule: WorkloadRule) => void;
  onCreate: () => void;
}) {
  const [rows, setRows] = useState<WorkloadRule[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [needsReviewOnly, setNeedsReviewOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const timer = setTimeout(() => {
      setLoading(true);
      setError(null);
      listWorkloadRules({
        search: search.trim() || undefined,
        needs_review: needsReviewOnly ? true : undefined,
        limit: LOAD_LIMIT,
        offset: 0,
      })
        .then((result) => {
          if (cancelled) return;
          setRows(result.rows);
          setTotal(result.total);
        })
        .catch((e: unknown) => {
          if (!cancelled) setError(e instanceof Error ? e.message : "Could not load rules");
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, 200);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [search, needsReviewOnly, revision]);

  const columns = useMemo<ColumnDef<WorkloadRule>[]>(
    () => [
      {
        accessorKey: "name",
        header: t(lang, "workload_name"),
        enableSorting: true,
        cell: ({ row }) => <span className="font-medium">{row.original.name}</span>,
      },
      {
        accessorKey: "legacy_type_code",
        header: t(lang, "workload_legacy_code"),
        enableSorting: true,
        cell: ({ row }) => (
          <span className="font-mono text-gray-600">{row.original.legacy_type_code ?? "—"}</span>
        ),
      },
      {
        accessorKey: "workload",
        header: t(lang, "eq_workload"),
        enableSorting: true,
        cell: ({ row }) => <span className="font-mono">{formatHours(row.original.workload)}</span>,
      },
      {
        accessorKey: "linked_materials",
        header: t(lang, "workload_linked_materials"),
        enableSorting: true,
        cell: ({ row }) => <span className="font-mono">{row.original.linked_materials}</span>,
      },
      {
        accessorKey: "needs_review",
        header: t(lang, "workload_needs_review"),
        enableSorting: true,
        cell: ({ row }) =>
          row.original.needs_review ? (
            <span className="rounded bg-amber-100 px-2 py-0.5 text-xs text-amber-800">
              {t(lang, "workload_needs_review")}
            </span>
          ) : (
            <span className="text-gray-400">—</span>
          ),
      },
    ],
    [lang],
  );

  return (
    <>
      <div className="mb-2 flex shrink-0 items-center gap-2">
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder={t(lang, "workload_search")}
          className="min-w-0 flex-1 rounded border px-3 py-1.5 text-sm"
        />

        <span className="shrink-0 text-sm text-gray-500">
          {total.toLocaleString()} {t(lang, "workload_rules_label")}
        </span>

        <label className="flex shrink-0 items-center gap-1.5 whitespace-nowrap text-sm">
          <input
            type="checkbox"
            checked={needsReviewOnly}
            onChange={(event) => setNeedsReviewOnly(event.target.checked)}
          />
          {t(lang, "workload_review_only")}
        </label>

        {canEdit && (
          <button
            type="button"
            onClick={onCreate}
            className="shrink-0 rounded bg-weber-blue px-3 py-1.5 text-sm font-semibold text-white hover:opacity-90"
          >
            + {t(lang, "workload_rule_new")}
          </button>
        )}
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
        getRowId={(row) => row.id}
        onRowClick={onOpen}
      />
    </>
  );
}
