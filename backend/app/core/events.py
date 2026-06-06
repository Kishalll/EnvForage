"""
Asynchronous webhook event dispatcher.

Sends webhook payloads to registered target URLs and ensures that
failed deliveries are logged with enough detail to allow post-mortem
debugging without re-running the triggering event.

Logged on failure
-----------------
- ``target_url``   – the registered endpoint that was called
- ``status_code``  – HTTP status returned (or ``None`` for network errors)
- ``payload_hash`` – SHA-256 hex-digest of the serialised payload, so the
                     exact payload can be correlated with request logs
- ``response_body`` – up to 500 characters (plus ellipsis if truncated) of the response body
- full exception traceback (via ``logger.exception``)
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Maximum number of characters from the response body to include in the log.
_RESPONSE_BODY_TRUNCATION_LIMIT: int = 500

# Default timeout (seconds) for a single webhook delivery attempt.
_DEFAULT_TIMEOUT: float = 10.0


def _hash_payload(payload: dict[str, Any]) -> str:
    """Return the SHA-256 hex-digest of the JSON-serialised *payload*.

    The digest is deterministic (sorted keys, no extra whitespace) so it can
    be used to correlate log entries with request logs or stored payloads.
    """
    serialised = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialised.encode()).hexdigest()


def _truncate(text: str, limit: int = _RESPONSE_BODY_TRUNCATION_LIMIT) -> str:
    """Return *text* truncated to *limit* characters with an ellipsis suffix."""
    if len(text) <= limit:
        return text
    return text[:limit] + "…"


async def dispatch_webhook(
    target_url: str,
    payload: dict[str, Any],
    *,
    timeout: float = _DEFAULT_TIMEOUT,
    client: httpx.AsyncClient | None = None,
) -> bool:
    """POST *payload* as JSON to *target_url*.

    Parameters
    ----------
    target_url:
        The registered webhook endpoint.
    payload:
        Arbitrary JSON-serialisable event data.
    timeout:
        Request timeout in seconds. Defaults to :data:`_DEFAULT_TIMEOUT`.
    client:
        An optional pre-configured :class:`httpx.AsyncClient` to use.
        When ``None`` a short-lived client is created internally.
        Pass a client explicitly in tests to avoid real network calls.

    Returns
    -------
    bool
        ``True`` if the delivery succeeded (2xx response), ``False`` otherwise.
    """
    async def _send(c: httpx.AsyncClient) -> bool:
        payload_hash = None
        try:
            payload_hash = _hash_payload(payload)
            response = await c.post(
                target_url,
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            logger.info(
                "Webhook delivered successfully",
                extra={
                    "target_url": target_url,
                    "status_code": response.status_code,
                    "payload_hash": payload_hash,
                },
            )
            return True

        except httpx.HTTPStatusError as exc:
            # Server returned a 4xx / 5xx response.
            response_body = _truncate(exc.response.text)
            logger.error(
                "Webhook delivery failed: non-2xx response",
                extra={
                    "target_url": target_url,
                    "status_code": exc.response.status_code,
                    "payload_hash": payload_hash,
                    "response_body": response_body,
                },
                exc_info=True,
            )
            return False

        except httpx.TimeoutException:
            # Network-level timeout – no status code available.
            logger.error(
                "Webhook delivery failed: request timed out",
                extra={
                    "target_url": target_url,
                    "status_code": None,
                    "payload_hash": payload_hash,
                    "response_body": None,
                },
                exc_info=True,
            )
            return False

        except httpx.RequestError:
            # Covers connection errors, DNS failures, etc.
            logger.error(
                "Webhook delivery failed: network error",
                extra={
                    "target_url": target_url,
                    "status_code": None,
                    "payload_hash": payload_hash,
                    "response_body": None,
                },
                exc_info=True,
            )
            return False

        except Exception:
            # Catch-all: unexpected runtime errors (e.g. serialisation).
            logger.exception(
                "Webhook delivery failed: unexpected error",
                extra={
                    "target_url": target_url,
                    "status_code": None,
                    "payload_hash": payload_hash,
                    "response_body": None,
                },
            )
            return False

    if client is not None:
        return await _send(client)

    async with httpx.AsyncClient() as auto_client:
        return await _send(auto_client)


async def dispatch_webhooks(
    registrations: list[str],
    payload: dict[str, Any],
    *,
    timeout: float = _DEFAULT_TIMEOUT,
) -> dict[str, bool]:
    """Dispatch *payload* to every URL in *registrations* concurrently.

    Parameters
    ----------
    registrations:
        List of registered webhook URLs to notify.
    payload:
        Event data to POST.
    timeout:
        Per-request timeout forwarded to :func:`dispatch_webhook`.

    Returns
    -------
    dict[str, bool]
        Mapping of ``{url: success}`` for each registered URL.
    """
    if not registrations:
        return {}

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *(
                dispatch_webhook(url, payload, timeout=timeout, client=client)
                for url in registrations
            ),
            return_exceptions=True,
        )

    final_results = {}
    for url, res in zip(registrations, results, strict=True):
        if isinstance(res, BaseException):
            logger.error(
                "Unexpected error in dispatch_webhooks fan-out",
                extra={"target_url": url},
                exc_info=res,
            )
            final_results[url] = False
        else:
            final_results[url] = res

    return final_results
