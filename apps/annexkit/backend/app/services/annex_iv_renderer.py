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

from konformia_core.artifacts import html_to_pdf, make_environment, render

from app.schemas.annex_iv import AnnexIVContext

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# The shared engine configures StrictUndefined (a typo like
# ``{{ ctx.systme.purpose }}`` becomes a render error, not a silent blank —
# critical for an audit-grade doc) over AnnexKit's own English templates.
_env = make_environment(_TEMPLATES_DIR)


def render_markdown(ctx: AnnexIVContext) -> str:
    """Render the canonical markdown document."""
    return render(_env, "annex_iv.md.jinja", {"ctx": ctx})


def render_pdf(ctx: AnnexIVContext) -> bytes:
    """Render the HTML+CSS template to a PDF byte-string.

    WeasyPrint is lazy-imported inside ``core.artifacts.html_to_pdf`` so the
    markdown path works in environments without Cairo/Pango (e.g. host-side
    test runs).
    """
    html_str = render(_env, "annex_iv.html.jinja", {"ctx": ctx})
    return html_to_pdf(html_str, base_url=str(_TEMPLATES_DIR))
