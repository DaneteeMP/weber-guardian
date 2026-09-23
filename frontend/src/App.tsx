import { useEffect, useState } from "react";
import Customers from "./Customers";
import Dashboard from "./Dashboard";
import ImportData from "./ImportData";
import OfferBuilder from "./OfferBuilder";
import { getDevUser, me, setDevUser, type Me } from "./api";
import { LANGS, t, type Lang } from "./i18n";

const DEVS = ["dev-admin", "dev-es", "dev-de", "dev-viewer"];

// Shell: tabs (no router lib), language selector, dev identity + /me badge.
// The dev-user dropdown is local-only; behind SharePoint/Entra it goes away.
export default function App() {
  const [tab, setTab] = useState<"customers" | "offers" | "import" | "dashboard">("offers");
  const [lang, setLang] = useState<Lang>(() => (localStorage.getItem("lang") as Lang) || "es");
  const [dev, setDev] = useState<string | null>(() => getDevUser());
  const [identity, setIdentity] = useState<Me | null>(null);

  useEffect(() => {
    localStorage.setItem("lang", lang);
  }, [lang]);

  useEffect(() => {
    if (!dev) {
      setIdentity(null);
      return;
    }
    me().then(setIdentity).catch(() => setIdentity(null));
  }, [dev, tab]);

  const btn = (active: boolean) =>
    `px-3 py-1 rounded text-sm font-medium ${active ? "bg-weber-blue text-white" : "bg-gray-200 text-gray-700 hover:bg-gray-300"}`;

  return (
    <div>
      <nav className="bg-white shadow px-4 py-2 flex gap-2 items-center">
        <button onClick={() => setTab("offers")} className={btn(tab === "offers")}>
          {t(lang, "nav_offers")}
        </button>
        <button onClick={() => setTab("customers")} className={btn(tab === "customers")}>
          {t(lang, "nav_customers")}
        </button>
        <button onClick={() => setTab("import")} className={btn(tab === "import")}>
          {t(lang, "nav_import")}
        </button>
        <button onClick={() => setTab("dashboard")} className={btn(tab === "dashboard")}>
          {t(lang, "nav_dashboard")}
        </button>
        <span className="flex-1" />
        <select
          value={lang}
          onChange={(e) => setLang(e.target.value as Lang)}
          className="border rounded px-2 py-1 text-sm"
          title="Language"
        >
          {LANGS.map((l) => (
            <option key={l.code} value={l.code}>
              {l.label}
            </option>
          ))}
        </select>
        <select
          value={dev ?? ""}
          onChange={(e) => {
            const v = e.target.value || null;
            setDevUser(v);
            setDev(v);
          }}
          className="border rounded px-2 py-1 text-sm bg-yellow-50"
          title="Dev user (local only)"
        >
          <option value="">No identity</option>
          {DEVS.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
        {identity && (
          <span className="text-xs text-gray-600">
            {identity.external_id} · {identity.role}
            {identity.subsidiary_id ? ` · ${identity.subsidiary_id}` : " · global"}
          </span>
        )}
      </nav>
      {tab === "offers" ? (
        <OfferBuilder lang={lang} />
      ) : tab === "import" ? (
        <ImportData lang={lang} />
      ) : tab === "dashboard" ? (
        <Dashboard lang={lang} />
      ) : (
        <Customers lang={lang} />
      )}
    </div>
  );
}
