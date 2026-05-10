"""span idempotency unique key on (tenant_id, trace_id, span_id)

Revision ID: 0002_span_idempotency
Revises: 0001_initial
Create Date: 2026-05-07 13:00:00.000000

Adds a unique constraint on ``spans(tenant_id, trace_id, span_id)`` so
duplicate ingests are rejected at the DB layer. The service layer's
``span_service.ingest`` now does a SELECT-then-INSERT dedupe; the
unique index is the backstop for concurrent insert races.

Why a separate migration:
  * Demonstrates the production migration workflow (don't amend
    history once a revision is deployed).
  * Reads cleanly in a future PR review — "Day 3 fix: idempotency".
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_span_idempotency"
down_revision: str | Sequence[str] | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_spans_tenant_trace_span",
        "spans",
        ["tenant_id", "trace_id", "span_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_spans_tenant_trace_span", "spans", type_="unique")
