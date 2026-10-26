"""Convert an uploaded .docx annex into sanitized HTML for the printed PDF.

The Print PDF modal attaches Word files; this module extracts their content
at upload time so the renderer works with plain HTML and never opens the
original file again. v1 scope: paragraphs (with bold/italic runs) and
tables. Images and complex styles are deliberately out of scope.

Security: every text run is HTML-escaped before being written, so the
returned string only contains the tags this module emits. The renderer can
insert it as trusted HTML even though it originates from a user upload.
"""
import io
from zipfile import BadZipFile

from docx import Document
from docx.opc.exceptions import PackageNotFoundError
from docx.table import Table
from docx.text.paragraph import Paragraph

MAX_ANNEX_HTML_CHARS = 500_000


class AnnexParseError(ValueError):
    """The uploaded file could not be read as a .docx document with text."""


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _render_runs(paragraph: Paragraph) -> str:
    """Render one paragraph: bold/italic runs wrapped in <strong>/<em>."""
    parts = []
    for run in paragraph.runs:
        text = _escape(run.text)
        if not text:
            continue
        if run.bold:
            text = f"<strong>{text}</strong>"
        if run.italic:
            text = f"<em>{text}</em>"
        parts.append(text)
    return "".join(parts)


def _render_paragraph(paragraph: Paragraph) -> str:
    html = _render_runs(paragraph)
    return f"<p>{html}</p>" if html else ""


def _render_table(table: Table) -> str:
    """Render one table. The first row is the header (bold cells)."""
    rows = []
    for row_index, row in enumerate(table.rows):
        tag = "th" if row_index == 0 else "td"
        cells = "".join(
            f"<{tag}>{_escape(cell.text.strip())}</{tag}>" for cell in row.cells
        )
        rows.append(f"<tr>{cells}</tr>")
    return f"<table><tbody>{''.join(rows)}</tbody></table>"


def parse_docx_annex(content: bytes, fallback_title: str) -> tuple[str, str]:
    """Return (title, html) for one uploaded Word annex.

    The title comes from the caller (the uploaded filename without
    extension); the document content itself carries no reliable title.
    Raises AnnexParseError when the file is not a readable .docx or
    contains no text at all (a silently empty annex page would be a
    defect the user cannot see until printing).
    """
    try:
        document = Document(io.BytesIO(content))
    except (PackageNotFoundError, BadZipFile) as exc:
        raise AnnexParseError("The file is not a valid Word (.docx) document.") from exc

    parts: list[str] = []
    for block in document.iter_inner_content():
        if isinstance(block, Paragraph):
            rendered = _render_paragraph(block)
        elif isinstance(block, Table):
            rendered = _render_table(block)
        else:  # pragma: no cover - defensive: python-docx adds no other type yet
            continue
        if rendered:
            parts.append(rendered)

    html = "".join(parts)
    if not html:
        raise AnnexParseError("The document contains no text.")
    if len(html) > MAX_ANNEX_HTML_CHARS:
        raise AnnexParseError("The document content is too large.")

    title = (fallback_title or "Annex").strip()[:200] or "Annex"
    return title, html
