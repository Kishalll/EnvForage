"""
Seed service — loads YAML fixtures into the database.
Run once on startup (idempotent via upsert logic).

Usage:
    python -m app.services.seed_service
"""
import asyncio
import datetime
import sys
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.profile import EnvironmentProfile, ProfilePackage

SEEDS_DIR = Path(__file__).parent.parent.parent / "seeds"


async def seed_profiles(db: AsyncSession) -> None:
    """Insert or skip environment profiles from profiles.yaml."""
    profiles_file = SEEDS_DIR / "profiles.yaml"
    if not profiles_file.exists():
        print(f"[seed] profiles.yaml not found at {profiles_file}")
        return

    data = yaml.safe_load(profiles_file.read_text(encoding="utf-8"))
    profiles_data = data.get("profiles", [])
    seeded = 0
    skipped = 0

    for p in profiles_data:
        # Check if profile already exists (idempotent)
        result = await db.execute(
            select(EnvironmentProfile).where(EnvironmentProfile.slug == p["slug"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            skipped += 1
            continue

        # Build profile
        last_validated = None
        if p.get("last_validated"):
            lv = p["last_validated"]
            if isinstance(lv, str):
                last_validated = datetime.date.fromisoformat(lv)
            elif isinstance(lv, datetime.date):
                last_validated = lv

        profile = EnvironmentProfile(
            slug=p["slug"],
            name=p["name"],
            description=p.get("description", "").strip(),
            tags=p.get("tags", []),
            os_support=p["os_support"],
            cuda_required=p.get("cuda_required", False),
            python_versions=p["python_versions"],
            cuda_versions=p.get("cuda_versions") or [],
            status=p.get("status", "ACTIVE"),
            last_validated=last_validated,
        )
        db.add(profile)
        await db.flush()  # Get profile.id

        # Build packages
        for pkg in p.get("packages", []):
            db.add(ProfilePackage(
                profile_id=profile.id,
                package_name=pkg["name"],
                version_spec=pkg["version_spec"],
                cuda_variant=pkg.get("cuda_variant"),
                is_optional=pkg.get("is_optional", False),
                install_order=pkg.get("install_order", 0),
            ))

        seeded += 1

    await db.commit()
    print(f"[seed] Profiles: {seeded} seeded, {skipped} already existed.")


async def run_all_seeds() -> None:
    async with AsyncSessionLocal() as db:
        print("[seed] Running database seeds...")
        await seed_profiles(db)
        print("[seed] Done.")


if __name__ == "__main__":
    asyncio.run(run_all_seeds())
