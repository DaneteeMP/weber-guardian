import { useEffect, useState } from "react";
import Config from "./Config";
import Customers from "./Customers";
import Dashboard from "./Dashboard";
import ImportData from "./ImportData";
import OfferBuilder from "./OfferBuilder";
import Offers from "./Offers";
import Subsidiaries from "./Subsidiaries";
import TopBar, { type Tab } from "./components/TopBar";
import { getDevUser, me, setDevUser, type Me } from "./api";
import type { Lang } from "./i18n";

// Shell: TopBar (brand, search, tabs, identity). No router lib, no i18n lib.
// The dev-user dropdown is local-only; behind SharePoint/Entra it goes away.
export default function App() {
  const [tab, setTab] = useState<Tab>("home");
  const [lang, setLang] = useState<Lang>(() => (localStorage.getItem("lang") as Lang) || "es");
  const [dev, setDevState] = useState<string | null>(() => getDevUser());
  const [identity, setIdentity] = useState<Me | null>(null);
  const [search, setSearch] = useState("");
  const [editingOffer, setEditingOffer] = useState<string | null>(null);

  function openNewOffer() {
    setEditingOffer(null);
    setTab("offers");
  }

  function openOffer(offerId: string) {
    setEditingOffer(offerId);
    setTab("offers");
  }

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

  function setDev(v: string | null) {
    setDevUser(v);
    setDevState(v);
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <TopBar
        tab={tab}
        setTab={setTab}
        lang={lang}
        setLang={setLang}
        search={search}
        setSearch={setSearch}
        dev={dev}
        setDev={setDev}
        identity={identity}
        showConfig={identity?.role === "admin"}
        showSubsidiaries={identity?.role === "admin"}
      />
      {tab === "home" ? (
        <Offers key={dev ?? "anon"} lang={lang} onNew={openNewOffer} onEdit={openOffer} />
      ) : tab === "offers" ? (
        <OfferBuilder
          key={`${dev ?? "anon"}:${editingOffer ?? "new"}`}
          lang={lang}
          editingOfferId={editingOffer}
          onDone={() => setTab("home")}
        />
      ) : tab === "import" ? (
        <ImportData key={dev ?? "anon"} lang={lang} />
      ) : tab === "dashboard" ? (
        <Dashboard key={dev ?? "anon"} lang={lang} />
      ) : tab === "config" ? (
        <Config key={dev ?? "anon"} lang={lang} isAdmin={identity?.role === "admin"} />
      ) : tab === "subsidiaries" ? (
        <Subsidiaries key={dev ?? "anon"} lang={lang} isAdmin={identity?.role === "admin"} />
      ) : (
        <Customers key={dev ?? "anon"} lang={lang} externalSearch={search} />
      )}
    </div>
  );
}
