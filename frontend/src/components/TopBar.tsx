import { useEffect, useState } from "react";
import { listSubsidiaries, type Subsidiary } from "../api";
import { APP_NAME, LANGS, t, type Lang } from "../i18n";

export type Tab =
  | "home"
  | "offers"
  | "customers"
  | "import"
  | "workloads"
  | "config";

// One compact bar: brand, scope label, navigation tabs, filial scope and
// language. The search box lives on the pages that need it (Customers,
// Offers), not here, so the shell stays a single row.
//
// The "Filial:" control is the view scope, not a filter: it decides whose
// data the whole app shows. Admins pick any filial (or all of them);
// everyone else is pinned by the backend and only sees their badge here.
export default function TopBar({
  tab,
  setTab,
  lang,
  setLang,
  identity,
  scope,
  setScope,
  showConfig,
  showWorkloadCatalog,
}: {
  tab: Tab;
  setTab: (t: Tab) => void;
  lang: Lang;
  setLang: (l: Lang) => void;
  identity: {
    role: string;
    subsidiary_id: string | null;
    subsidiary_short?: string | null;
  } | null;
  scope: string | null;
  setScope: (s: string | null) => void;
  showConfig: boolean;
  showWorkloadCatalog: boolean;
}) {
  const [subsidiaries, setSubsidiaries] = useState<Subsidiary[]>([]);
  const isAdmin = identity?.role === "admin";

  // Only admins get the selector, so only admins need the catalog.
  useEffect(() => {
    if (!isAdmin) return;
    listSubsidiaries().then(setSubsidiaries).catch(() => setSubsidiaries([]));
  }, [isAdmin]);

  const currentScopeLabel = isAdmin
    ? scope ?? t(lang, "scope_admin_all")
    : identity?.subsidiary_id ?? identity?.subsidiary_short ?? "—";

  const tabs: { id: Tab; label: string }[] = [
    { id: "home", label: t(lang, "nav_offers") },
    { id: "offers", label: t(lang, "nav_new_offer") },
    { id: "customers", label: t(lang, "nav_customers") },
  ];
  // The workload catalog is shared by all subsidiaries; writes are restricted
  // again by the API to admins and sales users.
  if (showWorkloadCatalog) tabs.push({ id: "workloads", label: t(lang, "nav_workloads") });
  if (showConfig) tabs.push({ id: "config", label: t(lang, "nav_config") });
  // Import always sits after Settings.
  tabs.push({ id: "import", label: t(lang, "nav_import") });

  return (
    <header className="bg-white shadow">
      <div className="flex items-center gap-3 px-4 py-2">
        <img src="/guardian-logo.png" alt={APP_NAME} className="h-8 w-auto shrink-0" />
        <span
          className="max-w-[180px] shrink-0 truncate text-base font-bold text-gray-800"
          title={currentScopeLabel}
        >
          {currentScopeLabel}
        </span>
        <nav className="flex min-w-0 items-center gap-1 overflow-x-auto">
          {tabs.map((item) => (
            <button
              key={item.id}
              onClick={() => setTab(item.id)}
              className={`whitespace-nowrap rounded-full px-3 py-1.5 text-sm font-medium ${
                tab === item.id
                  ? "bg-weber-blue text-white"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>
        <div className="ml-auto flex shrink-0 items-center gap-4 whitespace-nowrap">
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-semibold text-gray-600">{t(lang, "scope_filial")}:</span>
            {isAdmin ? (
              <select
                value={scope ?? ""}
                onChange={(e) => setScope(e.target.value || null)}
                className="border rounded px-2 py-1 text-sm font-medium bg-white"
                title={t(lang, "scope_filial")}
              >
                <option value="">{t(lang, "scope_admin_all")}</option>
                {subsidiaries.map((s) => (
                  <option key={s.name} value={s.name}>
                    {s.name}
                  </option>
                ))}
              </select>
            ) : (
              <span className="text-sm font-medium text-gray-700">
                {identity?.subsidiary_short ?? identity?.subsidiary_id ?? "—"}
              </span>
            )}
          </div>
          <div className="flex items-center gap-1.5">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.8}
              className="h-4 w-4 text-gray-600"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="9" />
              <path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18" />
            </svg>
            <label htmlFor="language-select" className="text-xs font-semibold text-gray-600">
              {t(lang, "language_label")}:
            </label>
            <select
              id="language-select"
              value={lang}
              onChange={(e) => setLang(e.target.value as Lang)}
              className="border rounded px-2 py-1 text-sm font-medium bg-white"
              aria-label={t(lang, "language_label")}
            >
              {LANGS.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </header>
  );
}