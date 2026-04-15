import time
from collections import defaultdict
from threading import Lock


class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            requests = self._requests[key]
            # Remove old requests outside window
            self._requests[key] = [t for t in requests if now - t < self.window_seconds]
            if len(self._requests[key]) >= self.max_requests:
                return False
            self._requests[key].append(now)
            return True


rate_limiter = RateLimiter()
