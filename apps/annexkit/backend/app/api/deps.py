"""Reusable FastAPI dependencies.

For Day 1 we only export `SessionDep` (an `AsyncSession` bound to the
current request). Tenant API key auth lands in Day 3 when the ingest
endpoint goes live.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
