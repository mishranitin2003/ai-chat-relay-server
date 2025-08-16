"""
Rate limiting middleware for FastAPI
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import logging

from app.core.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """Rate limiting middleware using token bucket algorithm"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Skip rate limiting for health checks and auth endpoints
        if request.url.path in ["/api/v1/health", "/api/v1/auth/login", "/api/v1/auth/register"]:
            await self.app(scope, receive, send)
            return

        # Get client identifier (IP address or user ID if authenticated)
        client_ip = request.client.host if request.client else "unknown"
        client_key = f"ip:{client_ip}"

        # Check rate limit
        if not await rate_limiter.is_allowed(client_key):
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
