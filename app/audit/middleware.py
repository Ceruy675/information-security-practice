from starlette.middleware.base import BaseHTTPMiddleware

from app.audit.logger import log_event

SKIP_PATHS = {"/docs", "/openapi.json", "/health"}


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        if request.url.path in SKIP_PATHS:
            return response

        code = response.status_code

        if code in (401, 403, 429):
            actions = {
                401: "unauthorized",
                403: "access_denied",
                429: "rate_limited",
            }
            action = actions[code]
            status = "failure"
        elif code >= 500:
            action = "server_error"
            status = "error"
        elif request.method != "GET":
            action = f"http_{request.method.lower()}"
            status = "success" if code < 400 else "failure"
        else:
            return response

        log_event(
            action=action,
            status=status,
            ip_address=request.client.host if request.client else "unknown",
            http_method=request.method,
            endpoint=request.url.path,
            status_code=code,
        )

        return response
