"""Unit tests for backend/app/core/events.py – webhook event dispatcher.

Covers
------
- Successful delivery logs target URL and status code.
- HTTPStatusError (5xx) logs target URL, status code, payload hash, and
  truncated response body.
- TimeoutException logs target URL with status_code=None.
- RequestError (connection error) logs target URL with status_code=None.
- Payload hash is deterministic and appears in failure logs.
- Response body is truncated to 500 characters in error logs.
- dispatch_webhooks fan-out returns per-URL success mapping.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.core.events import (
    _RESPONSE_BODY_TRUNCATION_LIMIT,
    _hash_payload,
    _truncate,
    dispatch_webhook,
    dispatch_webhooks,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TARGET_URL = "https://example.com/webhook"
PAYLOAD: dict[str, Any] = {"event": "test", "data": {"key": "value"}}


def _make_http_status_error(status_code: int, body: str) -> httpx.HTTPStatusError:
    """Build an httpx.HTTPStatusError with the given status code and body."""
    request = httpx.Request("POST", TARGET_URL)
    response = httpx.Response(status_code=status_code, text=body, request=request)
    return httpx.HTTPStatusError(
        message=f"HTTP {status_code}",
        request=request,
        response=response,
    )


# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------


class TestHashPayload:
    def test_deterministic(self) -> None:
        h1 = _hash_payload({"b": 2, "a": 1})
        h2 = _hash_payload({"a": 1, "b": 2})
        assert h1 == h2

    def test_sha256_hex(self) -> None:
        payload = {"event": "ping"}
        serialised = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        expected = hashlib.sha256(serialised.encode()).hexdigest()
        assert _hash_payload(payload) == expected

    def test_different_payloads_differ(self) -> None:
        assert _hash_payload({"a": 1}) != _hash_payload({"a": 2})


class TestTruncate:
    def test_short_string_unchanged(self) -> None:
        assert _truncate("hello") == "hello"

    def test_long_string_truncated(self) -> None:
        long_str = "x" * 600
        result = _truncate(long_str)
        assert len(result) == _RESPONSE_BODY_TRUNCATION_LIMIT + 1  # +1 for ellipsis char
        assert result.endswith("…")

    def test_exact_limit_unchanged(self) -> None:
        s = "a" * _RESPONSE_BODY_TRUNCATION_LIMIT
        assert _truncate(s) == s

    def test_custom_limit(self) -> None:
        result = _truncate("abcdef", limit=3)
        assert result == "abc…"


# ---------------------------------------------------------------------------
# dispatch_webhook – success path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_webhook_success_returns_true(caplog: pytest.LogCaptureFixture) -> None:
    """A 2xx response must return True and log an info message."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()  # does not raise

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(return_value=mock_response)

    with caplog.at_level(logging.INFO, logger="app.core.events"):
        result = await dispatch_webhook(TARGET_URL, PAYLOAD, client=mock_client)

    assert result is True
    assert any("successfully" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_dispatch_webhook_success_logs_target_url(caplog: pytest.LogCaptureFixture) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(return_value=mock_response)

    with caplog.at_level(logging.INFO, logger="app.core.events"):
        await dispatch_webhook(TARGET_URL, PAYLOAD, client=mock_client)

    record = next(r for r in caplog.records if "successfully" in r.message)
    assert record.__dict__.get("target_url") == TARGET_URL


# ---------------------------------------------------------------------------
# dispatch_webhook – HTTPStatusError (5xx / 4xx)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_webhook_http_status_error_returns_false(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A 5xx response must return False."""
    exc = _make_http_status_error(500, "Internal Server Error")
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock(side_effect=exc)

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(return_value=mock_response)

    with caplog.at_level(logging.ERROR, logger="app.core.events"):
        result = await dispatch_webhook(TARGET_URL, PAYLOAD, client=mock_client)

    assert result is False


@pytest.mark.asyncio
async def test_dispatch_webhook_http_status_error_logs_status_code(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The status code must appear in the log extra fields on failure."""
    exc = _make_http_status_error(503, "Service Unavailable")
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock(side_effect=exc)

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(return_value=mock_response)

    with caplog.at_level(logging.ERROR, logger="app.core.events"):
        await dispatch_webhook(TARGET_URL, PAYLOAD, client=mock_client)

    error_record = next(r for r in caplog.records if r.levelno == logging.ERROR)
    assert error_record.__dict__.get("status_code") == 503


@pytest.mark.asyncio
async def test_dispatch_webhook_http_status_error_logs_payload_hash(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The payload hash must appear in the log extra fields on failure."""
    exc = _make_http_status_error(500, "error body")
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock(side_effect=exc)

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(return_value=mock_response)

    expected_hash = _hash_payload(PAYLOAD)

    with caplog.at_level(logging.ERROR, logger="app.core.events"):
        await dispatch_webhook(TARGET_URL, PAYLOAD, client=mock_client)

    error_record = next(r for r in caplog.records if r.levelno == logging.ERROR)
    assert error_record.__dict__.get("payload_hash") == expected_hash


@pytest.mark.asyncio
async def test_dispatch_webhook_http_status_error_logs_response_body(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The (truncated) response body must appear in log extra fields."""
    body = "x" * 600  # longer than truncation limit
    exc = _make_http_status_error(422, body)
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock(side_effect=exc)

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(return_value=mock_response)

    with caplog.at_level(logging.ERROR, logger="app.core.events"):
        await dispatch_webhook(TARGET_URL, PAYLOAD, client=mock_client)

    error_record = next(r for r in caplog.records if r.levelno == logging.ERROR)
    logged_body: str = error_record.__dict__.get("response_body", "")
    assert len(logged_body) <= _RESPONSE_BODY_TRUNCATION_LIMIT + 1  # +1 for ellipsis
    assert logged_body.endswith("…")


@pytest.mark.asyncio
async def test_dispatch_webhook_http_status_error_logs_target_url(
    caplog: pytest.LogCaptureFixture,
) -> None:
    exc = _make_http_status_error(500, "err")
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock(side_effect=exc)

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(return_value=mock_response)

    with caplog.at_level(logging.ERROR, logger="app.core.events"):
        await dispatch_webhook(TARGET_URL, PAYLOAD, client=mock_client)

    error_record = next(r for r in caplog.records if r.levelno == logging.ERROR)
    assert error_record.__dict__.get("target_url") == TARGET_URL


# ---------------------------------------------------------------------------
# dispatch_webhook – TimeoutException
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_webhook_timeout_returns_false(
    caplog: pytest.LogCaptureFixture,
) -> None:
    request = httpx.Request("POST", TARGET_URL)
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(
        side_effect=httpx.TimeoutException("timed out", request=request)
    )

    with caplog.at_level(logging.ERROR, logger="app.core.events"):
        result = await dispatch_webhook(TARGET_URL, PAYLOAD, client=mock_client)

    assert result is False


@pytest.mark.asyncio
async def test_dispatch_webhook_timeout_logs_none_status_code(
    caplog: pytest.LogCaptureFixture,
) -> None:
    request = httpx.Request("POST", TARGET_URL)
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(
        side_effect=httpx.TimeoutException("timed out", request=request)
    )

    with caplog.at_level(logging.ERROR, logger="app.core.events"):
        await dispatch_webhook(TARGET_URL, PAYLOAD, client=mock_client)

    error_record = next(r for r in caplog.records if r.levelno == logging.ERROR)
    assert error_record.__dict__.get("status_code") is None
    assert error_record.__dict__.get("target_url") == TARGET_URL


# ---------------------------------------------------------------------------
# dispatch_webhook – RequestError (connection failure)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_webhook_request_error_returns_false(
    caplog: pytest.LogCaptureFixture,
) -> None:
    request = httpx.Request("POST", TARGET_URL)
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(
        side_effect=httpx.ConnectError("connection refused", request=request)
    )

    with caplog.at_level(logging.ERROR, logger="app.core.events"):
        result = await dispatch_webhook(TARGET_URL, PAYLOAD, client=mock_client)

    assert result is False


@pytest.mark.asyncio
async def test_dispatch_webhook_request_error_logs_target_url_and_no_status(
    caplog: pytest.LogCaptureFixture,
) -> None:
    request = httpx.Request("POST", TARGET_URL)
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(
        side_effect=httpx.ConnectError("connection refused", request=request)
    )

    with caplog.at_level(logging.ERROR, logger="app.core.events"):
        await dispatch_webhook(TARGET_URL, PAYLOAD, client=mock_client)

    error_record = next(r for r in caplog.records if r.levelno == logging.ERROR)
    assert error_record.__dict__.get("target_url") == TARGET_URL
    assert error_record.__dict__.get("status_code") is None


# ---------------------------------------------------------------------------
# dispatch_webhooks – fan-out
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_webhooks_returns_per_url_result() -> None:
    """dispatch_webhooks must return a {url: bool} mapping for all URLs."""
    url_a = "https://a.example.com/hook"
    url_b = "https://b.example.com/hook"

    async def _fake_dispatch(url: str, payload: dict[str, Any], **kwargs: Any) -> bool:
        return url == url_a  # url_a succeeds, url_b fails

    with patch("app.core.events.dispatch_webhook", side_effect=_fake_dispatch):
        results = await dispatch_webhooks([url_a, url_b], PAYLOAD)

    assert results == {url_a: True, url_b: False}


@pytest.mark.asyncio
async def test_dispatch_webhooks_empty_list_returns_empty_dict() -> None:
    results = await dispatch_webhooks([], PAYLOAD)
    assert results == {}


@pytest.mark.asyncio
async def test_dispatch_webhook_serialization_error_returns_false(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """If payload contains non-serialisable data, _hash_payload raises TypeError,
    which must be caught by the generic exception handler and log details with status_code=None, payload_hash=None.
    """
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    # Payload contains a set, which is not JSON serialisable
    invalid_payload = {"set_data": {1, 2, 3}}

    with caplog.at_level(logging.ERROR, logger="app.core.events"):
        result = await dispatch_webhook(TARGET_URL, invalid_payload, client=mock_client)

    assert result is False
    error_record = next(r for r in caplog.records if r.levelno == logging.ERROR)
    assert error_record.__dict__.get("status_code") is None
    assert error_record.__dict__.get("payload_hash") is None
    assert "unexpected error" in error_record.message


@pytest.mark.asyncio
async def test_dispatch_webhook_unexpected_exception_returns_false(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """An unexpected exception during POST (e.g. RuntimeError) must return False
    and log details via logger.exception with status_code=None.
    """
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(side_effect=RuntimeError("something went wrong"))

    with caplog.at_level(logging.ERROR, logger="app.core.events"):
        result = await dispatch_webhook(TARGET_URL, PAYLOAD, client=mock_client)

    assert result is False
    error_record = next(r for r in caplog.records if r.levelno == logging.ERROR)
    assert error_record.__dict__.get("status_code") is None
    assert error_record.__dict__.get("payload_hash") == _hash_payload(PAYLOAD)
    assert "unexpected error" in error_record.message


@pytest.mark.asyncio
async def test_dispatch_webhooks_handles_unexpected_exceptions_in_fanout(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """If a dispatch_webhook call raises an unhandled exception, dispatch_webhooks
    must handle it, log the error, and mark that URL as False.
    """
    url_a = "https://a.example.com/hook"
    url_b = "https://b.example.com/hook"

    # We mock dispatch_webhook to raise an exception for url_b
    async def _fake_dispatch(url: str, payload: dict[str, Any], **kwargs: Any) -> bool:
        if url == url_b:
            raise ValueError("Unexpected crash in dispatch")
        return True

    with patch("app.core.events.dispatch_webhook", side_effect=_fake_dispatch):
        with caplog.at_level(logging.ERROR, logger="app.core.events"):
            results = await dispatch_webhooks([url_a, url_b], PAYLOAD)

    assert results == {url_a: True, url_b: False}
    error_record = next(r for r in caplog.records if r.levelno == logging.ERROR)
    assert "Unexpected error in dispatch_webhooks fan-out" in error_record.message
    assert error_record.__dict__.get("target_url") == url_b
