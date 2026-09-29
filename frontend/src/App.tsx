import { useEffect, useState } from "react";
import Config from "./Config";
import Customers from "./Customers";
import Dashboard from "./Dashboard";
import ImportData from "./ImportData";
import OfferBuilder from "./OfferBuilder";
import Offers from "./Offers";
import Subsidiaries from "./Subsidiaries";
import Gate from "./components/Gate";
import TopBar, { type Tab } from "./components/TopBar";
import {
  getDevUser,
  hasGateCredentials,
  me,
  onGateRequired,
  probeGate,
  setDevUser,
  type Me,
} from "./api";
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
  const [gateBlocked, setGateBlocked] = useState(false);
  const [gateChecked, setGateChecked] = useState(false);
  const [epoch, setEpoch] = useState(0);

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

  // Decide once, before painting the app, whether the shared password is
  // needed. Any later Basic challenge from api.ts also opens the gate.
  useEffect(() => {
    onGateRequired(() => setGateBlocked(true));
    if (hasGateCredentials()) {
      setGateChecked(true);
      return;
    }
    probeGate()
      .then((ok) => setGateBlocked(!ok))
      .finally(() => setGateChecked(true));
  }, []);

  useEffect(() => {
    if (!dev) {
      setIdentity(null);
      return;
    }
    me().then(setIdentity).catch(() => setIdentity(null));
  }, [dev, tab, epoch]);

  function setDev(v: string | null) {
    setDevUser(v);
    setDevState(v);
  }

  function passGate() {
    setGateBlocked(false);
    setEpoch((n) => n + 1);
  }

  if (!gateChecked) {
    return <div className="min-h-screen bg-gray-100" />;
  }

  if (gateBlocked) {
    return <Gate lang={lang} onPass={passGate} />;
  }

  const contentKey = `${dev ?? "anon"}:${epoch}`;

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
        <Offers key={contentKey} lang={lang} onNew={openNewOffer} onEdit={openOffer} />
      ) : tab === "offers" ? (
        <OfferBuilder
          key={`${contentKey}:${editingOffer ?? "new"}`}
          lang={lang}
          editingOfferId={editingOffer}
          onDone={() => setTab("home")}
        />
      ) : tab === "import" ? (
        <ImportData key={contentKey} lang={lang} />
      ) : tab === "dashboard" ? (
        <Dashboard key={contentKey} lang={lang} />
      ) : tab === "config" ? (
        <Config key={contentKey} lang={lang} isAdmin={identity?.role === "admin"} />
      ) : tab === "subsidiaries" ? (
        <Subsidiaries key={contentKey} lang={lang} isAdmin={identity?.role === "admin"} />
      ) : (
        <Customers key={contentKey} lang={lang} externalSearch={search} />
      )}
    </div>
  );
}
