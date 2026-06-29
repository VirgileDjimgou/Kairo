import time
from collections import defaultdict


class RateLimiter:
    """
    Simple in-memory sliding window rate limiter.

    Tracks request timestamps per key (e.g., IP+endpoint) and rejects
    requests that exceed max_requests within window_seconds.
    """

    def __init__(self) -> None:
        self._windows: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        cutoff = now - window_seconds
        timestamps = [t for t in self._windows[key] if t > cutoff]
        if len(timestamps) >= max_requests:
            return False
        timestamps.append(now)
        self._windows[key] = timestamps
        return True

    def reset(self, key: str) -> None:
        self._windows.pop(key, None)


# Singleton shared across the application
rate_limiter = RateLimiter()
