// Workload Catalog: every workload of the company, the only place hours are edited.
//
// Four views over one model:
//   * Workloads: each global workload with its real name, hours and materials;
//   * Lines: the machine-line families (30x, 40x...) priced by equipment_catalog;
//   * Material: how one material number resolves, and moving it to another workload;
//   * Unresolved: installed materials that are not priced, for a human decision.
// The screen only shows and sends; the backend decides every resolution.
import { useCallback, useState } from "react";

import type { WorkloadRule } from "./api";
import SectionCard from "./components/SectionCard";
import { t, type Lang } from "./i18n";
import LineWorkloadsPanel from "./workloads/LineWorkloadsPanel";
import MaterialLookup from "./workloads/MaterialLookup";
import RuleModal from "./workloads/RuleModal";
import RulesPanel from "./workloads/RulesPanel";
import UnresolvedPanel from "./workloads/UnresolvedPanel";

type CatalogTab = "rules" | "lines" | "material" | "unresolved";

type ModalState = { ruleId: string | null } | null;

export default function WorkloadCatalog({ lang, canEdit }: { lang: Lang; canEdit: boolean }) {
  const [tab, setTab] = useState<CatalogTab>("rules");
  // Bumped after any change so the other panels reload their data.
  const [revision, setRevision] = useState(0);
  const [modal, setModal] = useState<ModalState>(null);
  const [materialFocus, setMaterialFocus] = useState<string | null>(null);

  const bump = useCallback(() => setRevision((value) => value + 1), []);

  const openMaterial = useCallback((materialNo: string) => {
    setMaterialFocus(materialNo);
    setTab("material");
  }, []);

  function openRule(rule: WorkloadRule) {
    setModal({ ruleId: rule.id });
  }

  const tabs: { key: CatalogTab; label: string }[] = [
    { key: "rules", label: t(lang, "workload_tab_rules") },
    { key: "lines", label: t(lang, "workload_tab_lines") },
    { key: "material", label: t(lang, "workload_tab_material") },
    { key: "unresolved", label: t(lang, "workload_tab_unresolved") },
  ];

  return (
    <main className="flex h-full min-h-0 w-full flex-col overflow-hidden">
      <div className="min-h-0 flex-1 overflow-hidden p-4">
        <div className="flex h-full min-h-0 flex-col">
          <h1 className="mb-3 shrink-0 text-2xl font-bold text-gray-900">{t(lang, "workload_title")}</h1>

          <SectionCard className="flex min-h-0 flex-1 flex-col">
            <div className="mb-3 flex shrink-0 overflow-hidden rounded border text-sm">
              {tabs.map((item) => (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => setTab(item.key)}
                  className={`px-3 py-1.5 ${
                    tab === item.key ? "bg-weber-blue font-semibold text-white" : "bg-white hover:bg-gray-50"
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>

            <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
              {tab === "rules" && (
                <RulesPanel
                  lang={lang}
                  canEdit={canEdit}
                  revision={revision}
                  onOpen={openRule}
                  onCreate={() => setModal({ ruleId: null })}
                />
              )}

              {tab === "lines" && <LineWorkloadsPanel lang={lang} canEdit={canEdit} />}

              {tab === "material" && (
                <div className="min-h-0 flex-1 overflow-auto">
                  <MaterialLookup
                    lang={lang}
                    canEdit={canEdit}
                    initialMaterial={materialFocus}
                    onChanged={bump}
                  />
                </div>
              )}

              {tab === "unresolved" && (
                <UnresolvedPanel lang={lang} revision={revision} onOpen={openMaterial} />
              )}
            </div>
          </SectionCard>
        </div>
      </div>

      {modal && (
        <RuleModal
          lang={lang}
          canEdit={canEdit}
          ruleId={modal.ruleId}
          onClose={() => setModal(null)}
          onChanged={bump}
        />
      )}
    </main>
  );
}
