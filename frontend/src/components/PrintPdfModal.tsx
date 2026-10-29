import { useCallback, useEffect, useRef, useState } from "react";
import Modal from "./Modal";
import {
  downloadOfferPdf,
  fetchOfferPdf,
  getOffer,
  patchOfferDocumentSettings,
  uploadOfferAnnex,
  type CustomAnnex,
} from "../api";
import { LANGS, t, type Lang } from "../i18n";

// The database holds legacy language names ("Spanish") from before the modal
// existed; the selector works with canonical codes. Anything unknown falls
// back to Spanish, matching the backend's own document fallback.
function langCodeOf(raw: string | null | undefined): Lang {
  const value = (raw ?? "").trim().toLowerCase();
  if (LANGS.some((l) => l.code === value)) return value as Lang;
  const legacy: Record<string, Lang> = {
    spanish: "es",
    "español": "es",
    english: "en",
    german: "de",
    deutsch: "de",
    portuguese: "pt",
    "português": "pt",
    italian: "it",
    italiano: "it",
  };
  return legacy[value] ?? "es";
}

const inputClass =
  "h-8 w-full rounded-lg border border-line-strong bg-white px-2 text-xs text-ink outline-none transition focus:border-primary focus:ring-[3px] focus:ring-focus/70";
const softBtn =
  "inline-flex h-8 items-center rounded-lg border border-line-strong bg-white px-2.5 text-xs font-medium text-ink transition hover:bg-canvas disabled:cursor-not-allowed disabled:opacity-40";
const primaryBtn =
  "inline-flex h-8 items-center rounded-lg border border-primary bg-primary px-3 text-xs font-medium text-white transition hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-40";

