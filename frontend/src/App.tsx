import { useState } from "react";
import Customers from "./Customers";
import OfferBuilder from "./OfferBuilder";

// F1 shell: two tabs, no router library (F2 will add auth-aware routing).
export default function App() {
  const [tab, setTab] = useState<"customers" | "offers">("offers");
  const btn = (active: boolean) =>
    `px-3 py-1 rounded text-sm font-medium ${active ? "bg-weber-blue text-white" : "bg-gray-200 text-gray-700 hover:bg-gray-300"}`;

  return (
    <div>
      <nav className="bg-white shadow px-4 py-2 flex gap-2">
        <button onClick={() => setTab("offers")} className={btn(tab === "offers")}>
          Guardian offers
        </button>
        <button onClick={() => setTab("customers")} className={btn(tab === "customers")}>
          Customers
        </button>
      </nav>
      {tab === "offers" ? <OfferBuilder /> : <Customers />}
    </div>
  );
}
