"""Troubleshoot endpoint — POST /api/v1/troubleshoot."""
import logging

from fastapi import APIRouter, Depends, HTTPException

from app.ai.models import TroubleshootRequest, TroubleshootResponse
from app.ai.providers.base import LLMProviderError
from app.ai.service import AITroubleshootService
from app.api.deps import DB
from app.middleware.rate_limit import ai_rate_limit
from app.templates.safety import SafetyViolationError

logger = logging.getLogger(__name__)
router = APIRouter()

# Singleton service instance
_service = AITroubleshootService()


@router.post(
    "/troubleshoot",
    response_model=TroubleshootResponse,
    status_code=201,
    summary="AI-assisted environment troubleshooting",
    description=(
        "Submit a diagnostic report and receive AI-generated root cause analysis "
        "with ordered fix suggestions. All AI output is validated through the "
        "SafetyFilter before being returned."
    ),
    responses={
        201: {"description": "Troubleshooting analysis completed successfully"},
        422: {"description": "Invalid request payload"},
        500: {"description": "LLM provider error or safety violation"},
        503: {"description": "AI service temporarily unavailable"},
        429: {"description": "Rate limit exceeded (10 requests/min)"},
    },
)
async def troubleshoot(
    request: TroubleshootRequest,
    db: DB,
    _rate_limit: None = Depends(ai_rate_limit),
) -> TroubleshootResponse:
    """
    Accept a structured diagnostic report and return AI-powered
    troubleshooting analysis with fix suggestions.

    The AI output is:
    - Structured as validated Pydantic models (never raw text)
    - Filtered through SafetyFilter (no destructive commands)
    - Persisted to the ai_sessions table for audit trail
    - Rate-limited (10 requests per minute per IP)
    """
    try:
        result = await _service.troubleshoot(request, db)
        return result

    except LLMProviderError as exc:
        logger.error("LLM provider error: %s", exc)
        raise HTTPException(
            status_code=503,
            detail={
                "error": "AI_SERVICE_UNAVAILABLE",
                "message": f"AI provider error: {exc.reason}",
                "provider": exc.provider,
            },
        ) from exc

    except SafetyViolationError as exc:
        logger.critical("AI safety violation blocked: %s", exc)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "AI_SAFETY_VIOLATION",
                "message": (
                    "The AI response was blocked by the safety filter. "
                    "This incident has been logged for review."
                ),
            },
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected error in troubleshoot endpoint")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during AI analysis.",
            },
        ) from exc
