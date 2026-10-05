import { useEffect, useMemo, useState, type FormEvent } from "react";
import type { ColumnDef } from "@tanstack/react-table";

import {
  createComponentWorkload,
  deleteComponentWorkload,
  importWorkloadCsv,
  listComponentWorkloads,
  updateComponentWorkload,
  type ComponentWorkload,
  type WorkloadImportReport,
} from "./api";
import DataTable from "./components/DataTable";
import IconButton from "./components/IconButton";
import Modal from "./components/Modal";
import SectionCard from "./components/SectionCard";
import { t, type Lang } from "./i18n";

const LOAD_LIMIT = 200;

type WorkloadDraft = {
  id?: string;
  name: string;
  component_type: string;
  workload: string;
  needs_review: boolean;
};

function EditIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z" />
    </svg>
  );
}

function DeleteIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path d="M3 6h18" />
      <path d="M8 6V4h8v2" />
      <path d="M19 6l-1 14H6L5 6" />
      <path d="M10 11v5" />
      <path d="M14 11v5" />
    </svg>
  );
}

export default function WorkloadCatalog({
  lang,
  canEdit,
}: {
  lang: Lang;
  canEdit: boolean;
}) {
  const [rows, setRows] = useState<ComponentWorkload[]>([]);
  const [total, setTotal] = useState(0);

  const [search, setSearch] = useState("");
  const [needsReviewOnly, setNeedsReviewOnly] = useState(false);

  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const [error, setError] = useState<string | null>(null);

  const [draft, setDraft] = useState<WorkloadDraft | null>(null);

  const [importOpen, setImportOpen] = useState(false);
  const [report, setReport] = useState<WorkloadImportReport | null>(null);

  async function load() {
    setLoading(true);
    setError(null);

    try {
      const result = await listComponentWorkloads({
        search: search.trim() || undefined,
        needs_review: needsReviewOnly ? true : undefined,
        limit: LOAD_LIMIT,
        offset: 0,
      });

      setRows(result.rows);
      setTotal(result.total);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Could not load workloads",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      void load();
    }, 200);

    return () => clearTimeout(timer);

    // load intentionally follows the current filters.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, needsReviewOnly]);

  function startCreate() {
    setDraft({
      name: "",
      component_type: "",
      workload: "",
      needs_review: true,
    });
  }

  function startEdit(row: ComponentWorkload) {
    setDraft({
      id: row.id,
      name: row.name,
      component_type: row.component_type,
      workload: row.workload ?? "",
      needs_review: row.needs_review,
    });
  }

  async function saveDraft(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!draft) return;

    const workload = draft.workload.trim() || null;

    if (!draft.needs_review && workload === null) {
      setError(t(lang, "workload_hours_required"));
      return;
    }

    setBusy(true);
    setError(null);

    try {
      if (draft.id) {
        await updateComponentWorkload(draft.id, {
          name: draft.name.trim(),
          workload,
          needs_review: draft.needs_review,
        });
      } else {
        await createComponentWorkload({
          name: draft.name.trim(),
          component_type: draft.component_type.trim(),
          workload,
          needs_review: draft.needs_review,
        });
      }

      setDraft(null);
      await load();
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Could not save workload",
      );
    } finally {
      setBusy(false);
    }
  }

  async function handleImport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const input = event.currentTarget.elements.namedItem(
      "sap-csv",
    ) as HTMLInputElement;

    const file = input.files?.[0];

    if (!file) {
      setError("Please select a CSV file.");
      return;
    }

    setBusy(true);
    setError(null);

    try {
      const result = await importWorkloadCsv(file);

      setReport(result);
      setImportOpen(false);

      input.value = "";

      await load();
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Could not import SAP CSV",
      );
    } finally {
      setBusy(false);
    }
  }

  async function remove(row: ComponentWorkload) {
    const confirmation = t(lang, "workload_delete_confirm").replace(
      "{name}",
      row.name,
    );

    if (!window.confirm(confirmation)) return;

    setError(null);

    try {
      await deleteComponentWorkload(row.id);
      await load();
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Could not delete workload",
      );
    }
  }

  const columns = useMemo<ColumnDef<ComponentWorkload>[]>(
    () => [
      {
        accessorKey: "name",
        header: t(lang, "workload_name"),
        enableSorting: true,
        cell: ({ row }) => (
          <span className="font-medium">{row.original.name}</span>
        ),
      },
      {
        accessorKey: "component_type",
        header: t(lang, "workload_component_type"),
        enableSorting: true,
        cell: ({ row }) => (
          <span className="text-gray-600">
            {row.original.component_type || "—"}
          </span>
        ),
      },
      {
        accessorKey: "workload",
        header: t(lang, "eq_workload"),
        enableSorting: true,
        sortingFn: (rowA, rowB, columnId) => {
          const a = rowA.getValue<number | null>(columnId);
          const b = rowB.getValue<number | null>(columnId);

          if (a === null && b === null) return 0;
          if (a === null) return 1;
          if (b === null) return -1;

          return Number(a) - Number(b);
        },
        cell: ({ row }) => (
          <span className="font-mono">
            {row.original.workload === null
              ? "—"
              : `${row.original.workload} h`}
          </span>
        ),
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
      {
        id: "actions",
        header: "",
        enableSorting: false,
        cell: ({ row }) =>
          canEdit ? (
            <div className="flex justify-end gap-1">
              <IconButton
                label={t(lang, "cfg_edit")}
                onClick={() => startEdit(row.original)}
                icon={<EditIcon />}
              />

              <IconButton
                label={t(lang, "cfg_delete")}
                variant="danger"
                onClick={() => void remove(row.original)}
                icon={<DeleteIcon />}
              />
            </div>
          ) : null,
      },
    ],
    [lang, canEdit],
  );

  const inputClass = "w-full rounded border px-2 py-1.5 text-sm";

  return (
    <main className="flex h-full min-h-0 w-full flex-col overflow-hidden">
      <div className="min-h-0 flex-1 overflow-hidden p-4">
        <div className="flex h-full min-h-0 flex-col">
          {/* Page title */}
          <h1 className="mb-3 shrink-0 text-2xl font-bold text-gray-900">
            {t(lang, "workload_title")}
          </h1>

          {/* Error */}
          {error && (
            <div className="mb-3 shrink-0 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Import report */}
          {report && (
            <div className="mb-3 flex shrink-0 items-center justify-between gap-3 rounded border border-green-200 bg-green-50 px-3 py-2 text-xs text-green-950">
              <div className="flex flex-wrap gap-x-4 gap-y-1">
                <span className="font-semibold">
                  {t(lang, "workload_import_report")}
                </span>

                <span>
                  {t(lang, "workload_source_rows")}:{" "}
                  {report.rows_read.toLocaleString()}
                </span>

                <span>
                  {t(lang, "workload_products")}:{" "}
                  {report.products_discovered.toLocaleString()}
                </span>

                <span>
                  {t(lang, "workload_created")}:{" "}
                  {report.workloads_created.toLocaleString()}
                </span>

                <span>
                  {t(lang, "workload_preserved")}:{" "}
                  {report.workloads_preserved.toLocaleString()}
                </span>

                <span>
                  {t(lang, "workload_review_created")}:{" "}
                  {report.workloads_needing_review_created.toLocaleString()}
                </span>
              </div>

              <button
                type="button"
                onClick={() => setReport(null)}
                className="shrink-0 text-gray-500 hover:text-gray-900"
                aria-label="Close import report"
              >
                ×
              </button>
            </div>
          )}

          {/* Content */}
          <SectionCard className="flex min-h-0 flex-1 flex-col">
            {/* Toolbar */}
            <div className="mb-2 flex shrink-0 items-center gap-2">
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder={t(lang, "workload_search")}
                className="min-w-0 flex-1 rounded border px-3 py-1.5 text-sm"
              />

              <span className="shrink-0 text-sm text-gray-500">
                {total.toLocaleString()} entries
              </span>

              <label className="flex shrink-0 items-center gap-1.5 whitespace-nowrap text-sm">
                <input
                  type="checkbox"
                  checked={needsReviewOnly}
                  onChange={(event) =>
                    setNeedsReviewOnly(event.target.checked)
                  }
                />

                {t(lang, "workload_review_only")}
              </label>

              {canEdit && (
                <>
                  <button
                    type="button"
                    onClick={() => setImportOpen(true)}
                    className="shrink-0 rounded border px-3 py-1.5 text-sm hover:bg-gray-50"
                  >
                    {t(lang, "workload_import")}
                  </button>

                  <button
                    type="button"
                    onClick={startCreate}
                    className="shrink-0 rounded bg-weber-blue px-3 py-1.5 text-sm font-semibold text-white hover:opacity-90"
                  >
                    + {t(lang, "cfg_add")}
                  </button>
                </>
              )}
            </div>

            {/* Table */}
            <DataTable
              data={rows}
              columns={columns}
              loading={loading}
              loadingText={t(lang, "dash_loading")}
              emptyText={t(lang, "workload_no_results")}
              getRowId={(row) => row.id}
            />
          </SectionCard>
        </div>
      </div>

      {/* Create / edit modal */}
      {draft && (
        <Modal
          title={draft.id ? t(lang, "cfg_edit") : t(lang, "cfg_add")}
          onClose={() => setDraft(null)}
        >
          <form
            onSubmit={(event) => void saveDraft(event)}
            className="space-y-3"
          >
            <label className="block text-xs">
              {t(lang, "workload_name")}

              <input
                required
                maxLength={256}
                value={draft.name}
                onChange={(event) =>
                  setDraft({
                    ...draft,
                    name: event.target.value,
                  })
                }
                className={`${inputClass} mt-1`}
              />
            </label>

            <label className="block text-xs">
              {t(lang, "workload_component_type")}

              <input
                required
                maxLength={128}
                value={draft.component_type}
                disabled={Boolean(draft.id)}
                onChange={(event) =>
                  setDraft({
                    ...draft,
                    component_type: event.target.value,
                  })
                }
                className={`${inputClass} mt-1 disabled:bg-gray-100`}
              />
            </label>

            <label className="block text-xs">
              {t(lang, "eq_workload")}

              <input
                type="number"
                min="0"
                step="0.01"
                value={draft.workload}
                onChange={(event) =>
                  setDraft({
                    ...draft,
                    workload: event.target.value,
                  })
                }
                className={`${inputClass} mt-1`}
              />
            </label>

            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={draft.needs_review}
                onChange={(event) =>
                  setDraft({
                    ...draft,
                    needs_review: event.target.checked,
                  })
                }
              />

              {t(lang, "workload_needs_review")}
            </label>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                className="rounded border px-3 py-1.5 text-sm"
                onClick={() => setDraft(null)}
              >
                {t(lang, "cfg_cancel")}
              </button>

              <button
                type="submit"
                disabled={busy}
                className="rounded bg-weber-blue px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-50"
              >
                {busy
                  ? t(lang, "dash_loading")
                  : t(lang, "cfg_save")}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* Import CSV modal */}
      {canEdit && importOpen && (
        <Modal
          title={t(lang, "workload_import")}
          onClose={() => setImportOpen(false)}
        >
          <form
            onSubmit={(event) => void handleImport(event)}
            className="space-y-3"
          >
            <input
              className={inputClass}
              type="file"
              name="sap-csv"
              accept=".csv,text/csv"
            />

            <p className="text-xs text-gray-600">
              {t(lang, "workload_import_help")}
            </p>

            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setImportOpen(false)}
                className="rounded border px-3 py-1.5 text-sm"
              >
                {t(lang, "cfg_cancel")}
              </button>

              <button
                type="submit"
                disabled={busy}
                className="rounded bg-weber-blue px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-50"
              >
                {busy
                  ? t(lang, "workload_importing")
                  : t(lang, "workload_import")}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </main>
  );
}