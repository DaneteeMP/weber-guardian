import { useEffect, useState } from "react";
import { listSubsidiaries, type Subsidiary } from "../api";
import { LANGS, t, type Lang } from "../i18n";

export type Tab = "home" | "offers" | "customers" | "import" | "dashboard" | "config" | "subsidiaries";

// Salesforce-style shell: brand row (logo, global search, identity) plus
// the tab bar. No routing library: tabs are plain state in App.
//
// The "Filial:" control is the view scope, not a filter: it decides whose
// data the whole app shows. Admins pick any filial (or all of them);
// everyone else is pinned by the backend and only sees their badge here.
export default function TopBar({
  tab,
  setTab,
  lang,
  setLang,
  search,
  setSearch,
  identity,
  scope,
  setScope,
  showConfig,
  showSubsidiaries,
}: {
  tab: Tab;
  setTab: (t: Tab) => void;
  lang: Lang;
  setLang: (l: Lang) => void;
  search: string;
  setSearch: (s: string) => void;
  identity: {
    external_id: string;
    role: string;
    subsidiary_id: string | null;
    subsidiary_short?: string | null;
    scope_subsidiary_id?: string | null;
    scope_subsidiary_short?: string | null;
  } | null;
  scope: string | null;
  setScope: (s: string | null) => void;
  showConfig: boolean;
  showSubsidiaries: boolean;
}) {
  const [subsidiaries, setSubsidiaries] = useState<Subsidiary[]>([]);
  const isAdmin = identity?.role === "admin";

  // Only admins get the selector, so only admins need the catalog.
  useEffect(() => {
    if (!isAdmin) return;
    listSubsidiaries().then(setSubsidiaries).catch(() => setSubsidiaries([]));
  }, [isAdmin]);

  const tabs: { id: Tab; label: string }[] = [
    { id: "home", label: t(lang, "nav_offers") },
    { id: "offers", label: t(lang, "nav_new_offer") },
    { id: "customers", label: t(lang, "nav_customers") },
    { id: "import", label: t(lang, "nav_import") },
    { id: "dashboard", label: t(lang, "nav_dashboard") },
  ];
  if (showConfig) tabs.push({ id: "config", label: t(lang, "nav_config") });
  if (showSubsidiaries) tabs.push({ id: "subsidiaries", label: t(lang, "nav_subsidiaries") });

  return (
    <header className="bg-white shadow">
      <div className="flex items-center gap-4 px-4 py-2">
        <img src="/guardian-logo.png" alt="Guardian" className="h-9 w-auto" />
        <span className="text-sm font-semibold text-gray-700">Guardian HQ</span>
        <input
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            if (e.target.value) setTab("customers");
          }}
          placeholder="Search..."
          className="border rounded-full px-4 py-1.5 text-sm w-full max-w-xl mx-auto"
        />
        <div className="flex items-center gap-1.5 whitespace-nowrap">
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
        <select value={lang} onChange={(e) => setLang(e.target.value as Lang)} className="border rounded px-2 py-1 text-sm" title="Language">
          {LANGS.map((l) => (
            <option key={l.code} value={l.code}>
              {l.label}
            </option>
          ))}
        </select>
        {identity && (
          <span className="text-xs text-gray-600 whitespace-nowrap">
            {identity.external_id} · {identity.role} ·{" "}
            {identity.scope_subsidiary_short ?? identity.scope_subsidiary_id ?? "global"}
          </span>
        )}
      </div>
      <nav className="flex gap-1 px-4 border-t overflow-x-auto">
        {tabs.map((item) => (
          <button
            key={item.id}
            onClick={() => setTab(item.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px whitespace-nowrap ${
              tab === item.id
                ? "border-weber-blue text-weber-blue"
                : "border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300"
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>
    </header>
  );
}
