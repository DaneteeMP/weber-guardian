// Materials linked to one rule: list, add (or move from another rule) and remove.
// A material belongs to at most one rule; adding it here moves it when it had one.
import { useState, type FormEvent } from "react";
import type { ColumnDef } from "@tanstack/react-table";

import { linkRuleMaterial, unlinkRuleMaterial, type RuleMaterial } from "../api";
import DataTable from "../components/DataTable";
import { t, type Lang } from "../i18n";

export default function RuleMaterials({
  lang,
  canEdit,
  ruleId,
  ruleName,
  materials,
  onChanged,
}: {
  lang: Lang;
  canEdit: boolean;
  ruleId: string;
  ruleName: string;
  materials: RuleMaterial[];
  onChanged: () => void;
}) {
  const [materialNo, setMaterialNo] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  async function add(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = materialNo.trim();
    if (!value) {
      setError(t(lang, "workload_no_material"));
      return;
    }

    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      const result = await linkRuleMaterial(value, ruleId);
      setInfo(
        result.previous_rule_name && result.changed
          ? t(lang, "workload_moved_from").replace("{rule}", result.previous_rule_name)
          : t(lang, "workload_linked_to").replace("{rule}", ruleName),
      );
      setMaterialNo("");
      onChanged();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not link material");
    } finally {
      setBusy(false);
    }
  }

  async function remove(row: RuleMaterial) {
    const question = t(lang, "workload_remove_material_confirm").replace("{material}", row.material_no);
    if (!window.confirm(question)) return;

    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      await unlinkRuleMaterial(row.material_no);
      onChanged();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not remove material");
    } finally {
      setBusy(false);
    }
  }

  // Plain array on purpose: cheap to rebuild, and it always sees the current busy state.
  const columns: ColumnDef<RuleMaterial>[] = [
      {
        accessorKey: "material_no",
        header: t(lang, "workload_material_no"),
        cell: ({ row }) => <span className="font-mono font-medium">{row.original.material_no}</span>,
      },
      {
        accessorKey: "name_en",
        header: t(lang, "workload_material_name"),
        cell: ({ row }) => <span className="text-gray-700">{row.original.name_en ?? "—"}</span>,
      },
      {
        accessorKey: "type_code",
        header: t(lang, "workload_legacy_code"),
        cell: ({ row }) => <span className="font-mono text-gray-600">{row.original.type_code ?? "—"}</span>,
      },
      {
        accessorKey: "customers",
        header: t(lang, "workload_customers"),
        cell: ({ row }) => <span className="font-mono">{row.original.customers}</span>,
      },
      {
        id: "flags",
        header: "",
        enableSorting: false,
        cell: ({ row }) => (
          <div className="flex items-center justify-end gap-2">
            {row.original.has_conflict && (
              <span className="rounded bg-amber-100 px-2 py-0.5 text-xs text-amber-800">
                {t(lang, "workload_dictionary_conflict")}
              </span>
            )}
            {canEdit && (
              <button
                type="button"
                disabled={busy}
                onClick={() => void remove(row.original)}
                className="text-xs text-red-600 hover:underline disabled:opacity-50"
              >
                {t(lang, "workload_remove_material")}
              </button>
            )}
          </div>
        ),
      },
    ];

  return (
    <div className="space-y-2">
      <div className="text-xs font-semibold uppercase tracking-wide text-gray-500">
        {t(lang, "workload_linked_materials")} ({materials.length})
      </div>

      {canEdit && (
        <form onSubmit={(event) => void add(event)} className="flex items-center gap-2">
          <input
            value={materialNo}
            onChange={(event) => setMaterialNo(event.target.value)}
            placeholder={t(lang, "workload_material_placeholder")}
            className="min-w-0 flex-1 rounded border px-2 py-1.5 text-sm"
          />
          <button
            type="submit"
            disabled={busy}
            className="shrink-0 rounded bg-weber-blue px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-50"
          >
            {t(lang, "workload_add_material")}
          </button>
        </form>
      )}

      {error && <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">{error}</div>}
      {info && <div className="rounded border border-green-200 bg-green-50 px-3 py-2 text-xs text-green-900">{info}</div>}

      <div className="max-h-72 overflow-auto rounded border">
        <DataTable
          data={materials}
          columns={columns}
          emptyText={t(lang, "workload_no_results")}
          getRowId={(row) => row.material_no}
          tableClassName="min-w-[560px]"
        />
      </div>
    </div>
  );
}
