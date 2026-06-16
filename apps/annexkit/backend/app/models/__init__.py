"""Aggregate model imports so Alembic autogenerate sees every table.

``alembic/env.py`` does ``import app.models`` and relies on this module
re-exporting every ORM class so they're registered on
``Base.metadata``. Keep imports here in sync as new models land.
"""

from __future__ import annotations

from app.models.ai_system import AISystem
from app.models.audit_log import AuditLog
from app.models.lead import Lead
from app.models.span import Span
from app.models.tenant import ApiKey, Tenant

__all__ = ["AISystem", "ApiKey", "AuditLog", "Lead", "Span", "Tenant"]
