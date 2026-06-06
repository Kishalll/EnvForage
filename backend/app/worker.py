import json
from celery import Celery

from app.config import get_settings
from app.compatibility.models import OSTarget, PackageConstraint, ResolvedEnvironment
from app.compatibility.resolver import CompatibilityResolver
from app.compatibility.errors import (
    IncompatibilityError,
    UnknownVersionError,
    UnsupportedOSError,
)
from app.schemas.diagnostic import CompatibilityIssue, DiagnoseResponse

settings = get_settings()

celery_app = Celery(
    "envforge_worker",
    broker=settings.redis_url or "redis://localhost:6379/0",
    backend=settings.redis_url or "redis://localhost:6379/0",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

from typing import Literal

@celery_app.task(name="run_diagnose_task")
def run_diagnose_task(report_id: str, report_data: dict, target_os: Literal['LINUX', 'WIN', 'WSL'], profiles_data: list[dict]) -> dict:
    """
    Celery task that resolves an environment's dependencies against all profiles
    and returns a structured DiagnoseResponse as a dict.
    """
    resolver = CompatibilityResolver()
    
    issues: list[CompatibilityIssue] = []
    compatible_profiles: list[str] = []
    recommendations: list[str] = []

    active_python_version = report_data.get("active_python", {}).get("version", "3.10") if report_data.get("active_python") else "3.10"
    cuda_version = report_data.get("cuda", {}).get("version") if report_data.get("cuda") else None
    rocm_version = report_data.get("rocm", {}).get("version") if report_data.get("rocm") else None

    for profile_dict in profiles_data:
        profile_slug: str = profile_dict.get("slug", "")
        os_support: list[str] = profile_dict.get("os_support", [])
        cuda_required: bool = profile_dict.get("cuda_required", False)
        rocm_required: bool = profile_dict.get("rocm_required", False)
        
        packages = []
        for pkg in profile_dict.get("packages", []):
            packages.append(
                PackageConstraint(
                    name=pkg.get("package_name", ""),
                    version_spec=pkg.get("version_spec", ""),
                    cuda_variant=pkg.get("cuda_variant"),
                )
            )

        try:
            result = resolver.resolve(
                packages=packages,
                python_version=active_python_version,
                cuda_version=cuda_version,
                rocm_version=rocm_version,
                target_os=target_os,
                profile_slug=profile_slug,
                os_support=os_support,
                cuda_required=cuda_required,
                rocm_required=rocm_required,
            )
            
            if isinstance(result, ResolvedEnvironment):
                compatible_profiles.append(profile_slug)
                if result.warnings:
                    recommendations.extend(result.warnings)
        
        except IncompatibilityError as exc:
            issues.append(
                CompatibilityIssue(
                    severity="ERROR",
                    component=exc.component,
                    message=str(exc),
                    suggested_fix=exc.suggestion,
                    docs_url=exc.docs_url,
                )
            )
        except (UnknownVersionError, UnsupportedOSError) as exc:
            issues.append(
                CompatibilityIssue(
                    severity="ERROR",
                    component="compatibility",
                    message=str(exc),
                    suggested_fix=None,
                    docs_url=None,
                )
            )
        except Exception as exc:
            pass # Or log it

    response = DiagnoseResponse(
        report_id=report_id,
        compatible_profiles=compatible_profiles,
        issues=issues,
        recommendations=recommendations,
    )
    
    return response.model_dump()
