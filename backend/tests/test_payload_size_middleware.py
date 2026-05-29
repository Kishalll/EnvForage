# backend/tests/test_payload_size_middleware.py

"""Tests for PayloadSizeLimitMiddleware — DoS protection on /api/v1/verify."""

import pytest
from httpx import AsyncClient

from app.middleware.payload_size import MAX_PAYLOAD_BYTES

VERIFY_URL = "/api/v1/verify"
VALID_PROFILE_ID = "550e8400-e29b-41d4-a716-446655440000"

# Minimal valid-shaped payload (profile won't exist in test DB, but
# payload validation runs before the DB lookup — that's what we're testing)
def make_payload(raw_output: str) -> dict:
    return {
        "profile_id": VALID_PROFILE_ID,
        "raw_output": raw_output,
    }


class TestPayloadSizeLimitMiddleware:

    @pytest.mark.anyio
    async def test_small_payload_passes_middleware(self, client: AsyncClient):
        """Normal-sized payloads must reach the route handler (404 = profile
        not found, which means middleware allowed it through)."""
        response = await client.post(
            VERIFY_URL,
            json=make_payload("[PASS] Python 3.10 detected"),
        )
        # 404 is correct here — profile doesn't exist in test DB.
        # What matters: it is NOT 413 (middleware didn't block it).
        assert response.status_code != 413

    @pytest.mark.anyio
    async def test_oversized_payload_returns_413(self, client: AsyncClient):
        """Payloads exceeding 1 MB must be rejected with 413."""
        oversized = "A" * (MAX_PAYLOAD_BYTES + 1)
        response = await client.post(
            VERIFY_URL,
            json=make_payload(oversized),
        )
        assert response.status_code == 413

    @pytest.mark.anyio
    async def test_413_response_matches_api_error_envelope(self, client: AsyncClient):
        """413 error shape must match the existing API error envelope convention."""
        oversized = "A" * (MAX_PAYLOAD_BYTES + 1)
        response = await client.post(
            VERIFY_URL,
            json=make_payload(oversized),
        )
        body = response.json()
        assert "error" in body
        assert body["error"]["code"] == "PAYLOAD_TOO_LARGE"
        assert "message" in body["error"]

    @pytest.mark.anyio
    async def test_exact_limit_boundary_passes(self, client: AsyncClient):
        """Payload at exactly MAX_PAYLOAD_BYTES must not be rejected by middleware."""
        at_limit = "A" * MAX_PAYLOAD_BYTES
        response = await client.post(
            VERIFY_URL,
            json=make_payload(at_limit),
        )
        # Pydantic max_length is also 1MB, so this may 422 from schema
        # validation — that is acceptable. What's NOT acceptable is 413.
        assert response.status_code != 413

    @pytest.mark.anyio
    async def test_content_length_lie_is_caught(self, client: AsyncClient):
        """A client lying about Content-Length must be caught by the stream guard."""
        oversized_body = "A" * (MAX_PAYLOAD_BYTES + 1)
        response = await client.post(
            VERIFY_URL,
            content=oversized_body.encode(),
            headers={
                "Content-Type": "application/json",
                "Content-Length": "100",  # Lies — claims 100 bytes
            },
        )
        assert response.status_code == 413

    @pytest.mark.anyio
    async def test_non_verify_routes_unaffected(self, client: AsyncClient):
        """Middleware must not interfere with other endpoints (e.g. /health)."""
        response = await client.get("/health")
        assert response.status_code == 200