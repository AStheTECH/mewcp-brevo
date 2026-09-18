"""Shared error helpers for all tool modules."""

import httpx
import pydantic
from brevo.core.api_error import ApiError
from fastmcp_credentials import CredentialError

from ..logging_utils import ToolLogger
from ..schemas import ToolError


def _err(result_class, tlog, code, message, status, retriable=False, retry_after=None):
    tlog.failure(code, message)
    return result_class(
        success=False, statusCode=status, retriable=retriable,
        retry_after_seconds=retry_after,
        error=ToolError(code=code, message=message),
    )


def _parse_retry_after(headers) -> int | None:
    header = (headers or {}).get("Retry-After") or (headers or {}).get("retry-after")
    if not header:
        return None
    try:
        return int(header)
    except ValueError:
        return None


def _handle_request_exc(result_class, tlog, exc):
    if isinstance(exc, httpx.ConnectTimeout):
        tlog.failure("UPSTREAM_ERROR", "Connection timeout")
        return result_class(success=False, statusCode=408, retriable=False,
            error=ToolError(code="UPSTREAM_ERROR", message="Connection timeout"))
    if isinstance(exc, httpx.ReadTimeout):
        tlog.failure("UPSTREAM_ERROR", "Read timeout")
        return result_class(success=False, statusCode=504, retriable=False,
            error=ToolError(code="UPSTREAM_ERROR", message="Read timeout"))
    if isinstance(exc, httpx.RequestError):
        tlog.failure("UPSTREAM_ERROR", "Network error")
        return result_class(success=False, statusCode=503, retriable=True,
            error=ToolError(code="UPSTREAM_ERROR", message=str(exc)))
    # Must precede ValueError — ValidationError subclasses it.
    if isinstance(exc, pydantic.ValidationError):
        tlog.failure("UPSTREAM_ERROR", "Response validation failed")  # str(exc) embeds response field values — never log it
        return result_class(success=False, statusCode=502, retriable=False,
            error=ToolError(code="UPSTREAM_ERROR",
                            message="Upstream response did not match the expected schema"))
    # The SDK raises a typed ApiError subclass (BadRequestError, UnauthorizedError,
    # NotFoundError, TooManyRequestsError, ...) for every non-2xx response.
    if isinstance(exc, ApiError):
        status = exc.status_code or 500
        retry_after = _parse_retry_after(exc.headers)
        if status == 401:
            tlog.failure("AUTH_ERROR", f"HTTP {status}")
            return result_class(success=False, statusCode=status, retriable=False,
                error=ToolError(code="AUTH_ERROR", message="Invalid or missing api-key credential"))
        retriable = status in (429, 500, 502, 503)
        tlog.failure("UPSTREAM_ERROR", f"HTTP {status}")
        msg = exc.body.get("message") if isinstance(exc.body, dict) else str(exc.body) or f"HTTP {status}"
        return result_class(
            success=False, statusCode=status, retriable=retriable,
            retry_after_seconds=retry_after,
            error=ToolError(code="UPSTREAM_ERROR", message=str(msg)),
        )
    # CredentialError subclasses Exception, not ValueError.
    if isinstance(exc, (CredentialError, ValueError)):
        tlog.failure("AUTH_ERROR", str(exc))
        return result_class(success=False, statusCode=401, retriable=False,
            error=ToolError(code="AUTH_ERROR", message=str(exc)))
    tlog.failure("SERVER_ERROR", str(exc))  # log full detail internally
    return result_class(success=False, statusCode=500, retriable=False,
        error=ToolError(code="SERVER_ERROR", message="Unexpected server error"))
