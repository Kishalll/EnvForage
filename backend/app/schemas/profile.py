"""Pydantic schemas for environment profiles API."""
import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Package schemas ────────────────────────────────────────────────────────────

class PackageSpecSchema(BaseModel):
    package_name: str
    version_spec: str
    cuda_variant: str | None = None
    is_optional: bool = False
    install_order: int = 0


# ── Profile schemas ────────────────────────────────────────────────────────────

class ProfileSummarySchema(BaseModel):
    """Lightweight profile for list responses."""
    id: uuid.UUID
    slug: str
    name: str
    description: str | None
    tags: list[str] | None
    os_support: list[str]
    cuda_required: bool
    python_versions: list[str]
    cuda_versions: list[str] | None
    status: str
    last_validated: date | None

    model_config = {"from_attributes": True}


class ProfileDetailSchema(ProfileSummarySchema):
    """Full profile including package list."""
    packages: list[PackageSpecSchema]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── List response ──────────────────────────────────────────────────────────────

class ProfileListResponse(BaseModel):
    profiles: list[ProfileSummarySchema]
    total: int
    page: int
    page_size: int


# ── Query filters ──────────────────────────────────────────────────────────────

class ProfileFilters(BaseModel):
    tags: list[str] | None = None
    os: str | None = Field(None, description="Filter by OS: LINUX | WSL | WIN")
    cuda_required: bool | None = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
