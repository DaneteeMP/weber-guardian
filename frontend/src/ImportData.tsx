import { useEffect, useState } from "react";
import { listSubsidiaries, uploadCsv, type ImportReport, type Subsidiary } from "./api";
import Button from "./components/Button";
import SectionCard from "./components/SectionCard";
import { t, type Lang } from "./i18n";

// CSV upload with dry-run report. The backend validates everything;
// this page only sends the file and renders the returned report.
const STR = {
  es: { title: "Importar desde SAP", subtitle: "CSV separado por «;»", drop: "Arrastra el CSV aquí", required: "Columnas requeridas", pick: "Elegir archivo", subsidiary: "Filial (opcional)", simulate: "Simular", import: "Importar", rows: "filas", created: "creados", skipped: "omitidos", errors: "errores", customers: "Clientes", sites: "Ubicaciones", equipment: "Equipos", updated: "actualizados", need: "Elige un fichero primero" },
  en: { title: "Import from SAP", subtitle: "CSV separated by «;»", drop: "Drag the CSV here", required: "Required columns", pick: "Choose file", subsidiary: "Subsidiary (optional)", simulate: "Simulate", import: "Import", rows: "rows", created: "created", skipped: "skipped", errors: "errors", customers: "Customers", sites: "Sites", equipment: "Equipment", updated: "updated", need: "Pick a file first" },
  de: { title: "Aus SAP importieren", subtitle: "CSV mit «;» getrennt", drop: "CSV hierher ziehen", required: "Erforderliche Spalten", pick: "Datei wählen", subsidiary: "Filiale (optional)", simulate: "Simulieren", import: "Importieren", rows: "Zeilen", created: "angelegt", skipped: "übersprungen", errors: "Fehler", customers: "Kunden", sites: "Standorte", equipment: "Anlagen", updated: "aktualisiert", need: "Bitte zuerst eine Datei wählen" },
  pt: { title: "Importar do SAP", subtitle: "CSV separado por «;»", drop: "Arraste o CSV aqui", required: "Colunas necessárias", pick: "Escolher ficheiro", subsidiary: "Filial (opcional)", simulate: "Simular", import: "Importar", rows: "linhas", created: "criados", skipped: "omitidos", errors: "erros", customers: "Clientes", sites: "Locais", equipment: "Equipamentos", updated: "atualizados", need: "Escolhe um ficheiro primeiro" },
  it: { title: "Importa da SAP", subtitle: "CSV separato da «;»", drop: "Trascina qui il CSV", required: "Colonne richieste", pick: "Scegli file", subsidiary: "Filiale (facoltativa)", simulate: "Simula", import: "Importa", rows: "righe", created: "creati", skipped: "saltati", errors: "errori", customers: "Clienti", sites: "Sedi", equipment: "Impianti", updated: "aggiornati", need: "Scegli prima un file" },
} as const;

export default function ImportData({ lang, scope }: { lang: Lang; scope?: string | null }) {
  const s = STR[lang];
  const [file, setFile] = useState<File | null>(null);
  const [subsidiary, setSubsidiary] = useState(scope ?? "");
  const [subsidiaries, setSubsidiaries] = useState<Subsidiary[]>([]);
  const [report, setReport] = useState<ImportReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const requiredColumns = t(lang, "cfg_import_columns")
    .split("·")
    .map((column) => column.trim())
    .filter(Boolean);

  useEffect(() => {
    if (scope) return;
    listSubsidiaries().then(setSubsidiaries).catch(() => {});
  }, [scope]);

  async function run(dryRun: boolean) {
    setError(null);
    setReport(null);
    if (!file) {
      setError(s.need);
      return;
    }
    setBusy(true);
    try {
      setReport(await uploadCsv(file, dryRun, (scope ?? subsidiary) || undefined));
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
    <>
      <SectionCard title={s.title} subtitle={s.subtitle}>
        <div className="ui-dropzone">
          <p className="text-sm font-semibold text-ink">{s.drop}</p>
          <label className="mt-2.5 inline-flex h-9 cursor-pointer items-center justify-center rounded-lg border border-line-strong bg-white px-3.5 text-sm font-medium text-ink transition hover:bg-canvas">
            {s.pick}
            <input type="file" accept=".csv" className="hidden" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          </label>
          {file && <p className="mt-2 truncate text-xs text-muted">{file.name}</p>}
        </div>
        {!scope && (
          <select value={subsidiary} onChange={(e) => setSubsidiary(e.target.value)} className="ui-input mt-3 w-full" title={s.subsidiary}>
            <option value="">{s.subsidiary}</option>
            {subsidiaries.map((f) => (
              <option key={f.name} value={f.name}>
                {f.short_label}
              </option>
            ))}
          </select>
        )}
        <div className="mt-3 flex justify-end gap-2">
          <Button size="sm" variant="secondary" disabled={busy} onClick={() => run(true)}>
            {s.simulate}
          </Button>
          <Button size="sm" disabled={busy} onClick={() => run(false)}>
            {s.import}
          </Button>
        </div>
        <details className="mt-3 text-xs">
          <summary className="cursor-pointer font-medium text-primary">{s.required} ({requiredColumns.length})</summary>
          <p className="mt-2 text-xs text-muted">{t(lang, "cfg_import_hint")}</p>
          <div className="ui-cols mt-2.5">
            {requiredColumns.map((column) => (
              <span key={column}>{column}</span>
            ))}
          </div>
        </details>
      </SectionCard>

      {error && <p className="rounded-lg border border-red-200 bg-white p-3 text-sm text-red-600">{error}</p>}

      {report && (
        <SectionCard title={report.dry_run ? s.simulate : s.import}>
          <p className="text-sm">
            {report.total_rows} {s.rows} · {report.customers_created + report.sites_created + report.equipment_created} {s.created} ·{" "}
            {report.customers_skipped + report.sites_skipped + report.equipment_skipped} {s.skipped} · {report.errors.length} {s.errors}
          </p>
          <p className="text-xs text-muted">
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
    </>
  );
}
