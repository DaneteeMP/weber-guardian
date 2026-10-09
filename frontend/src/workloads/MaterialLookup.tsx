// Material tab: type a material number (raw serial like CCW01001-10901 is fine),
// see how it resolves today, and move it to another rule when needed.
import { useEffect, useState, type FormEvent } from "react";

import {
  linkRuleMaterial,
  listWorkloadRules,
  resolveMaterial,
  type MaterialResolution,
  type WorkloadRule,
} from "../api";
import { t, type Lang } from "../i18n";
import { formatHours, reasonKey, stateKey } from "./labels";

export default function MaterialLookup({
  lang,
  canEdit,
  initialMaterial,
  onChanged,
}: {
  lang: Lang;
  canEdit: boolean;
  // Material handed over from the Unresolved tab; looked up on arrival.
  initialMaterial: string | null;
  onChanged: () => void;
}) {
  const [query, setQuery] = useState("");
  const [resolution, setResolution] = useState<MaterialResolution | null>(null);
  const [rules, setRules] = useState<WorkloadRule[]>([]);
  const [targetRuleId, setTargetRuleId] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listWorkloadRules({ limit: 500 })
      .then((result) => {
        if (!cancelled) setRules(result.rows);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Could not load rules");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function lookup(value: string) {
    const material = value.trim();
    if (!material) {
      setError(t(lang, "workload_no_material"));
      return;
    }

    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      const result = await resolveMaterial(material);
      setResolution(result);
      setTargetRuleId("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not look up material");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    if (!initialMaterial) return;
    setQuery(initialMaterial);
    void lookup(initialMaterial);
    // Only when the parent hands over a new material.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialMaterial]);

  function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void lookup(query);
  }

  async function assign() {
    if (!resolution || !targetRuleId) return;
    // Link by the dictionary key, so a serial such as CCW01001-10901 assigns CCW01001.
    const materialNo = resolution.dictionary_material_no ?? resolution.material_no;

    setBusy(true);
    setError(null);
    try {
      const result = await linkRuleMaterial(materialNo, targetRuleId);
      const target = rules.find((rule) => rule.id === targetRuleId);
      setInfo(
        result.previous_rule_name && result.changed
          ? t(lang, "workload_moved_from").replace("{rule}", result.previous_rule_name)
          : t(lang, "workload_linked_to").replace("{rule}", target?.name ?? ""),
      );
      onChanged();
      await lookup(resolution.material_no);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not assign material");
    } finally {
      setBusy(false);
    }
  }

  const assignable = resolution !== null && (resolution.state === "resolved" || resolution.state === "no_rule");

  return (
    <div className="space-y-4">
      <form onSubmit={search} className="flex items-center gap-2">
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={t(lang, "workload_material_placeholder")}
          className="min-w-0 flex-1 rounded border px-3 py-1.5 text-sm"
        />
        <button
          type="submit"
          disabled={busy}
          className="shrink-0 rounded bg-weber-blue px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-50"
        >
          {t(lang, "workload_lookup")}
        </button>
      </form>

      {error && <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
      {info && <div className="rounded border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-900">{info}</div>}

      {resolution && (
        <div className="space-y-3 rounded border p-4 text-sm">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-base font-semibold">{resolution.material_no}</span>
            <span className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-700">
              {t(lang, stateKey(resolution.state))}
            </span>
            {resolution.has_conflict && (
              <span className="rounded bg-amber-100 px-2 py-0.5 text-xs text-amber-800">
                {t(lang, "workload_dictionary_conflict")}
              </span>
            )}
          </div>

          <dl className="grid grid-cols-[max-content_1fr] gap-x-4 gap-y-1 text-xs">
            <dt className="text-gray-500">{t(lang, "workload_material_no")}</dt>
            <dd className="font-mono">{resolution.dictionary_material_no ?? "—"}</dd>
            <dt className="text-gray-500">{t(lang, "workload_material_name")}</dt>
            <dd>{resolution.name_en ?? "—"}</dd>
            <dt className="text-gray-500">{t(lang, "workload_legacy_code")}</dt>
            <dd className="font-mono">{resolution.type_code ?? "—"}</dd>
            <dt className="text-gray-500">{t(lang, "workload_customers")}</dt>
            <dd className="font-mono">{resolution.customers}</dd>
            <dt className="text-gray-500">{t(lang, "workload_current_rule")}</dt>
            <dd>
              {resolution.rule ? (
                <>
                  <span className="font-medium">{resolution.rule.name}</span>{" "}
                  <span className="font-mono">{formatHours(resolution.rule.workload)}</span>
                  {resolution.rule.needs_review && (
                    <span className="ml-2 rounded bg-amber-100 px-2 py-0.5 text-amber-800">
                      {t(lang, "workload_needs_review")}
                    </span>
                  )}
                </>
              ) : (
                <span className="text-gray-500">
                  {resolution.state === "not_in_dictionary"
                    ? t(lang, reasonKey("not_in_dictionary"))
                    : t(lang, "workload_state_no_rule")}
                </span>
              )}
            </dd>
          </dl>

          {canEdit && assignable && (
            <div className="flex items-center gap-2 border-t pt-3">
              <select
                value={targetRuleId}
                onChange={(event) => setTargetRuleId(event.target.value)}
                className="min-w-0 flex-1 rounded border px-2 py-1.5 text-sm"
              >
                <option value="">{t(lang, "workload_select_rule")}</option>
                {rules.map((rule) => (
                  <option key={rule.id} value={rule.id}>
                    {rule.name} · {formatHours(rule.workload)}
                  </option>
                ))}
              </select>
              <button
                type="button"
                disabled={busy || !targetRuleId}
                onClick={() => void assign()}
                className="shrink-0 rounded bg-weber-blue px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-50"
              >
                {t(lang, "workload_assign_rule")}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
