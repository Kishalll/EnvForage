"""Health check endpoints — /api/v1/health.

Provides a readiness probe that verifies database and Redis connectivity.
Use for Kubernetes readiness/liveness probes.
"""

import asyncio
import logging

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.api.deps import DB
from app.cache import get_redis_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/health",
    summary="Readiness health check",
    description="Verifies database and Redis connectivity for orchestrator probes.",
    tags=["Health"],
    responses={
        200: {"description": "All services healthy"},
        503: {"description": "One or more services degraded"},
    },
)
async def health_check(db: DB, response: Response) -> dict:
    """Check database and Redis availability.

    Returns 200 if all services are reachable, 503 if any are degraded.
    """
    db_status = "ok"
    cache_status = "ok"
    overall = "healthy"

    # Check database
    try:
        async with asyncio.timeout(2):
            await db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("Health check: database unreachable — %s", exc)
        db_status = "unavailable"
        overall = "degraded"

    # Check Redis
    try:
        redis = await get_redis_client()
        if redis:
            async with asyncio.timeout(1):
                await redis.ping()
        else:
            cache_status = "not_configured"
    except Exception as exc:
        logger.error("Health check: Redis unreachable — %s", exc)
        cache_status = "unavailable"
        overall = "degraded"

    if overall != "healthy":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": overall,
        "db": db_status,
        "cache": cache_status,
    }
