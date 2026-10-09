// Lines tab: the machine-line families (30x, 40x, 1000...) whose hours live in
// equipment_catalog, not in workload_rules. A family prices a whole machine,
// slicer included, so these hours are never linked to a material.
//
// Saving sends PUT /line-workloads/{code} with the row's first machine code:
// the endpoint keys lines by machine_type and resolves back to this same
// family (also confirming that code). Offers only display the hours.
import { useEffect, useState } from "react";
import type { ColumnDef } from "@tanstack/react-table";

import {
  deleteLineWorkload,
  listLineWorkloads,
  updateLineWorkload,
  type LineWorkload,
} from "../api";
import DataTable from "../components/DataTable";
import { t, type Lang } from "../i18n";

export default function LineWorkloadsPanel({ lang, canEdit }: { lang: Lang; canEdit: boolean }) {
  const [rows, setRows] = useState<LineWorkload[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Unsaved hours per entry id; a key only exists while the row is dirty.
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [busyId, setBusyId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listLineWorkloads()
      .then((entries) => {
        if (!cancelled) setRows(entries);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Could not load lines");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  function value(entry: LineWorkload): string {
    if (entry.id in drafts) return drafts[entry.id];
    return entry.workload === null ? "" : String(entry.workload);
  }

  function isDirty(entry: LineWorkload): boolean {
    return entry.id in drafts && drafts[entry.id] !== (entry.workload === null ? "" : String(entry.workload));
  }

  async function save(entry: LineWorkload) {
    const code = entry.matches[0]?.match_value;
    if (!code) {
      setError(t(lang, "workload_line_no_code"));
      return;
    }

    const raw = value(entry).trim();
    setBusyId(entry.id);
    setError(null);
    try {
      await updateLineWorkload(code, { workload: raw === "" ? null : raw });
      setDrafts((prev) => {
        const next = { ...prev };
        delete next[entry.id];
        return next;
      });
      // Reload so stored hours and confirmed codes come from the backend.
      setRows(await listLineWorkloads());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save line hours");
    } finally {
      setBusyId(null);
    }
  }

  function revert(entry: LineWorkload) {
    setDrafts((prev) => {
      const next = { ...prev };
      delete next[entry.id];
      return next;
    });
  }

  // Delete a family nobody prices through; the backend answers 409 while a
  // customer's equipment still resolves to one of its codes.
  async function remove(entry: LineWorkload) {
    const text = t(lang, "workload_line_delete_confirm")
      .replace("{label}", entry.label)
      .replace("{n}", String(entry.matches.length));
    if (!window.confirm(text)) return;

    setBusyId(entry.id);
    setError(null);
    try {
      await deleteLineWorkload(entry.id);
      setDrafts((prev) => {
        const next = { ...prev };
        delete next[entry.id];
        return next;
      });
      setRows(await listLineWorkloads());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not delete line");
    } finally {
      setBusyId(null);
    }
  }

  const columns: ColumnDef<LineWorkload>[] = [
    {
      accessorKey: "label",
      header: t(lang, "workload_name"),
      enableSorting: true,
      cell: ({ row }) => <span className="font-medium">{row.original.label}</span>,
    },
    {
      id: "workload",
      header: () => <span className="block text-right">{t(lang, "eq_workload")}</span>,
      enableSorting: false,
      cell: ({ row }) => {
        const entry = row.original;
        if (!canEdit) {
          return (
            <span className="block text-right font-mono">
              {entry.workload === null ? t(lang, "workload_state_no_rule") : String(entry.workload)}
            </span>
          );
        }
        return (
          <input
            type="number"
            min="0"
            step="0.01"
            disabled={busyId === entry.id}
            value={value(entry)}
            onChange={(event) =>
              setDrafts((prev) => ({ ...prev, [entry.id]: event.target.value }))
            }
            className="ml-auto block w-28 rounded border px-2 py-1 text-right text-sm font-mono disabled:opacity-50"
          />
        );
      },
    },
    {
      id: "codes",
      header: t(lang, "workload_line_codes"),
      enableSorting: false,
      cell: ({ row }) => {
        const unconfirmed = row.original.matches.filter((match) => !match.is_confirmed);
        return (
          <span className="flex flex-wrap items-center gap-1.5 text-xs">
            <span className="font-mono text-gray-600">
              {row.original.matches.map((match) => match.match_value).join(", ") || "—"}
            </span>
            {unconfirmed.length > 0 && (
              <span className="rounded bg-amber-100 px-1.5 py-0.5 text-amber-800">
                {t(lang, "ob_unconfirmed")}
              </span>
            )}
          </span>
        );
      },
    },
    {
      id: "actions",
      header: "",
      enableSorting: false,
      cell: ({ row }) => {
        const entry = row.original;
        if (!canEdit) return <span />;
        return (
          <div className="flex items-center justify-end gap-2">
            {isDirty(entry) && (
              <>
                <button
                  type="button"
                  onClick={() => revert(entry)}
                  disabled={busyId === entry.id}
                  className="rounded border px-2 py-1 text-xs disabled:opacity-50"
                >
                  {t(lang, "cfg_cancel")}
                </button>
                <button
                  type="button"
                  onClick={() => void save(entry)}
                  disabled={busyId === entry.id || entry.matches.length === 0}
                  title={entry.matches.length === 0 ? t(lang, "workload_line_no_code") : undefined}
                  className="rounded bg-weber-blue px-2 py-1 text-xs font-semibold text-white disabled:opacity-50"
                >
                  {busyId === entry.id ? t(lang, "dash_loading") : t(lang, "cfg_save")}
                </button>
              </>
            )}
            <button
              type="button"
              onClick={() => void remove(entry)}
              disabled={busyId === entry.id}
              className="rounded border border-red-200 px-2 py-1 text-xs text-red-700 hover:bg-red-50 disabled:opacity-50"
            >
              {t(lang, "home_delete")}
            </button>
          </div>
        );
      },
    },
  ];

  return (
    <>
      <div className="mb-2 flex shrink-0 items-center justify-between gap-3">
        <p className="text-xs text-gray-600">{t(lang, "workload_lines_help")}</p>
        <span className="shrink-0 text-sm text-gray-500">{rows.length}</span>
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
        tableClassName="min-w-[560px]"
      />
    </>
  );
}
