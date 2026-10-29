"""Page geometry and base typography for the offer PDF (WeasyPrint).

Single source of truth for @page rules (A4, margins, Weber wordmark on every
page via a running element, page counter) and for @font-face registration of
the bundled Noto Sans fonts (OFL, app/weber/fonts/).

Who uses it: the Jinja2 renderer passes BASE_CSS to WeasyPrint alongside the
rendered section HTML. The wordmark markup (class "wordmark") comes from the
base template; layout.py only defines where and how it prints.
"""
from pathlib import Path

_WEBER_DIR = Path(__file__).resolve().parent
_FONTS_DIR = _WEBER_DIR / "fonts"

# file:// URIs built from __file__ so rendering is deterministic both in the
# container (/code/...) and on a developer machine.
_NOTO_REGULAR = (_FONTS_DIR / "NotoSans-Regular.ttf").as_uri()
_NOTO_BOLD = (_FONTS_DIR / "NotoSans-Bold.ttf").as_uri()

BASE_CSS = f"""
@font-face {{
    font-family: "NotoSans";
    font-style: normal;
    font-weight: 400;
    src: url("{_NOTO_REGULAR}");
}}
@font-face {{
    font-family: "NotoSans";
    font-style: normal;
    font-weight: 700;
    src: url("{_NOTO_BOLD}");
}}

@page {{
    size: A4;
    margin: 24mm 18mm 18mm 18mm;

    @top-right {{
        content: element(wordmark);
        margin-top: 3mm;
        margin-right: 0;
    }}

    @bottom-center {{
        content: counter(page);
        font-family: "NotoSans";
        font-size: 8pt;
        color: #7c8188;
    }}
}}

html {{
    font-family: "NotoSans", sans-serif;
    font-size: 9pt;
    color: #111111;
    hyphens: auto;
}}

.wordmark {{
    position: running(wordmark);
    width: 34mm;
    text-align: right;
}}

.wordmark img {{
    width: 100%;
    height: auto;
    display: block;
}}

h1 {{
    font-size: 16pt;
    font-weight: 700;
    color: #245a93;
    margin: 0 0 6mm 0;
}}

h2 {{
    font-size: 11pt;
    font-weight: 700;
    color: #064477;
    margin: 6mm 0 2mm 0;
}}

p {{
    margin: 0 0 2.5mm 0;
    line-height: 1.45;
    text-align: justify;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 2mm 0 4mm 0;
    font-size: 8.5pt;
}}

th {{
    background-color: #064477;
    color: #ffffff;
    font-weight: 700;
    text-align: left;
    padding: 1.6mm 2mm;
    border: 0.3pt solid #064477;
}}

td {{
    padding: 1.6mm 2mm;
    border: 0.3pt solid #b9c2cc;
    vertical-align: top;
}}

.page-break {{
    page-break-before: always;
}}

/* Cover (first section) */
.cover-logo {{
    display: block;
    width: 62mm;
    height: auto;
    margin: 22mm auto 14mm auto;
}}

.cover h1 {{
    font-size: 21pt;
    color: #245a93;
    text-align: center;
    letter-spacing: 0.5pt;
    margin: 0 0 22mm 0;
}}

/* The preamble is the only direct paragraph of the cover section */
.cover > p {{
    margin: 10mm 0 0 27mm;
}}

/* Executor / Client party blocks */
.party {{
    margin: 8mm 0 0 27mm;
}}

.party-label {{
    margin: 0;
    font-size: 9pt;
}}

.party-name {{
    margin: 0.5mm 0 0 0;
    font-weight: 700;
    color: #245a93;
    font-size: 10pt;
}}

.party-address {{
    margin: 0;
    line-height: 1.35;
}}

.party-alias {{
    margin: 1.5mm 0 0 0;
    text-align: right;
    font-size: 9pt;
}}

/* Red banner on the cover when the subsidiary legal block is provisional */
.draft-banner {{
    color: #b00020;
    font-weight: bold;
    font-size: 9pt;
    text-align: center;
    margin: 0 0 6mm 0;
}}

/* Label/value rows (cover, contract info, term lists, billing, ...) */
.kv {{
    margin: 0 0 1.5mm 0;
    line-height: 1.4;
}}

.kv-label {{
    display: inline-block;
    width: 48mm;
    font-weight: 700;
}}

/* Definition list (Master Agreement clause 3) */
.dl-term {{
    font-weight: 700;
}}

/* Legacy contract definition term (bold, no list) */
.clause-subheading {{
    font-weight: 700;
    text-align: left;
    margin: 3mm 0 1mm 0;
}}

/* Module checklist (Annex 1 section 3) */
.checklist {{
    list-style: none;
    margin: 0 0 3mm 0;
    padding: 0;
}}

/* Highlighted final row of kv tables (TOTAL CONTRACT VALUE) */
tr.total td {{
    font-weight: 700;
    border-top: 1pt solid #064477;
}}

/* Signature page: two columns, underline blanks instead of underscores */
.sig-table th {{
    background-color: transparent;
    color: #064477;
    border: none;
    padding: 0 4mm 2mm 0;
}}

.sig-table td {{
    border: none;
    padding: 1mm 4mm 1mm 0;
    vertical-align: bottom;
}}

.sig-line {{
    display: inline-block;
    width: 62mm;
    height: 7mm;
    border-bottom: 0.5pt solid #111111;
}}

/* Commercial breakdown page (legacy Annex 1) */
.breakdown-top {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-top: 4mm;
}}

.breakdown-customer {{
    border: 0.6pt solid #111111;
    padding: 2.5mm 3mm;
    width: 95mm;
}}

.breakdown-customer p {{
    margin: 0;
}}

.breakdown-meta-right {{
    text-align: right;
}}

.breakdown-meta-right p,
.breakdown-meta-left p {{
    margin: 0;
}}

.breakdown-meta-label {{
    font-weight: 700;
    display: inline-block;
    min-width: 26mm;
}}

.breakdown-meta-left {{
    display: flex;
    justify-content: space-between;
    margin-top: 3mm;
}}

.breakdown-table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 5mm;
    font-size: 8.5pt;
}}

.breakdown-table th {{
    background-color: #cfd8e3;
    color: #111111;
    text-align: left;
    padding: 1.5mm 2mm;
    border: 0.3pt solid #b9c2cc;
}}

.breakdown-table td {{
    padding: 1.2mm 2mm;
    border: 0.3pt solid #b9c2cc;
}}

.breakdown-table th:last-child,
.breakdown-table td:last-child {{
    text-align: right;
}}

.breakdown-table tfoot td {{
    border: none;
    text-align: right;
    padding: 1mm 2mm;
}}

.breakdown-table tfoot tr.total td {{
    font-weight: 700;
}}

.notes-title {{
    font-weight: 700;
    margin-top: 3mm;
}}

/* Contract time-band rate tables (Service Support annex) */
.band-rates {{
    margin-top: 4mm;
}}

.band-rates-title {{
    font-weight: 700;
    margin: 0 0 2mm 0;
}}

.band-rates-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 3mm;
    font-size: 8.5pt;
}}

.band-rates-table th,
.band-rates-table td {{
    border: 0.3pt solid #b9c2cc;
    padding: 1.2mm 2mm;
}}

.band-rates-table th {{
    background-color: #064477;
    color: #ffffff;
    text-align: left;
    font-weight: 700;
}}

.band-rates-table td:first-child {{
    font-weight: 700;
}}

.band-rates-table td:not(:first-child) {{
    text-align: center;
}}
"""
