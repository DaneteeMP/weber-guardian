// Create or edit one global workload rule, with its linked materials.
// Hours and name are global: saving here reprices every future draft that uses
// this rule. The legacy code is an optional label, editable here.
import { useEffect, useState, type FormEvent } from "react";

import {
  createWorkloadRule,
  deleteWorkloadRule,
  getWorkloadRule,
  updateWorkloadRule,
  type WorkloadRuleDetail,
} from "../api";
import Modal from "../components/Modal";
import { t, type Lang } from "../i18n";
import RuleMaterials from "./RuleMaterials";

type Form = { name: string; workload: string; legacyCode: string; needsReview: boolean };

const inputClass = "w-full rounded border px-2 py-1.5 text-sm";

export default function RuleModal({
  lang,
  canEdit,
  ruleId,
  onClose,
  onChanged,
}: {
  lang: Lang;
  canEdit: boolean;
  // null = create a new rule.
  ruleId: string | null;
  onClose: () => void;
  // Called after any change so the parent list reloads.
  onChanged: () => void;
}) {
  const [detail, setDetail] = useState<WorkloadRuleDetail | null>(null);
  const [form, setForm] = useState<Form>({ name: "", workload: "", legacyCode: "", needsReview: true });
  const [loading, setLoading] = useState(ruleId !== null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (ruleId === null) return;
    let cancelled = false;
    getWorkloadRule(ruleId)
      .then((row) => {
        if (cancelled) return;
        setDetail(row);
        setForm({
          name: row.name,
          workload: row.workload ?? "",
          legacyCode: row.legacy_type_code ?? "",
          needsReview: row.needs_review,
        });
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Could not load rule");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [ruleId]);

  // Reload the rule (after a material was linked or removed) and tell the list.
  async function reload() {
    if (ruleId === null) return;
    try {
      setDetail(await getWorkloadRule(ruleId));
      onChanged();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not reload rule");
    }
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const workload = form.workload.trim() || null;
    if (workload === null && !form.needsReview) {
      setError(t(lang, "workload_hours_required"));
      return;
    }

    setBusy(true);
    setError(null);
    try {
      if (ruleId === null) {
        await createWorkloadRule({
          name: form.name.trim(),
          workload,
          legacy_type_code: form.legacyCode.trim() || null,
          needs_review: form.needsReview,
        });
      } else {
        await updateWorkloadRule(ruleId, {
          name: form.name.trim(),
          workload,
          legacy_type_code: form.legacyCode.trim() || null,
          needs_review: form.needsReview,
        });
      }
      onChanged();
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save rule");
    } finally {
      setBusy(false);
    }
  }

  // Delete the rule; the backend answers 409 while a customer's material
  // still resolves to it, and the error box shows that message.
  async function remove() {
    if (ruleId === null || detail === null) return;
    const text =
      detail.linked_materials > 0
        ? t(lang, "workload_delete_confirm_links")
            .replace("{name}", detail.name)
            .replace("{n}", String(detail.linked_materials))
        : t(lang, "workload_delete_confirm").replace("{name}", detail.name);
    if (!window.confirm(text)) return;

    setBusy(true);
    setError(null);
    try {
      await deleteWorkloadRule(ruleId);
      onChanged();
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not delete rule");
    } finally {
      setBusy(false);
    }
  }

  const title = ruleId === null ? t(lang, "workload_rule_new") : t(lang, "workload_rule_title");

  return (
    <Modal title={title} onClose={onClose} widthClass="max-w-3xl">
      {loading ? (
        <div className="text-sm text-gray-500">{t(lang, "dash_loading")}</div>
      ) : (
        <div className="space-y-4">
          <form onSubmit={(event) => void save(event)} className="space-y-3">
            <label className="block text-xs">
              {t(lang, "workload_name")}
              <input
                required
                maxLength={128}
                disabled={!canEdit}
                value={form.name}
                onChange={(event) => setForm({ ...form, name: event.target.value })}
                className={`${inputClass} mt-1 disabled:bg-gray-100`}
              />
            </label>

            <div className="grid grid-cols-2 gap-3">
              <label className="block text-xs">
                {t(lang, "eq_workload")}
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  disabled={!canEdit}
                  value={form.workload}
                  onChange={(event) => setForm({ ...form, workload: event.target.value })}
                  className={`${inputClass} mt-1 disabled:bg-gray-100`}
                />
              </label>

              <label className="block text-xs">
                {t(lang, "workload_legacy_code")}
                <input
                  maxLength={16}
                  disabled={!canEdit}
                  value={form.legacyCode}
                  onChange={(event) => setForm({ ...form, legacyCode: event.target.value })}
                  className={`${inputClass} mt-1 font-mono disabled:bg-gray-100`}
                />
              </label>
            </div>

            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                disabled={!canEdit}
                checked={form.needsReview}
                onChange={(event) => setForm({ ...form, needsReview: event.target.checked })}
              />
              {t(lang, "workload_needs_review")}
            </label>

            {detail?.note && (
              <div className="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
                {detail.note}
              </div>
            )}

            <p className="text-xs text-gray-500">
              {t(lang, "workload_global_note")} {t(lang, "workload_legacy_note")}
            </p>

            {error && <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">{error}</div>}

            {canEdit && (
              <div className="flex items-center justify-end gap-2">
                {detail && ruleId !== null && (
                  <button
                    type="button"
                    onClick={() => void remove()}
                    disabled={busy}
                    className="mr-auto rounded border border-red-200 px-3 py-1.5 text-sm text-red-700 hover:bg-red-50 disabled:opacity-50"
                  >
                    {t(lang, "home_delete")}
                  </button>
                )}
                <button type="button" className="rounded border px-3 py-1.5 text-sm" onClick={onClose}>
                  {t(lang, "cfg_cancel")}
                </button>
                <button
                  type="submit"
                  disabled={busy}
                  className="rounded bg-weber-blue px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-50"
                >
                  {busy ? t(lang, "dash_loading") : t(lang, "cfg_save")}
                </button>
              </div>
            )}
          </form>

          {detail && (
            <RuleMaterials
              lang={lang}
              canEdit={canEdit}
              ruleId={detail.id}
              ruleName={detail.name}
              materials={detail.materials}
              onChanged={() => void reload()}
            />
          )}
        </div>
      )}
    </Modal>
  );
}
