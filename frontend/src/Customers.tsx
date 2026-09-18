import { useEffect, useState } from "react";

// Mirrors backend CustomerOut (app/modules/customers/schemas.py).
// No business rules here: the backend owns validation (422) and duplicates (409).
type Customer = {
  id: string;
  customer_id: string;
  account_name: string;
  city: string | null;
  province: string | null;
  country: string | null;
  created_at: string;
};

const API_URL = "http://localhost:8000/api/v1/customers";

export default function Customers() {
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
      const res = await fetch(API_URL);
      if (!res.ok) throw new Error(`GET failed: ${res.status}`);
      setRows(await res.json());
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
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
      <h1>Customers (F0)</h1>

      <form onSubmit={handleSubmit} style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input
          placeholder="SAP Debitor ID (customer_id)"
          value={customerId}
          onChange={(e) => setCustomerId(e.target.value)}
        />
        <input
          placeholder="Account Name"
          value={accountName}
          onChange={(e) => setAccountName(e.target.value)}
        />
        <input
          placeholder="Country (optional)"
          value={country}
          onChange={(e) => setCountry(e.target.value)}
        />
        <button type="submit">Create</button>
      </form>

      {loading && <p>Loading…</p>}
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
