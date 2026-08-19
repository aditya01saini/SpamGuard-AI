"""Security: simple in-memory rate limiter (sliding window per client IP).

Intentionally lightweight — no external store required. Suitable for a
single-instance deployment. Limits the number of analysis requests per IP
within a rolling window.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque


class RateLimiter:
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, Deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str) -> bool:
        now = time.monotonic()
        dq = self._hits[key]
        # Evict entries outside the window.
        while dq and now - dq[0] > self.window_seconds:
            dq.popleft()
        if len(dq) >= self.max_requests:
            return False
        dq.append(now)
        return True


# Global limiter instance (shared across routers).
rate_limiter = RateLimiter(max_requests=30, window_seconds=60)
