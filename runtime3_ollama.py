"""Transport-only Ollama hardening for the frozen P2-C1.4 runtime.

The class subclasses the pinned Project 1 OllamaProvider so its generate_sql()
and summarize() methods, including their exact prompts and JSON handling, remain
owned by the pinned Project 1 commit. Only the HTTP transport implementation is
overridden.
"""

from __future__ import annotations

import json
import os
import time

import httpx

from app.services.llm import OllamaProvider, LLMResult


class Runtime3OllamaProvider(OllamaProvider):
    """Pinned Project 1 OllamaProvider with streaming HTTP transport."""

    def __init__(self, base_url: str, model: str):
        # Keep the parent constructor for the exact provider identity/URL/model
        # contract. The parent timeout is not used by our overridden _chat().
        super().__init__(base_url, model)

        self.connect_timeout = float(os.getenv("RUNTIME3_OLLAMA_CONNECT_TIMEOUT_SECONDS", "30"))
        self.read_timeout = float(os.getenv("RUNTIME3_OLLAMA_READ_TIMEOUT_SECONDS", "600"))
        self.write_timeout = float(os.getenv("RUNTIME3_OLLAMA_WRITE_TIMEOUT_SECONDS", "30"))
        self.pool_timeout = float(os.getenv("RUNTIME3_OLLAMA_POOL_TIMEOUT_SECONDS", "30"))
        self.max_attempts = int(os.getenv("RUNTIME3_OLLAMA_MAX_ATTEMPTS", "2"))
        self.retry_backoff_seconds = float(os.getenv("RUNTIME3_OLLAMA_RETRY_BACKOFF_SECONDS", "2"))
        self.max_output_tokens = int(os.getenv("RUNTIME3_OLLAMA_MAX_OUTPUT_TOKENS", "2048"))

        if self.max_attempts < 1:
            raise ValueError("RUNTIME3_OLLAMA_MAX_ATTEMPTS must be >= 1")
        if self.max_output_tokens < 1:
            raise ValueError("RUNTIME3_OLLAMA_MAX_OUTPUT_TOKENS must be >= 1")

    def _chat(self, prompt: str) -> LLMResult:
        # This payload intentionally matches the pinned Project 1 provider:
        # same endpoint, model, single user message, JSON mode, and temperature=0.
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
            "format": "json",
            "options": {
                "temperature": 0,
                "num_predict": self.max_output_tokens,
            },
        }

        timeout = httpx.Timeout(
            connect=self.connect_timeout,
            read=self.read_timeout,
            write=self.write_timeout,
            pool=self.pool_timeout,
        )

        last_error: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            parts: list[str] = []
            final_data: dict = {}
            done_seen = False

            try:
                with httpx.Client(timeout=timeout) as client:
                    with client.stream("POST", self.url, json=payload) as response:
                        response.raise_for_status()

                        for line in response.iter_lines():
                            if not line:
                                continue
                            event = json.loads(line)
                            message = event.get("message") or {}
                            content = message.get("content") or ""
                            if content:
                                parts.append(content)
                            if event.get("done"):
                                final_data = event
                                done_seen = True
                                break

                if not done_seen:
                    raise RuntimeError("Ollama stream ended before the final done event")

                text = "".join(parts)
                if not text:
                    raise RuntimeError("Ollama stream completed without assistant content")

                done_reason = final_data.get("done_reason")
                if done_reason == "length":
                    raise RuntimeError(
                        "Runtime3 Ollama generation stopped at the configured "
                        "output-token limit before a complete response was produced."
                    )
                if done_reason not in (None, "stop"):
                    raise RuntimeError(
                        f"Runtime3 Ollama generation ended with unexpected done_reason={done_reason!r}"
                    )

                return LLMResult(
                    text=text,
                    input_tokens=int(final_data.get("prompt_eval_count") or 0),
                    output_tokens=int(final_data.get("eval_count") or 0),
                    model=final_data.get("model", self.model),
                )

            except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError, json.JSONDecodeError) as exc:
                last_error = exc

                # A partially received generation is never replayed. This keeps
                # retry behavior deterministic at the request boundary.
                if parts:
                    raise RuntimeError(
                        "Runtime3 Ollama stream failed after assistant content was received; "
                        "request was not retried to avoid ambiguous replay."
                    ) from exc

                if attempt >= self.max_attempts:
                    break

                time.sleep(self.retry_backoff_seconds * attempt)

        raise RuntimeError(
            f"Runtime3 Ollama transport failed after {self.max_attempts} attempt(s): {last_error}"
        ) from last_error