// Print settings dialog: contract language and custom annexes on the left,
// live PDF preview on the right. Scope (Guardian modules) is edited only in
// the OfferBuilder rail. Text annexes are added by attaching a Word file:
// the backend parses it and stores sanitized HTML (paragraphs + tables).
// Title changes auto-save through PATCH and re-render the preview.
export default function PrintPdfModal({
  open,
  offerId,
  lang,
  onClose,
}: {
  open: boolean;
  offerId: string;
  lang: Lang;
  onClose: () => void;
}) {
  const [language, setLanguage] = useState<Lang>("es");
  const [annexes, setAnnexes] = useState<CustomAnnex[]>([]);
  const [loaded, setLoaded] = useState(false);
  // Bumps on every user change: the debounce effect saves only when dirty.
  const [dirty, setDirty] = useState(0);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [rendering, setRendering] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  // Monotonic id: a slow response of an outdated edit never overwrites a
  // newer one when the user toggles quickly.
  const sequence = useRef(0);
  const previewUrlRef = useRef<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  // Mirror of the dirty counter, readable inside saveAndPreview without
  // adding it to the callback dependencies.
  const dirtyRef = useRef(0);

  const annexesValid = annexes.every((annex) => annex.title.trim() !== "");

  const saveAndPreview = useCallback(
    async (next: { language: Lang; annexes: CustomAnnex[] }) => {
      const id = ++sequence.current;
      const dirtyAtStart = dirtyRef.current;
      setSaving(true);
      setError(null);
      try {
        await patchOfferDocumentSettings(offerId, {
          language: next.language,
          custom_annexes: next.annexes,
        });
        if (id !== sequence.current) return;
        setRendering(true);
        const blob = await fetchOfferPdf(offerId);
        if (id !== sequence.current) return;
        const url = URL.createObjectURL(blob);
        if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
        previewUrlRef.current = url;
        setPreviewUrl(url);
        // Mark the form clean only if nothing changed while this save ran:
        // a newer edit keeps the dirty flag so its own debounce still fires.
        if (dirtyRef.current === dirtyAtStart) {
          dirtyRef.current = 0;
          setDirty(0);
        }
      } catch (e) {
        if (id !== sequence.current) return;
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (id === sequence.current) {
          setSaving(false);
          setRendering(false);
        }
      }
    },
    [offerId],
  );

  // Load the stored settings each time the modal opens and preview at once.
  // saveAndPreview is read on purpose only here: a change inside the modal
  // must not reload the form over the user's edits.
  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    setLoaded(false);
    setError(null);
    setPreviewUrl(null);
    getOffer(offerId)
      .then((offer) => {
        if (cancelled) return;
        const nextLanguage = langCodeOf(offer.language);
        const nextAnnexes = offer.custom_annexes ?? [];
        setLanguage(nextLanguage);
        setAnnexes(nextAnnexes);
        setLoaded(true);
        void saveAndPreview({ language: nextLanguage, annexes: nextAnnexes });
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, offerId]);

  // Auto-save (debounced) after each change once the form is loaded.
  useEffect(() => {
    if (!loaded || dirty === 0 || !annexesValid) return;
    const timer = setTimeout(() => {
      void saveAndPreview({ language, annexes });
    }, 500);
    return () => clearTimeout(timer);
  }, [dirty, loaded, annexesValid, language, annexes, saveAndPreview]);

  // Release the last blob URL when the modal unmounts.
  useEffect(
    () => () => {
      if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    },
    [],
  );

  function markDirty() {
    dirtyRef.current += 1;
    setDirty(dirtyRef.current);
  }

  function updateAnnex(index: number, patch: Partial<CustomAnnex>) {
    setAnnexes((current) =>
      current.map((annex, i) => (i === index ? { ...annex, ...patch } : annex)),
    );
    markDirty();
  }

  async function handleUpload(file: File) {
    const id = ++sequence.current;
    setUploading(true);
    setError(null);
    try {
      // The backend appends the parsed annex and returns the full offer;
      // the local list is replaced by the server list so unsaved edits and
      // the upload cannot diverge.
      const offer = await uploadOfferAnnex(offerId, file);
      if (id !== sequence.current) return;
      const nextAnnexes = offer.custom_annexes ?? [];
      setAnnexes(nextAnnexes);
      setRendering(true);
      const blob = await fetchOfferPdf(offerId);
      if (id !== sequence.current) return;
      const url = URL.createObjectURL(blob);
      if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
      previewUrlRef.current = url;
      setPreviewUrl(url);
    } catch (e) {
      if (id !== sequence.current) return;
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      if (id === sequence.current) {
        setUploading(false);
        setRendering(false);
      }
    }
  }

  if (!open) return null;

  return (
    <Modal
      title={t(lang, "mp_title")}
      onClose={onClose}
      widthClass="w-[96vw] max-w-[96vw]"
      bodyClass="p-4 h-[88vh] flex flex-col"
    >
      <div className="grid min-h-0 flex-1 grid-cols-1 gap-4 md:grid-cols-[18rem_1fr]">
        <div className="min-h-0 space-y-3 overflow-y-auto pr-1">
          <div>
            <label className="mb-1 block text-[11px] font-semibold text-slate-700" htmlFor="print-language">
              {t(lang, "mp_language")}
            </label>
            <select
              id="print-language"
              value={language}
              onChange={(e) => {
                const value = e.target.value as Lang;
                setLanguage(value);
                // A discrete choice, not typing: save it now instead of
                // waiting for the annex-edit debounce, so a quick Download
                // cannot fetch the previous language's PDF.
                void saveAndPreview({ language: value, annexes });
              }}
              className={inputClass}
            >
              {LANGS.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <div className="mb-1 flex items-center justify-between">
              <span className="text-[11px] font-semibold text-slate-700">{t(lang, "mp_annexes")}</span>
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading || annexes.length >= 10}
                className={softBtn}
              >
                {uploading ? t(lang, "mp_annex_uploading") : t(lang, "mp_annex_upload")}
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  // Reset so the same file can be attached again later.
                  e.target.value = "";
                  if (file) void handleUpload(file);
                }}
              />
            </div>
            {annexes.length === 0 && (
              <p className="text-[10px] leading-snug text-slate-500">{t(lang, "mp_annex_empty")}</p>
            )}
            {annexes.map((annex, index) => (
              <div key={index} className="mb-2 rounded border border-slate-200 p-2">
                <div className="flex items-center gap-1">
                  <input
                    value={annex.title}
                    onChange={(e) => updateAnnex(index, { title: e.target.value })}
                    placeholder={t(lang, "mp_annex_title_ph")}
                    maxLength={200}
                    className={inputClass}
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setAnnexes((current) => current.filter((_, i) => i !== index));
                      markDirty();
                    }}
                    title={t(lang, "mp_annex_remove")}
                    aria-label={t(lang, "mp_annex_remove")}
                    className="h-7 shrink-0 rounded border border-slate-300 px-2 text-xs text-slate-500 hover:bg-slate-50"
                  >
                    ×
                  </button>
                </div>
              </div>
            ))}
            {!annexesValid && <p className="text-[10px] text-amber-700">{t(lang, "mp_annex_hint")}</p>}
          </div>
        </div>

        <div className="flex min-h-0 flex-col">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-[11px] font-semibold text-slate-700">{t(lang, "mp_preview")}</span>
            {(saving || rendering || uploading) && (
              <span className="animate-pulse text-[10px] text-slate-500">
                {uploading
                  ? t(lang, "mp_annex_uploading")
                  : saving
                    ? t(lang, "mp_saving")
                    : t(lang, "mp_preview_updating")}
              </span>
            )}
          </div>
          {previewUrl ? (
            <iframe
              src={previewUrl}
              title={t(lang, "mp_preview")}
              className="min-h-0 w-full flex-1 rounded border border-slate-300 bg-slate-50"
            />
          ) : (
            <div className="flex min-h-0 flex-1 items-center justify-center rounded border border-slate-200 bg-slate-50 text-[11px] text-slate-400">
              {error ? t(lang, "mp_preview_error") : t(lang, "mp_preview_updating")}
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-2 rounded border border-red-200 bg-red-50 px-2 py-1 text-[11px] text-red-700">{error}</div>
      )}

      <div className="mt-3 flex shrink-0 justify-end gap-2">
        <button
          type="button"
          onClick={() => void downloadOfferPdf(offerId)}
          disabled={saving || rendering || uploading || dirty > 0 || !previewUrl}
          className={primaryBtn}
        >
          {t(lang, "mp_download")}
        </button>
        <button type="button" onClick={onClose} className={softBtn}>
          {t(lang, "mp_close")}
        </button>
      </div>
    </Modal>
  );
}
