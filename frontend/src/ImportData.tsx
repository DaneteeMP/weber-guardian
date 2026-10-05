import { useEffect, useState } from "react";
import { listSubsidiaries, uploadCsv, type ImportReport, type Subsidiary } from "./api";
import SectionCard from "./components/SectionCard";
import { t, type Lang } from "./i18n";

// CSV upload with dry-run report. The backend validates everything;
// this page only sends the file and renders the returned report.
const STR = {
  es: { title: "Importar CSV", pick: "Elegir fichero", subsidiary: "Filial (opcional)", simulate: "Simular", import: "Importar", rows: "filas", created: "creados", skipped: "omitidos", errors: "errores", customers: "Clientes", sites: "Ubicaciones", equipment: "Equipos", updated: "actualizados", need: "Elige un fichero primero" },
  en: { title: "Import CSV", pick: "Choose file", subsidiary: "Subsidiary (optional)", simulate: "Simulate", import: "Import", rows: "rows", created: "created", skipped: "skipped", errors: "errors", customers: "Customers", sites: "Sites", equipment: "Equipment", updated: "updated", need: "Pick a file first" },
  de: { title: "CSV importieren", pick: "Datei wählen", subsidiary: "Filiale (optional)", simulate: "Simulieren", import: "Importieren", rows: "Zeilen", created: "angelegt", skipped: "übersprungen", errors: "Fehler", customers: "Kunden", sites: "Standorte", equipment: "Anlagen", updated: "aktualisiert", need: "Bitte zuerst eine Datei wählen" },
  pt: { title: "Importar CSV", pick: "Escolher ficheiro", subsidiary: "Filial (opcional)", simulate: "Simular", import: "Importar", rows: "linhas", created: "criados", skipped: "omitidos", errors: "erros", customers: "Clientes", sites: "Locais", equipment: "Equipamentos", updated: "atualizados", need: "Escolhe um ficheiro primeiro" },
  it: { title: "Importa CSV", pick: "Scegli file", subsidiary: "Filiale (facoltativa)", simulate: "Simula", import: "Importa", rows: "righe", created: "creati", skipped: "saltati", errors: "errori", customers: "Clienti", sites: "Sedi", equipment: "Impianti", updated: "aggiornati", need: "Scegli prima un file" },
} as const;

export default function ImportData({ lang }: { lang: Lang }) {
  const s = STR[lang];
  const [file, setFile] = useState<File | null>(null);
  const [subsidiary, setSubsidiary] = useState("");
  const [subsidiaries, setSubsidiaries] = useState<Subsidiary[]>([]);
  const [report, setReport] = useState<ImportReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const input = "border rounded px-2 py-1 text-sm";

  useEffect(() => {
    listSubsidiaries().then(setSubsidiaries).catch(() => {});
  }, []);

  async function run(dryRun: boolean) {
    setError(null);
    setReport(null);
    if (!file) {
      setError(s.need);
      return;
    }
    setBusy(true);
    try {
      setReport(await uploadCsv(file, dryRun, subsidiary || undefined));
    } catch (e) {
      // 422 carries the report inside detail: surface row errors readably.
      const msg = e instanceof Error ? e.message : "Upload failed";
      setError(msg);
      const m = msg.match(/\{.*\}$/);
      if (m) {
        try {
          setReport(JSON.parse(m[0]));
        } catch {
          /* keep the raw message */
        }
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="p-4 space-y-3 max-w-3xl mx-auto">
      <SectionCard title={s.title}>
        <div className="flex gap-2 items-center flex-wrap">
          <label className={`${input} cursor-pointer bg-blue-50`}>
            {s.pick}
            <input type="file" accept=".csv" className="hidden" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          </label>
          <span className="text-sm text-gray-600">{file?.name ?? ""}</span>
          <select value={subsidiary} onChange={(e) => setSubsidiary(e.target.value)} className={input} title={s.subsidiary}>
            <option value="">{s.subsidiary}</option>
            {subsidiaries.map((f) => (
              <option key={f.name} value={f.name}>
                {f.short_label}
              </option>
            ))}
          </select>
          <button disabled={busy} onClick={() => run(true)} className="px-3 py-1 rounded text-sm bg-gray-200 hover:bg-gray-300 disabled:opacity-50">
            {s.simulate}
          </button>
          <button disabled={busy} onClick={() => run(false)} className="px-3 py-1 rounded text-sm bg-weber-blue text-white disabled:opacity-50">
            {s.import}
          </button>
        </div>
      </SectionCard>

      {error && <p className="text-sm text-red-600 bg-white rounded shadow p-2">{error}</p>}

      {report && (
        <SectionCard title={report.dry_run ? s.simulate : s.import}>
          <p className="text-sm">
            {report.total_rows} {s.rows} · {report.customers_created + report.sites_created + report.equipment_created} {s.created} ·{" "}
            {report.customers_skipped + report.sites_skipped + report.equipment_skipped} {s.skipped} · {report.errors.length} {s.errors}
          </p>
          <p className="text-xs text-gray-500">
            {s.customers} {report.customers_created}/{report.customers_skipped} · {s.sites} {report.sites_created}/{report.sites_skipped} · {s.equipment} {report.equipment_created}/{report.equipment_updated}/{report.equipment_skipped} ({s.created}/{s.updated}/{s.skipped})
          </p>
          {report.errors.length > 0 && (
            <ul className="mt-2 text-xs text-red-700 space-y-1">
              {report.errors.slice(0, 50).map((e, i) => (
                <li key={i}>
                  L{e.line}: {e.reason}
                </li>
              ))}
            </ul>
          )}
          {(report.warnings ?? []).length > 0 && (
            <ul className="mt-2 text-xs text-amber-700 space-y-1">
              {(report.warnings ?? []).slice(0, 50).map((w, i) => (
                <li key={i}>⚠ {w}</li>
              ))}
            </ul>
          )}
        </SectionCard>
      )}
    </div>
  );
}
