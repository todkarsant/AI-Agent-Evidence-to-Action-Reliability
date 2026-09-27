"""Transport-only Ollama hardening for the frozen P2-C1.4 runtime.

The class subclasses the pinned Project 1 OllamaProvider so its generate_sql()
and summarize() methods, including their exact prompts and JSON handling, remain
owned by the pinned Project 1 commit. Only the HTTP transport implementation is
overridden.
"""

from __future__ import annotations

import contextvars
import json
import os
import time

import httpx

from app.services.llm import OllamaProvider, LLMResult


_ACTIVE_RESPONSE_SCHEMA = contextvars.ContextVar("runtime3_active_response_schema", default=None)


class Runtime3OllamaProvider(OllamaProvider):
    """Pinned Project 1 OllamaProvider with streaming HTTP transport and SQL-schema output control."""

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
        self.retry_output_tokens = int(os.getenv("RUNTIME3_OLLAMA_RETRY_OUTPUT_TOKENS", str(self.max_output_tokens)))

        # Frozen Project1 generate_sql() returns exactly one JSON object with one string field: sql.
        # Ollama supports a JSON Schema in format, constraining generation without changing the Project1 prompt.
        self.response_schema = {
            "type": "object",
            "properties": {"sql": {"type": "string", "maxLength": 12000}},
            "required": ["sql"],
            "additionalProperties": False,
        }

        if self.max_attempts < 1:
            raise ValueError("RUNTIME3_OLLAMA_MAX_ATTEMPTS must be >= 1")
        if self.max_output_tokens < 1:
            raise ValueError("RUNTIME3_OLLAMA_MAX_OUTPUT_TOKENS must be >= 1")
        if self.retry_output_tokens < self.max_output_tokens:
            raise ValueError("RUNTIME3_OLLAMA_RETRY_OUTPUT_TOKENS must be >= RUNTIME3_OLLAMA_MAX_OUTPUT_TOKENS")

    @staticmethod
    def _is_complete_json_object(text: str) -> bool:
        """Return True only when the accumulated response is a complete JSON object.

        Ollama can report done_reason="length" even when the streamed content is
        already a complete JSON object. A token-limit condition is therefore not
        sufficient by itself to declare the transport response unusable.
        """
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return False
        return isinstance(value, dict)

    def generate_sql(self, question: str, schema: str, repair_reason: str | None = None) -> LLMResult:
        token = _ACTIVE_RESPONSE_SCHEMA.set(self.response_schema)
        try:
            return super().generate_sql(question, schema, repair_reason=repair_reason)
        finally:
            _ACTIVE_RESPONSE_SCHEMA.reset(token)

    def _chat(self, prompt: str) -> LLMResult:
        # Use the same non-streaming Ollama transport semantics as the pinned
        # Project1 provider. This avoids a separate streaming response-assembly
        # path while preserving the Runtime3 timeout/retry controls.
        base_payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": _ACTIVE_RESPONSE_SCHEMA.get() or "json",
            "options": {"temperature": 0},
        }

        timeout = httpx.Timeout(
            connect=self.connect_timeout,
            read=self.read_timeout,
            write=self.write_timeout,
            pool=self.pool_timeout,
        )

        last_error: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            payload = {
                **base_payload,
                "options": {
                    **base_payload["options"],
                    "num_predict": self.max_output_tokens if attempt == 1 else self.retry_output_tokens,
                },
            }
            try:
                with httpx.Client(timeout=timeout) as client:
                    response = client.post(self.url, json=payload)
                    response.raise_for_status()
                    final_data = response.json()

                message = final_data.get("message") or {}
                text = message.get("content") or ""
                if not text:
                    raise RuntimeError(
                        "Ollama response completed without assistant content"
                    )

                done_reason = final_data.get("done_reason")
                if done_reason == "length":
                    if not self._is_complete_json_object(text):
                        last_error = RuntimeError(
                            "Runtime3 Ollama generation stopped at the configured "
                            "output-token limit before a complete JSON object was produced."
                        )
                        if attempt >= self.max_attempts:
                            break
                        time.sleep(self.retry_backoff_seconds * attempt)
                        continue
                elif done_reason not in (None, "stop"):
                    raise RuntimeError(
                        f"Runtime3 Ollama generation ended with unexpected done_reason={done_reason!r}"
                    )

                return LLMResult(
                    text=text,
                    input_tokens=int(final_data.get("prompt_eval_count") or 0),
                    output_tokens=int(final_data.get("eval_count") or 0),
                    model=final_data.get("model", self.model),
                )

            except (
                httpx.TimeoutException,
                httpx.NetworkError,
                httpx.RemoteProtocolError,
                httpx.HTTPStatusError,
                json.JSONDecodeError,
            ) as exc:
                last_error = exc
                if attempt >= self.max_attempts:
                    break
                time.sleep(self.retry_backoff_seconds * attempt)

        raise RuntimeError(
            f"Runtime3 Ollama transport failed after {self.max_attempts} attempt(s): {last_error}"
        ) from last_error
