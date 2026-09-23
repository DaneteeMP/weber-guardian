import { LANGS, t, type Lang } from "../i18n";

export type Tab = "offers" | "customers" | "import" | "dashboard" | "config";

// Salesforce-style shell: brand row (logo, global search, identity) plus
// the tab bar. No routing library: tabs are plain state in App.
export default function TopBar({
  tab,
  setTab,
  lang,
  setLang,
  search,
  setSearch,
  dev,
  setDev,
  identity,
  showConfig,
}: {
  tab: Tab;
  setTab: (t: Tab) => void;
  lang: Lang;
  setLang: (l: Lang) => void;
  search: string;
  setSearch: (s: string) => void;
  dev: string | null;
  setDev: (d: string | null) => void;
  identity: { external_id: string; role: string; subsidiary_id: string | null } | null;
  showConfig: boolean;
}) {
  const tabs: { id: Tab; label: string }[] = [
    { id: "offers", label: t(lang, "nav_offers") },
    { id: "customers", label: t(lang, "nav_customers") },
    { id: "import", label: t(lang, "nav_import") },
    { id: "dashboard", label: t(lang, "nav_dashboard") },
  ];
  if (showConfig) tabs.push({ id: "config", label: t(lang, "nav_config") });

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
        <select value={lang} onChange={(e) => setLang(e.target.value as Lang)} className="border rounded px-2 py-1 text-sm" title="Language">
          {LANGS.map((l) => (
            <option key={l.code} value={l.code}>
              {l.label}
            </option>
          ))}
        </select>
        <select
          value={dev ?? ""}
          onChange={(e) => setDev(e.target.value || null)}
          className="border rounded px-2 py-1 text-sm bg-yellow-50"
          title="Dev user (local only)"
        >
          <option value="">No identity</option>
          {["dev-admin", "dev-es", "dev-de", "dev-viewer"].map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
        {identity && (
          <span className="text-xs text-gray-600 whitespace-nowrap">
            {identity.external_id} · {identity.role}
            {identity.subsidiary_id ? ` · ${identity.subsidiary_id}` : " · global"}
          </span>
        )}
      </div>
      <nav className="flex gap-1 px-4 border-t">
        {tabs.map((item) => (
          <button
            key={item.id}
            onClick={() => setTab(item.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px ${
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
