"""
Rate limiting implementation using token bucket algorithm
"""

import time
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
import redis.asyncio as redis
from fastapi import HTTPException, status

from app.core.config import settings


@dataclass
class TokenBucket:
    """Token bucket for rate limiting"""
    capacity: int
    refill_rate: float
    tokens: float
    last_refill: float


class RateLimiter:
    """Redis-based rate limiter using token bucket algorithm"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.local_buckets: Dict[str, TokenBucket] = {}

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            await self.redis_client.ping()
        except Exception:
            # Fallback to in-memory rate limiting
            self.redis_client = None

    async def is_allowed(self, key: str, requests: int = 1) -> bool:
        """Check if request is allowed under rate limit"""
        if self.redis_client:
            return await self._redis_rate_limit(key, requests)
        else:
            return await self._memory_rate_limit(key, requests)

    async def _redis_rate_limit(self, key: str, requests: int) -> bool:
        """Redis-based rate limiting"""
        current_time = time.time()
        pipeline = self.redis_client.pipeline()

        # Get current bucket state
        bucket_data = await self.redis_client.hgetall(f"bucket:{key}")

        if bucket_data:
            tokens = float(bucket_data.get(b"tokens", 0))
            last_refill = float(bucket_data.get(b"last_refill", current_time))
        else:
            tokens = float(settings.RATE_LIMIT_REQUESTS)
            last_refill = current_time

        # Calculate token refill
        time_passed = current_time - last_refill
        refill_rate = settings.RATE_LIMIT_REQUESTS / settings.RATE_LIMIT_WINDOW
        tokens = min(
            settings.RATE_LIMIT_REQUESTS,
            tokens + (time_passed * refill_rate)
        )

        # Check if request can be served
        if tokens >= requests:
            tokens -= requests
            # Update bucket in Redis
            await pipeline.hset(
                f"bucket:{key}",
                mapping={
                    "tokens": str(tokens),
                    "last_refill": str(current_time)
                }
            )
            await pipeline.expire(f"bucket:{key}", settings.RATE_LIMIT_WINDOW * 2)
            await pipeline.execute()
            return True
        else:
            return False

    async def _memory_rate_limit(self, key: str, requests: int) -> bool:
        """In-memory rate limiting fallback"""
        current_time = time.time()

        if key not in self.local_buckets:
            self.local_buckets[key] = TokenBucket(
                capacity=settings.RATE_LIMIT_REQUESTS,
                refill_rate=settings.RATE_LIMIT_REQUESTS / settings.RATE_LIMIT_WINDOW,
                tokens=float(settings.RATE_LIMIT_REQUESTS),
                last_refill=current_time
            )

        bucket = self.local_buckets[key]

        # Refill tokens
        time_passed = current_time - bucket.last_refill
        bucket.tokens = min(
            bucket.capacity,
            bucket.tokens + (time_passed * bucket.refill_rate)
        )
        bucket.last_refill = current_time

        # Check if request can be served
        if bucket.tokens >= requests:
            bucket.tokens -= requests
            return True
        else:
            return False


# Global rate limiter instance
rate_limiter = RateLimiter()
