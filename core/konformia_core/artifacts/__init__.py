"""Shared artifact rendering engine.

Public API (see ``renderer``): ``make_environment``, ``render``, ``html_to_pdf``.
core owns the rendering discipline (jinja config + WeasyPrint); each app owns its
own per-language templates and label maps and builds an Environment over them.
"""

from __future__ import annotations

from konformia_core.artifacts.renderer import html_to_pdf, make_environment, render

__all__ = ["html_to_pdf", "make_environment", "render"]
