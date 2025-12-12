from __future__ import annotations

from dataclasses import asdict, dataclass
from threading import Lock
from typing import Dict


@dataclass
class _MetricsState:
    total_requests: int = 0
    total_failures: int = 0
    timed_requests: int = 0
    total_latency_ms: float = 0.0


class Metrics:
    """Thread-safe in-memory counters for basic request instrumentation."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._state = _MetricsState()

    def record(self, *, duration_ms: float | None, success: bool) -> None:
        with self._lock:
            self._state.total_requests += 1
            if not success:
                self._state.total_failures += 1
                return
            if duration_ms is not None:
                self._state.timed_requests += 1
                self._state.total_latency_ms += duration_ms

    def snapshot(self) -> Dict[str, float]:
        with self._lock:
            state = asdict(self._state)
        success_count = state["total_requests"] - state["total_failures"]
        avg_latency = (
            state["total_latency_ms"] / state["timed_requests"]
            if state["timed_requests"]
            else 0.0
        )
        success_rate = (
            success_count / state["total_requests"]
            if state["total_requests"]
            else 0.0
        )
        return {
            "total_requests": state["total_requests"],
            "total_failures": state["total_failures"],
            "avg_latency_ms": round(avg_latency, 2),
            "success_rate": round(success_rate, 4),
        }

    def reset(self) -> None:
        with self._lock:
            self._state = _MetricsState()
