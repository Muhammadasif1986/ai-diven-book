"""
API dependencies and middleware for the RAG chatbot system.
"""
import time
from typing import Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request
from collections import defaultdict
import asyncio

from src.core.config import settings


class RateLimiter:
    """Simple in-memory rate limiter for API requests."""

    def __init__(self):
        # Store request times for each IP: {ip: [timestamps]}
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()

    async def is_allowed(self, identifier: str) -> bool:
        """
        Check if a request from the given identifier is allowed.

        Args:
            identifier: The identifier to check (e.g., IP address)

        Returns:
            bool: True if request is allowed, False otherwise
        """
        async with self.lock:
            now = time.time()
            # Remove requests older than the window
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if now - req_time < settings.RATE_LIMIT_WINDOW
            ]

            # Check if we're under the limit
            if len(self.requests[identifier]) < settings.RATE_LIMIT_REQUESTS:
                # Add current request
                self.requests[identifier].append(now)
                return True
            else:
                return False

# Global rate limiter instance
rate_limiter = RateLimiter()


async def get_rate_limit_status(identifier: str) -> dict:
    """Get the current rate limit status for an identifier."""
    async with rate_limiter.lock:
        now = time.time()
        # Remove old requests
        rate_limiter.requests[identifier] = [
            req_time for req_time in rate_limiter.requests[identifier]
            if now - req_time < settings.RATE_LIMIT_WINDOW
        ]

        current_requests = len(rate_limiter.requests[identifier])
        remaining = max(0, settings.RATE_LIMIT_REQUESTS - current_requests)

        return {
            "limit": settings.RATE_LIMIT_REQUESTS,
            "remaining": remaining,
            "reset_time": now + settings.RATE_LIMIT_WINDOW
        }


async def check_rate_limit(request: Request):
    """
    Dependency to check rate limit for API requests.
    """
    # Get client IP (considering potential proxy headers)
    client_ip = request.headers.get("x-forwarded-for")
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
    else:
        client_ip = request.client.host

    # Check if request is allowed
    if not await rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit exceeded. Maximum {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW} seconds."
            }
        )

    # Add rate limit headers to response
    status_info = await get_rate_limit_status(client_ip)
    request.state.rate_limit_info = status_info


def get_session_token(request: Request) -> Optional[str]:
    """
    Extract session token from request headers or cookies.
    """
    # Try to get session token from header first
    session_token = request.headers.get("x-session-token")

    # If not found, try to get from cookie
    if not session_token:
        session_token = request.cookies.get("session_token")

    return session_token


def create_session_token() -> str:
    """
    Create a new session token for anonymous users.
    """
    import uuid
    return f"sess_{uuid.uuid4().hex}"


async def log_api_metric(request: Request, response_time_ms: int, status_code: int):
    """
    Log API usage metric to database.
    This is a placeholder - actual implementation would require database access.
    """
    # In a real implementation, this would insert a record into the api_usage_metrics table
    # For now, we'll just log to console
    print(f"API Metric: endpoint={request.url.path}, "
          f"response_time={response_time_ms}ms, "
          f"status_code={status_code}")