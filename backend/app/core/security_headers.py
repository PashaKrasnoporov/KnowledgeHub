from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request,
        call_next,
    ):
        response = await call_next(
            request
        )

        response.headers[
            "X-Content-Type-Options"
        ] = "nosniff"

        response.headers[
            "X-Frame-Options"
        ] = "DENY"

        response.headers[
            "Strict-Transport-Security"
        ] = (
            "max-age=31536000; "
            "includeSubDomains"
        )

        response.headers[
            "Referrer-Policy"
        ] = (
            "strict-origin-when-cross-origin"
        )

        response.headers[
            "Permissions-Policy"
        ] = (
            "camera=(), "
            "microphone=(), "
            "geolocation=()"
        )

        response.headers[
            "Cross-Origin-Opener-Policy"
        ] = "same-origin"

        response.headers[
            "Cross-Origin-Resource-Policy"
        ] = "same-origin"

        response.headers[
            "Content-Security-Policy"
        ] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'"
        )

        return response
