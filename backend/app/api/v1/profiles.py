"""Profile endpoints — GET /api/v1/profiles and /api/v1/profiles/{slug}."""
from fastapi import APIRouter, HTTPException, Query

from app.api.deps import DB
from app.schemas.profile import (
    ProfileDetailSchema,
    ProfileFilters,
    ProfileListResponse,
    ProfileSummarySchema,
)
from app.services import profile_service

router = APIRouter()


@router.get("/profiles", response_model=ProfileListResponse)
async def list_profiles(
    db: DB,
    tags: list[str] | None = Query(None, description="Filter by tags"),
    os: str | None = Query(None, description="Filter by OS: LINUX | WSL | WIN"),
    cuda_required: bool | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> ProfileListResponse:
    """
    List all available environment profiles.

    Supports filtering by OS, CUDA requirement, and tags.
    """
    filters = ProfileFilters(
        tags=tags, os=os, cuda_required=cuda_required, page=page, limit=limit
    )
    profiles, total = await profile_service.list_profiles(db, filters)

    return ProfileListResponse(
        profiles=[ProfileSummarySchema.model_validate(p) for p in profiles],
        total=total,
        page=page,
        page_size=limit,
    )


@router.get("/profiles/{slug}", response_model=ProfileDetailSchema)
async def get_profile(slug: str, db: DB) -> ProfileDetailSchema:
    """
    Get full details for a single environment profile including package list.
    """
    profile = await profile_service.get_profile_by_slug(db, slug)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "PROFILE_NOT_FOUND",
                    "message": f"Profile '{slug}' not found",
                }
            },
        )
    return ProfileDetailSchema.model_validate(profile)
