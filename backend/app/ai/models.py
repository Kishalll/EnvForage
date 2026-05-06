"""AI Layer — Pydantic models for structured troubleshoot responses."""
from typing import Literal
from pydantic import BaseModel, Field


class SuggestedFix(BaseModel):
    step: int
    title: str
    description: str
    severity: Literal["CRITICAL", "WARNING", "INFO"]
    safe_commands: list[str] = Field(default_factory=list)
    repair_template_id: str | None = None


class TroubleshootResponse(BaseModel):
    session_id: str
    root_cause: str
    suggested_fixes: list[SuggestedFix]
    repair_script_available: bool = False
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    disclaimer: str = (
        "AI suggestions are advisory only. Review all steps before executing. "
        "EnvForge is not responsible for system changes."
    )
