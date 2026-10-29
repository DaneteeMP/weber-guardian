import { useEffect, useState } from "react";
import { listSubsidiaries, type Subsidiary } from "../api";
import { APP_NAME, LANGS, t, type Lang } from "../i18n";

export type Tab =
  | "home"
  | "offers"
  | "customers"
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
  onNew,
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
  onNew: () => void;
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

  return (
    <header className="border-b border-line bg-white">
      <div className="flex min-h-0 items-stretch gap-3 px-4">
        <img src="/guardian-logo.png" alt={APP_NAME} className="h-8 w-auto shrink-0 self-center" />
        <span
          className="max-w-[180px] shrink-0 truncate self-center text-base font-bold text-ink"
          title={currentScopeLabel}
        >
          {currentScopeLabel}
        </span>
        <nav className="flex min-h-0 min-w-0 items-stretch overflow-x-auto">
          {tabs.map((item) => (
            <button
              key={item.id}
              onClick={() => (item.id === "offers" ? onNew() : setTab(item.id))}
              className={`flex items-center whitespace-nowrap border-b-2 px-3 pt-1 text-sm font-medium transition-colors ${
                tab === item.id
                  ? "border-primary text-primary"
                  : "border-transparent text-muted hover:text-ink"
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>
        <div className="ml-auto flex shrink-0 items-center gap-4 whitespace-nowrap py-2">
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-medium text-muted">{t(lang, "scope_filial")}:</span>
            {isAdmin ? (
              <select
                value={scope ?? ""}
                onChange={(e) => setScope(e.target.value || null)}
                className="ui-input h-8 text-sm font-medium"
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
              <span className="text-sm font-medium text-ink">
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
              className="h-4 w-4 text-muted"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="9" />
              <path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18" />
            </svg>
            <label htmlFor="language-select" className="text-xs font-medium text-muted">
              {t(lang, "language_label")}:
            </label>
            <select
              id="language-select"
              value={lang}
              onChange={(e) => setLang(e.target.value as Lang)}
              className="ui-input h-8 text-sm font-medium"
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
