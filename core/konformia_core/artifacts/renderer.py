"""Shared artifact rendering engine — jinja config + (lazy) WeasyPrint.

core owns the rendering DISCIPLINE, not the content:

  * ``make_environment`` — the one jinja config both surfaces render with.
    ``StrictUndefined`` turns a typo'd field in a legal document into an error
    at render time, never a silent blank.
  * ``render`` — template → text (HTML or markdown, depending on the template).
  * ``html_to_pdf`` — HTML → PDF bytes via WeasyPrint.

It deliberately does NOT own templates (per-surface: Italian for Konformia,
English for AnnexKit) or display labels. Each app builds an Environment over
its own templates directory and calls these.

WeasyPrint is imported lazily inside ``html_to_pdf`` so that
``import konformia_core.artifacts`` stays light — the classifier and schema
users never pull the native cairo/pango stack. Install it via the ``pdf``
optional extra (``konformia-core[pdf]``); the app backends already ship it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


def make_environment(
    templates_dir: Path | str, *, autoescape: bool = True
) -> Environment:
    """Build the shared jinja Environment for artifact templates.

    ``autoescape`` defaults to True for HTML output; pass ``autoescape=False``
    for markdown templates, where HTML-escaping would corrupt the output.
    """
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=(
            select_autoescape(enabled_extensions=("html", "htm", "jinja"))
            if autoescape
            else False
        ),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render(env: Environment, template_name: str, context: dict[str, Any]) -> str:
    """Render ``template_name`` to text (HTML or markdown, per the template)."""
    return env.get_template(template_name).render(**context)


def html_to_pdf(html_str: str, *, base_url: str | None = None) -> bytes:
    """Render an HTML string to PDF bytes via WeasyPrint.

    ``base_url`` lets the renderer resolve relative asset references (fonts,
    images) against the templates directory.
    """
    # Lazy import: keeps WeasyPrint (+ native cairo/pango) out of a plain
    # ``import konformia_core.artifacts``. The caller (an app backend) ships it.
    from weasyprint import HTML  # type: ignore[import-untyped]

    return HTML(string=html_str, base_url=base_url).write_pdf()
