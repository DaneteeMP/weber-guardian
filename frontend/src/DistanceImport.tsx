import { useState } from "react";
import { importDistanceRoutes, type DistanceImportReport } from "./api";
import SectionCard from "./components/SectionCard";
import type { Lang } from "./i18n";

const STR = {
  es: {
    title: "Importar rutas CSV",
    help: "Cabecera de tabla reconocida automáticamente. Simula antes de importar; las rutas omitidas no se borran.",
    file: "Elegir CSV",
    origin: "Origen",
    date: "Fecha de los datos",
    simulate: "Simular",
    import: "Importar rutas",
    noFile: "Elige un CSV primero.",
    simulateFirst: "Ejecuta una simulación válida antes de importar.",
    rows: "filas",
    created: "nuevas",
    updated: "actualizadas",
    errors: "errores",
  },
  en: {
    title: "Import route CSV",
    help: "The table header is detected automatically. Preview before importing; omitted routes are not deleted.",
    file: "Choose CSV",
    origin: "Origin",
    date: "Data date",
    simulate: "Preview",
    import: "Import routes",
    noFile: "Choose a CSV file first.",
    simulateFirst: "Run a clean preview before importing.",
    rows: "rows",
    created: "new",
    updated: "updated",
    errors: "errors",
  },
  de: {
    title: "Routen-CSV importieren",
    help: "Die Tabellenüberschrift wird automatisch erkannt. Vor dem Import simulieren; ausgelassene Routen werden nicht gelöscht.",
    file: "CSV auswählen",
    origin: "Ursprung",
    date: "Datenstand",
    simulate: "Simulieren",
    import: "Routen importieren",
    noFile: "Bitte zuerst eine CSV-Datei auswählen.",
    simulateFirst: "Vor dem Import eine fehlerfreie Simulation ausführen.",
    rows: "Zeilen",
    created: "neu",
    updated: "aktualisiert",
    errors: "Fehler",
  },
  pt: {
    title: "Importar rotas CSV",
    help: "O cabeçalho é detetado automaticamente. Simule antes de importar; as rotas omitidas não são eliminadas.",
    file: "Escolher CSV",
    origin: "Origem",
    date: "Data dos dados",
    simulate: "Simular",
    import: "Importar rotas",
    noFile: "Escolha primeiro um ficheiro CSV.",
    simulateFirst: "Execute uma simulação sem erros antes de importar.",
    rows: "linhas",
    created: "novas",
    updated: "atualizadas",
    errors: "erros",
  },
  it: {
    title: "Importa rotte CSV",
    help: "L'intestazione viene rilevata automaticamente. Esegui un'anteprima prima dell'importazione; le rotte omesse non vengono eliminate.",
    file: "Scegli CSV",
    origin: "Origine",
    date: "Data dei dati",
    simulate: "Anteprima",
    import: "Importa rotte",
    noFile: "Scegli prima un file CSV.",
    simulateFirst: "Esegui un'anteprima senza errori prima di importare.",
    rows: "righe",
    created: "nuove",
    updated: "aggiornate",
    errors: "errori",
  },
} as const;

const ROUTE_ORIGIN = "39044 Egna / Neumarkt (Bolzano)";

export default function DistanceImport({
  lang,
  subsidiaryId,
  onImported,
}: {
  lang: Lang;
  subsidiaryId: string;
  onImported: () => Promise<void>;
}) {
  const text = STR[lang];
  const [file, setFile] = useState<File | null>(null);
  const [origin, setOrigin] = useState(ROUTE_ORIGIN);
  const [routeDate, setRouteDate] = useState("2026-10-01");
  const [report, setReport] = useState<DistanceImportReport | null>(null);
  const [previewed, setPreviewed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function run(dryRun: boolean) {
    setError(null);
    if (!file) {
      setError(text.noFile);
      return;
    }
    if (!dryRun && !previewed) {
      setError(text.simulateFirst);
      return;
    }
    setBusy(true);
    try {
      const result = await importDistanceRoutes(file, subsidiaryId, origin, routeDate, dryRun);
      setReport(result);
      setPreviewed(dryRun && result.errors.length === 0);
      if (!dryRun && result.errors.length === 0) await onImported();
    } catch (e) {
      setError(String(e));
      setPreviewed(false);
    } finally {
      setBusy(false);
    }
  }

  function invalidatePreview() {
    setPreviewed(false);
    setReport(null);
  }

  return (
    <SectionCard title={text.title}>
      <p className="mb-3 text-sm text-gray-600">{text.help}</p>
      <div className="grid gap-2 sm:grid-cols-2">
        <label className="block text-xs">
          {text.origin}
          <input
            value={origin}
            onChange={(event) => {
              setOrigin(event.target.value);
              invalidatePreview();
            }}
            className="mt-1 w-full rounded border px-2 py-1.5 text-sm"
          />
        </label>
        <label className="block text-xs">
          {text.date}
          <input
            type="date"
            value={routeDate}
            onChange={(event) => {
              setRouteDate(event.target.value);
              invalidatePreview();
            }}
            className="mt-1 w-full rounded border px-2 py-1.5 text-sm"
          />
        </label>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <label className="cursor-pointer rounded border bg-white px-3 py-1.5 text-sm">
          {text.file}
          <input
            type="file"
            accept=".csv,text/csv"
            className="hidden"
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null);
              invalidatePreview();
            }}
          />
        </label>
        <span className="text-sm text-gray-600">{file?.name ?? ""}</span>
        <button disabled={busy} onClick={() => void run(true)} className="rounded bg-gray-200 px-3 py-1.5 text-sm disabled:opacity-50">
          {busy ? "…" : text.simulate}
        </button>
        <button
          disabled={busy || !previewed}
          onClick={() => void run(false)}
          className="rounded bg-weber-blue px-3 py-1.5 text-sm text-white disabled:opacity-40"
        >
          {text.import}
        </button>
      </div>
      {error && <p className="mt-2 rounded bg-red-50 p-2 text-sm text-red-700">{error}</p>}
      {report && (
        <div className="mt-3 rounded border bg-gray-50 p-3 text-sm">
          <p>{report.total_rows} {text.rows} · {report.created} {text.created} · {report.updated} {text.updated} · {report.errors.length} {text.errors}</p>
          {report.errors.length > 0 && (
            <ul className="mt-2 max-h-48 space-y-1 overflow-y-auto text-xs text-red-700">
              {report.errors.map((rowError, index) => (
                <li key={`${rowError.line}:${index}`}>L{rowError.line}: {rowError.reason}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </SectionCard>
  );
}
