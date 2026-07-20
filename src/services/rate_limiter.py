"""Small bounded sliding-window limiter for single-process deployments.

Production deployments should still enforce distributed limits at the gateway
or in Redis. This limiter provides a safe, bounded application-level fallback
and prevents attacker-controlled keys from growing memory without limit.
"""

from __future__ import annotations

from collections import OrderedDict, deque
from threading import Lock
from time import monotonic

from fastapi import Request


class BoundedSlidingWindowLimiter:
    def __init__(self, *, window_seconds: float = 60.0, max_keys: int = 10_000) -> None:
        if window_seconds <= 0 or max_keys <= 0:
            raise ValueError("window_seconds and max_keys must be positive")
        self.window_seconds = window_seconds
        self.max_keys = max_keys
        self._events: OrderedDict[str, deque[float]] = OrderedDict()
        self._lock = Lock()

    def is_limited(self, key: str, limit: int) -> bool:
        if limit <= 0:
            return True
        now = monotonic()
        cutoff = now - self.window_seconds
        normalized_key = key[:256]

        with self._lock:
            events = self._events.pop(normalized_key, deque())
            while events and events[0] <= cutoff:
                events.popleft()

            limited = len(events) >= limit
            if not limited:
                events.append(now)

            if events:
                self._events[normalized_key] = events
            self._evict_expired(cutoff)
            while len(self._events) > self.max_keys:
                self._events.popitem(last=False)
            return limited

    def clear(self) -> None:
        with self._lock:
            self._events.clear()

    def _evict_expired(self, cutoff: float) -> None:
        # OrderedDict is LRU-ordered. Stop once a live oldest entry is found.
        while self._events:
            oldest_key = next(iter(self._events))
            oldest_events = self._events[oldest_key]
            while oldest_events and oldest_events[0] <= cutoff:
                oldest_events.popleft()
            if oldest_events:
                break
            self._events.popitem(last=False)


def client_identifier(request: Request) -> str:
    """Return the address already normalized by the ASGI server/proxy policy."""
    if request.client and request.client.host:
        return request.client.host[:128]
    return "unknown"

