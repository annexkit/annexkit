"""Render an :class:`AnnexIVContext` to Markdown or PDF.

Two formats:
  * **Markdown** — pure text, no native deps. Tested directly.
  * **PDF** — Jinja → HTML → WeasyPrint → bytes. Native deps
    (Cairo/Pango) are installed in the backend Docker image.

The renderer is a pure function. It takes a context and returns bytes
(PDF) or str (Markdown). It never touches the DB; the audit-log
``annex_iv.generated`` event is written by the route layer so the
renderer stays test-friendly.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from app.schemas.annex_iv import AnnexIVContext

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# StrictUndefined surfaces typos like ``{{ ctx.systme.purpose }}`` as
# render errors instead of silently rendering empty strings — critical
# for a doc that's supposed to be audit-grade.
_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
    autoescape=select_autoescape(enabled_extensions=("html", "htm", "jinja")),
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_markdown(ctx: AnnexIVContext) -> str:
    """Render the canonical markdown document."""
    template = _env.get_template("annex_iv.md.jinja")
    return template.render(ctx=ctx)


def render_pdf(ctx: AnnexIVContext) -> bytes:
    """Render the HTML+CSS template to a PDF byte-string.

    Lazy-imports WeasyPrint so the markdown path works in environments
    that don't have Cairo/Pango installed (e.g. host-side test runs).
    """
    from weasyprint import HTML  # type: ignore[import-untyped]

    template = _env.get_template("annex_iv.html.jinja")
    html_str = template.render(ctx=ctx)
    pdf_bytes = HTML(string=html_str, base_url=str(_TEMPLATES_DIR)).write_pdf()
    assert pdf_bytes is not None
    return bytes(pdf_bytes)
