"""Health and readiness endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from meridian_controller.db import get_session

router = APIRouter()


@router.get("/healthz", include_in_schema=False)
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz", include_in_schema=False)
async def readyz(
    session: AsyncSession = Depends(get_session),
) -> Response:
    try:
        await session.execute(text("SELECT 1"))
        return Response(content='{"status":"ready"}', media_type="application/json")
    except Exception:
        return Response(
            content='{"status":"not_ready"}',
            media_type="application/json",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
