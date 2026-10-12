// Basic Kits tab: one row per machine model with the kit workload hours
// (tied to the offer's basic-kit selector) and the spare-parts price.
//
// Offers sum these per machine_type through the maintenance draft
// (basic_kit_hours / basic_kit_price); this screen is the only place to
// maintain the table.
import { useEffect, useState } from "react";

import {
  createKit,
  deleteKit,
  listKits,
  updateKit,
  type Kit,
} from "../api";
import Button from "../components/Button";
import IconButton from "../components/IconButton";
import Modal from "../components/Modal";
import { t, type Lang } from "../i18n";
import { displayKitModel } from "../kitModels";

const num = (v: string, fallback: number) => {
  const n = Number(v);
  return Number.isFinite(n) && n >= 0 ? n : fallback;
};

function EditIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z" />
    </svg>
  );
}

function DeleteIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 6h18" />
      <path d="M8 6V4h8v2" />
      <path d="M19 6l-1 14H6L5 6" />
      <path d="M10 11v5" />
      <path d="M14 11v5" />
    </svg>
  );
}

type Editing = { model: string; hours: string; spares: string; isNew: boolean } | null;

export default function KitsPanel({ lang, canEdit }: { lang: Lang; canEdit: boolean }) {
  const [kits, setKits] = useState<Kit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState<Editing>(null);

  async function load() {
    try {
      setKits(await listKits());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load basic kits");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function save() {
    if (!editing || !editing.model.trim()) {
      setError(t(lang, "cfg_model_required"));
      return;
    }
    const model = editing.model.trim();
    const hours = num(editing.hours, 0);
    const spares = num(editing.spares, 0);
    try {
      if (editing.isNew) {
        await createKit(model, hours, spares);
      } else {
        await updateKit(model, hours, spares);
      }
      setEditing(null);
      setError(null);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save basic kit");
    }
  }

  async function remove(kit: Kit) {
    if (!window.confirm(t(lang, "cfg_delete"))) return;
    try {
      await deleteKit(kit.model);
      setError(null);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not delete basic kit");
    }
  }

  return (
    <>
      <div className="mb-2 flex shrink-0 items-center justify-between gap-3">
        <p className="text-xs text-gray-600">{t(lang, "workload_kits_help")}</p>
        {canEdit && (
          <Button size="sm" onClick={() => setEditing({ model: "", hours: "", spares: "", isNew: true })}>
            {t(lang, "cfg_add")}
          </Button>
        )}
      </div>

      {error && (
        <div className="mb-2 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <div className="min-h-0 flex-1 overflow-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0">
            <tr className="bg-weber-blue text-left text-white">
              <th className="px-3 py-1.5">Model</th>
              <th className="px-3 py-1.5 text-right">{t(lang, "eq_workload")}</th>
              <th className="px-3 py-1.5 text-right">{t(lang, "ob_spare")}</th>
              {canEdit && <th className="px-3 py-1.5" />}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={canEdit ? 4 : 3} className="px-3 py-4 text-center text-gray-500">
                  {t(lang, "dash_loading")}
                </td>
              </tr>
            ) : kits.length === 0 ? (
              <tr>
                <td colSpan={canEdit ? 4 : 3} className="px-3 py-4 text-center text-gray-500">
                  {t(lang, "workload_no_results")}
                </td>
              </tr>
            ) : (
              kits.map((kit) => (
                <tr key={kit.model} className="border-b">
                  <td className="px-3 py-1.5 font-mono">{displayKitModel(kit.model)}</td>
                  <td className="px-3 py-1.5 text-right font-mono">{kit.workload_basic_kit}</td>
                  <td className="px-3 py-1.5 text-right font-mono">{kit.spare_parts}</td>
                  {canEdit && (
                    <td className="px-3 py-1.5">
                      <div className="flex justify-end gap-1">
                        <IconButton
                          label={t(lang, "cfg_edit")}
                          onClick={() =>
                            setEditing({
                              model: kit.model,
                              hours: kit.workload_basic_kit,
                              spares: kit.spare_parts,
                              isNew: false,
                            })
                          }
                          icon={<EditIcon />}
                        />
                        <IconButton
                          label={t(lang, "cfg_delete")}
                          variant="danger"
                          onClick={() => void remove(kit)}
                          icon={<DeleteIcon />}
                        />
                      </div>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {editing && (
        <Modal title={t(lang, "cfg_kits")} onClose={() => setEditing(null)}>
          <div className="space-y-2">
            <label className="block text-xs">
              Model
              <input
                value={editing.model}
                disabled={!editing.isNew}
                placeholder="304 CCL"
                onChange={(e) => setEditing({ ...editing, model: e.target.value })}
                className="w-full rounded border px-2 py-1 text-sm disabled:bg-gray-100"
              />
            </label>
            <label className="block text-xs">
              {t(lang, "eq_workload")}
              <input
                type="number"
                min="0"
                step="0.01"
                value={editing.hours}
                onChange={(e) => setEditing({ ...editing, hours: e.target.value })}
                className="w-full rounded border px-2 py-1 text-sm"
              />
            </label>
            <label className="block text-xs">
              {t(lang, "ob_spare")}
              <input
                type="number"
                min="0"
                step="0.01"
                value={editing.spares}
                onChange={(e) => setEditing({ ...editing, spares: e.target.value })}
                className="w-full rounded border px-2 py-1 text-sm"
              />
            </label>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="secondary" size="sm" onClick={() => setEditing(null)}>
                {t(lang, "cfg_cancel")}
              </Button>
              <Button size="sm" onClick={() => void save()}>
                {t(lang, "cfg_save")}
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </>
  );
}