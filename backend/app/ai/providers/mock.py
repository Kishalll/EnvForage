"""Mock LLM provider for testing — returns deterministic responses."""
from typing import TypeVar
from pydantic import BaseModel
from app.ai.providers.base import LLMProvider
from app.ai.models import SuggestedFix, TroubleshootResponse
import uuid

T = TypeVar("T", bound=BaseModel)


class MockProvider(LLMProvider):
    """
    Deterministic mock for unit tests and development.
    Never makes network calls.
    """

    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        response_model: type[T],
    ) -> T:
        if response_model is TroubleshootResponse:
            return TroubleshootResponse(  # type: ignore[return-value]
                session_id=str(uuid.uuid4()),
                root_cause="[Mock] CUDA version mismatch detected in diagnostic report.",
                suggested_fixes=[
                    SuggestedFix(
                        step=1,
                        title="Check NVIDIA driver version",
                        description="Run nvidia-smi to verify driver version meets CUDA requirements.",
                        severity="INFO",
                        safe_commands=["nvidia-smi"],
                    ),
                    SuggestedFix(
                        step=2,
                        title="Verify CUDA toolkit version",
                        description="Confirm installed CUDA version matches framework requirements.",
                        severity="WARNING",
                        safe_commands=["nvcc --version"],
                    ),
                ],
                repair_script_available=False,
                confidence=0.5,
            )
        raise NotImplementedError(f"MockProvider does not support {response_model}")
