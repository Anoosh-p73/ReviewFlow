"""Request identifier validation, generation, propagation, and logging."""

import re
import time
from http import HTTPStatus
from uuid import uuid4

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import get_logger
from app.core.request_context import current_request_id

REQUEST_ID_HEADER = "X-Request-ID"
_VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def resolve_request_id(candidate: str | None) -> str:
    """Accept a safe caller identifier or create an opaque replacement."""
    if candidate is not None and _VALID_REQUEST_ID.fullmatch(candidate):
        return candidate
    return str(uuid4())


class RequestIdMiddleware:
    """Attach one safe request ID to HTTP responses and structured logs."""

    def __init__(self, app: ASGIApp) -> None:
        self._app = app
        self._logger = get_logger(__name__)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        request_id = resolve_request_id(headers.get(REQUEST_ID_HEADER))
        token = current_request_id.set(request_id)
        started_at = time.perf_counter()
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR

        async def send_with_request_id(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = MutableHeaders(scope=message)
                response_headers[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self._app(scope, receive, send_with_request_id)
        except Exception:
            self._logger.exception(
                "request_failed",
                extra={
                    "method": scope["method"],
                    "path": scope["path"],
                    "status_code": int(status_code),
                },
            )
            raise
        finally:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 3)
            self._logger.info(
                "request_completed",
                extra={
                    "method": scope["method"],
                    "path": scope["path"],
                    "status_code": int(status_code),
                    "duration_ms": duration_ms,
                },
            )
            current_request_id.reset(token)
