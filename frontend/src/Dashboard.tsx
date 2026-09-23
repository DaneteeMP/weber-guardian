import { useEffect, useState } from "react";
import { getDashboard, type Dashboard as Stats } from "./api";
import SectionCard from "./components/SectionCard";
import { t, type Lang } from "./i18n";

// System overview. Counts arrive scoped from the backend: a subsidiary
// user sees their numbers, never the global ones.
export default function Dashboard({ lang }: { lang: Lang }) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboard().then(setStats).catch((e) => setError(String(e)));
  }, []);

  if (error) return <p className="p-4 text-sm text-red-600">{error}</p>;
  if (!stats) return <p className="p-4 text-sm text-gray-500">{t(lang, "dash_loading")}</p>;

  const cards: [string, number][] = [
    [t(lang, "dash_customers"), stats.total_customers],
    [t(lang, "dash_equipment"), stats.total_equipment],
    [t(lang, "dash_offers"), stats.total_offers],
    [t(lang, "dash_lines"), stats.total_offer_lines],
  ];

  return (
    <div className="p-4 space-y-3 w-full">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t(lang, "nav_dashboard")}</h1>
        <p className="mt-1 text-sm text-gray-500">{t(lang, "dash_subtitle")}</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map(([label, value]) => (
          <SectionCard key={label} title={label}>
            <p className="text-3xl font-bold text-gray-900">{value.toLocaleString()}</p>
          </SectionCard>
        ))}
      </div>
      <SectionCard title={t(lang, "dash_countries")}>
        <ul className="text-sm divide-y">
          {stats.countries.slice(0, 20).map((c) => (
            <li key={c.country} className="flex justify-between py-1">
              <span>{c.country}</span>
              <span className="font-mono">{c.count.toLocaleString()}</span>
            </li>
          ))}
        </ul>
      </SectionCard>
    </div>
  );
}
