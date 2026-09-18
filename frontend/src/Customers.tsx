import { useEffect, useState } from "react";
import { getDevUser, listCustomers, type Customer } from "./api";
import { t, type Lang } from "./i18n";

const API_URL = "http://localhost:8000/api/v1/customers";

export default function Customers({ lang }: { lang: Lang }) {
  const [rows, setRows] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [customerId, setCustomerId] = useState("");
  const [accountName, setAccountName] = useState("");
  const [country, setCountry] = useState("");

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setRows(await listCustomers());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Load failed");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      const dev = getDevUser();
      if (dev) headers["X-Dev-User"] = dev;
      const res = await fetch(API_URL, {
        method: "POST",
        headers,
        body: JSON.stringify({
          customer_id: customerId,
          account_name: accountName,
          country: country || null,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => null);
        const detail =
          typeof data?.detail === "string"
            ? data.detail
            : JSON.stringify(data?.detail ?? res.statusText);
        throw new Error(`POST failed (${res.status}): ${detail}`);
      }
      setCustomerId("");
      setAccountName("");
      setCountry("");
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Create failed");
    }
  }

  return (
    <main style={{ maxWidth: 800, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>{t(lang, "cust_title")}</h1>

      <form onSubmit={handleSubmit} style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input
          placeholder={t(lang, "cust_id_ph")}
          value={customerId}
          onChange={(e) => setCustomerId(e.target.value)}
        />
        <input
          placeholder={t(lang, "cust_name_ph")}
          value={accountName}
          onChange={(e) => setAccountName(e.target.value)}
        />
        <input
          placeholder={t(lang, "cust_country_ph")}
          value={country}
          onChange={(e) => setCountry(e.target.value)}
        />
        <button type="submit">{t(lang, "cust_create")}</button>
      </form>

      {loading && <p>{t(lang, "cust_loading")}</p>}
      {error && <p style={{ color: "crimson" }}>{error}</p>}

      <table border={1} cellPadding={6} style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th>customer_id (SAP)</th>
            <th>account_name</th>
            <th>country</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((c) => (
            <tr key={c.id}>
              <td>{c.customer_id}</td>
              <td>{c.account_name}</td>
              <td>{c.country ?? ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
