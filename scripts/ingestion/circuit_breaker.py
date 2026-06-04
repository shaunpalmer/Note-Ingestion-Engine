"""
circuit_breaker.py
Purpose: Circuit breaker for Ollama API calls.
Uses tenacity for retry logic and custom state tracking for circuit state.
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Callable, TypeVar

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .signals import circuit_breaker_opened, circuit_breaker_closed


T = TypeVar("T")


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation, requests pass through
    OPEN = "open"          # Failure threshold exceeded, rejecting requests
    HALF_OPEN = "half_open"  # Testing if the service has recovered


class OllamaUnavailableError(Exception):
    """Raised when Ollama is not reachable or returns a service error."""
    pass


class CircuitBreaker:
    """Circuit breaker for external service calls.

    After `failure_threshold` consecutive failures, the circuit opens
    for `recovery_timeout` seconds. After that, it enters half-open state
    and allows one test request. If that succeeds, the circuit closes.
    If it fails, the circuit opens again.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 1,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._half_open_calls = 0

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if self._last_failure_time and (time.time() - self._last_failure_time) >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
        return self._state

    def call(self, fn: Callable[[], T]) -> T:
        """Execute a function through the circuit breaker."""
        current_state = self.state

        if current_state == CircuitState.OPEN:
            raise OllamaUnavailableError(
                f"Circuit breaker OPEN. Ollama unavailable. "
                f"Retry after {self.recovery_timeout}s."
            )

        if current_state == CircuitState.HALF_OPEN:
            if self._half_open_calls >= self.half_open_max_calls:
                raise OllamaUnavailableError(
                    "Circuit breaker HALF_OPEN: test call limit reached."
                )
            self._half_open_calls += 1

        try:
            result = fn()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Reset counters on successful call."""
        self._failure_count = 0
        self._last_failure_time = None
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
            circuit_breaker_closed.send(self)
        # Already CLOSED: nothing to do

    def _on_failure(self) -> None:
        """Increment failure counter and possibly open the circuit."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._failure_count >= self.failure_threshold:
            if self._state != CircuitState.OPEN:
                self._state = CircuitState.OPEN
                circuit_breaker_opened.send(
                    self,
                    failure_count=self._failure_count,
                    last_failure_time=self._last_failure_time,
                )


# ---------------------------------------------------------------------------
# Decorator for automatic retry with circuit breaker
# ---------------------------------------------------------------------------

def with_retry_and_circuit_breaker(
    breaker: CircuitBreaker,
    max_attempts: int = 3,
    min_wait: float = 4.0,
    max_wait: float = 10.0,
) -> Callable:
    """Decorator combining tenacity retry with circuit breaker."""

    def decorator(fn: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            retry=retry_if_exception_type(OllamaUnavailableError),
            reraise=True,
        )
        def wrapper(*args, **kwargs):
            return breaker.call(lambda: fn(*args, **kwargs))
        return wrapper
    return decorator


# Global circuit breaker instance for Ollama
ollama_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=300.0,  # 5 minutes recovery
)
