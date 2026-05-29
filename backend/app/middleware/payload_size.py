# backend/app/middleware/payload_size.py

"""Middleware to reject HTTP request bodies exceeding a configurable byte limit."""

from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

# 1 MB in bytes. Verification scripts produce text-only terminal output;
# no legitimate payload should approach this limit.
MAX_PAYLOAD_BYTES: int = 1 * 1024 * 1024  # 1 MB


class PayloadSizeLimitMiddleware:
    """
    Reject requests whose body exceeds MAX_PAYLOAD_BYTES.

    Two-layer strategy:
      Layer 1 — Content-Length fast-path:
          If the client declares a Content-Length that already exceeds the
          limit, reject immediately before reading a single body byte.

      Layer 2 — Stream guard:
          Wraps the ASGI receive callable and counts bytes as chunks arrive.
          Rejects the moment the running total exceeds the limit.
          Catches lying clients and chunked-transfer-encoding requests
          (which carry no Content-Length at all).
    """

    def __init__(self, app: ASGIApp, max_bytes: int = MAX_PAYLOAD_BYTES) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Only inspect HTTP — pass WebSocket and lifespan events through.
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)

        # ── Layer 1: Content-Length fast-path ────────────────────────────
        content_length_header = headers.get("content-length")
        if content_length_header is not None:
            try:
                declared_size = int(content_length_header)
            except ValueError:
                declared_size = 0  # Malformed header — let FastAPI handle it

            if declared_size > self.max_bytes:
                await self._send_413(send)
                return

        # ── Layer 2: Stream guard ─────────────────────────────────────────
        bytes_seen = 0
        limit_exceeded = False

        async def limited_receive() -> Message:
            nonlocal bytes_seen, limit_exceeded

            message = await receive()

            if message["type"] == "http.request":
                chunk: bytes = message.get("body", b"")
                bytes_seen += len(chunk)

                if bytes_seen > self.max_bytes:
                    limit_exceeded = True
                    # Return a valid terminal chunk — signals end-of-body
                    # to downstream without passing oversized data.
                    # Raising here would produce a 500, not a 413.
                    return {"type": "http.request", "body": b"", "more_body": False}

            return message

        async def guarded_send(message: Message) -> None:
            # If the stream guard tripped, intercept FastAPI's response
            # (which would be a 422 from empty-body Pydantic failure)
            # and replace it with our 413.
            if limit_exceeded:
                if message.get("type") == "http.response.start":
                    await self._send_413(send)
                    return
                if message.get("type") == "http.response.body":
                    return  # Already sent — suppress FastAPI's body
            await send(message)

        await self.app(scope, limited_receive, guarded_send)

    @staticmethod
    async def _send_413(send: Send) -> None:
        """Send a structured 413 response matching the API error envelope."""
        response = JSONResponse(
            status_code=413,
            content={
                "error": {
                    "code": "PAYLOAD_TOO_LARGE",
                    "message": (
                        f"Request body exceeds the maximum allowed size "
                        f"of {MAX_PAYLOAD_BYTES // (1024 * 1024)} MB."
                    ),
                }
            },
        )
        await response({"type": "http"}, lambda: None, send)