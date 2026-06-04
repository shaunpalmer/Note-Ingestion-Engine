"""
ollama_client.py
Purpose: Ollama API client with circuit breaker, retry, and structured logging.
Uses tenacity for retries and the circuit breaker for health management.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import structlog

from .circuit_breaker import (
    OllamaUnavailableError,
    ollama_circuit_breaker,
    with_retry_and_circuit_breaker,
)
from .config import get_ollama_config
from .signals import ollama_failed, ollama_responded

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Ollama Client
# ---------------------------------------------------------------------------

class OllamaClient:
    """Client for Ollama API with resilience patterns built in."""

    def __init__(self) -> None:
        cfg = get_ollama_config()
        self.host = cfg["host"]
        self.model = cfg["model"]
        self.fallback_model = cfg["fallback"]
        self._circuit_breaker = ollama_circuit_breaker

    def is_healthy(self) -> bool:
        """Quick health check without circuit breaker."""
        try:
            result = subprocess.run(
                ["curl", "-sf", f"{self.host}/api/tags"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    @with_retry_and_circuit_breaker(
        breaker=ollama_circuit_breaker,
        max_attempts=3,
        min_wait=4.0,
        max_wait=10.0,
    )
    def generate(self, prompt: str, model: str | None = None, timeout: int = 120) -> str:
        """Send a prompt to Ollama with full resilience stack."""
        model = model or self.model
        payload = json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "3h",
        })

        start_time = time.time()
        logger.info("ollama.request", model=model, prompt_length=len(prompt))

        try:
            result = subprocess.run(
                ["curl", "-sf", f"{self.host}/api/generate", "-d", payload],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            logger.error("ollama.timeout", model=model, timeout=timeout)
            raise OllamaUnavailableError(f"Ollama request timed out after {timeout}s")

        if result.returncode != 0:
            logger.error("ollama.curl_failed", stderr=result.stderr[:200])
            raise OllamaUnavailableError(f"curl failed: {result.stderr[:200]}")

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            logger.error("ollama.invalid_json", response=result.stdout[:200])
            raise OllamaUnavailableError("Ollama returned invalid JSON")

        response_text = data.get("response", "")
        elapsed_ms = int((time.time() - start_time) * 1000)

        ollama_responded.send(
            self,
            model=model,
            elapsed_ms=elapsed_ms,
            response_length=len(response_text),
        )
        logger.info("ollama.success", model=model, elapsed_ms=elapsed_ms)

        return response_text

    def generate_with_fallback(self, prompt: str, timeout: int = 120) -> str:
        """Try primary model, fall back to secondary on failure."""
        try:
            return self.generate(prompt, model=self.model, timeout=timeout)
        except OllamaUnavailableError:
            logger.warning("ollama.fallback", primary=self.model, fallback=self.fallback_model)
            try:
                return self.generate(prompt, model=self.fallback_model, timeout=timeout)
            except OllamaUnavailableError:
                ollama_failed.send(self, primary=self.model, fallback=self.fallback_model)
                raise
