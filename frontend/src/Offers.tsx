import { useEffect, useMemo, useState } from "react";
import { listAllCustomers, listAllOffers, type Customer, type OfferListItem } from "./api";
import SectionCard from "./components/SectionCard";
import { t, type Lang } from "./i18n";

// Home offers screen: table over the whole scope with a prominent create
// button. Creating itself still happens in OfferBuilder (onNew prop).
export default function OffersHome({ lang, onNew }: { lang: Lang; onNew: () => void }) {
  const [offers, setOffers] = useState<OfferListItem[]>([]);
  const [names, setNames] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listAllCustomers()
      .then((cs: Customer[]) =>
        setNames(Object.fromEntries(cs.map((c) => [c.customer_id, c.account_name])))
      )
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    listAllOffers()
      .then((rows) => setOffers(rows))
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  const byStatus = useMemo(() => {
    const m: Record<string, number> = {};
    for (const o of offers) m[o.status || "Draft"] = (m[o.status || "Draft"] ?? 0) + 1;
    return m;
  }, [offers]);

  const eur = (v: string | number | null | undefined) =>
    `${Number(v ?? 0).toLocaleString("en-GB", { minimumFractionDigits: 2 })} €`;

  return (
    <div className="p-4 space-y-3 w-full">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">{t(lang, "home_list")}</h1>
        <button
          onClick={onNew}
          className="px-6 py-2.5 rounded-lg text-base font-bold bg-weber-blue text-white shadow hover:opacity-90"
        >
          + {t(lang, "home_new")}
        </button>
      </div>

      {error && <p className="text-sm text-red-600 bg-white rounded-lg shadow p-3">{error}</p>}

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {Object.entries(byStatus).map(([s, n]) => (
          <SectionCard key={s} title={s}>
            <p className="text-3xl font-bold text-gray-900">{n}</p>
          </SectionCard>
        ))}
        {offers.length === 0 && !loading && (
          <p className="text-sm text-gray-500 col-span-4">{t(lang, "home_empty")}</p>
        )}
      </div>

      <SectionCard title={`${t(lang, "home_list")} (${offers.length})`}>
        {loading ? (
          <p className="text-sm text-gray-500">{t(lang, "dash_loading")}</p>
        ) : (
          <div className="overflow-auto max-h-[calc(100vh-320px)] min-h-[300px]">
            <table className="w-full text-sm">
              <thead className="sticky top-0">
                <tr className="bg-weber-blue text-white text-left">
                  <th className="px-3 py-2 font-semibold">{t(lang, "home_col_number")}</th>
                  <th className="px-3 py-2 font-semibold">{t(lang, "home_col_customer")}</th>
                  <th className="px-3 py-2 font-semibold">{t(lang, "home_col_status")}</th>
                  <th className="px-3 py-2 text-right font-semibold">{t(lang, "home_col_total")}</th>
                </tr>
              </thead>
              <tbody>
                {offers.map((o, i) => (
                  <tr key={o.id} className={`border-b last:border-0 ${i % 2 ? "bg-gray-50" : "bg-white"} hover:bg-blue-50`}>
                    <td className="px-3 py-1.5 font-mono font-semibold text-weber-blue">{o.id_guardian_offer}</td>
                    <td className="px-3 py-1.5">{names[o.customer_id] ?? o.customer_id}</td>
                    <td className="px-3 py-1.5">
                      <span className="px-1.5 py-0.5 rounded text-xs bg-gray-100 text-gray-700">{o.status || "Draft"}</span>
                    </td>
                    <td className="px-3 py-1.5 text-right font-mono font-bold">{eur(o.total_end)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>
    </div>
  );
}
