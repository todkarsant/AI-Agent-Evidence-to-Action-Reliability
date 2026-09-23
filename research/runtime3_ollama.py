"""Runtime3-only Ollama transport hardening.

This module deliberately does not change the scientific prompt, model, temperature,
or LLMResult contract used by the pinned Project 1 research code. It changes only
HTTP response handling: Ollama /api/chat is consumed as its documented NDJSON
stream so a long-running generation is not represented as one silent non-streaming
HTTP response.

Retries are allowed only before any assistant content has been received. Once
content has arrived, the request is never replayed, avoiding duplicate/ambiguous
partial generations.
"""

from __future__ import annotations

import json
import os
import time

import httpx

from app.services.llm import LLMProvider, LLMResult, _extract_json_object


class Runtime3OllamaProvider(LLMProvider):
    """Transport-only Ollama provider for the frozen Runtime3 protocol."""

    def __init__(self, base_url: str, model: str):
        self.url = base_url.rstrip("/") + "/api/chat"
        self.model = model

        # These are transport controls only. They do not alter model/prompt
        # semantics. Read timeout applies to inactivity between streamed chunks,
        # not to the total generation duration.
        self.connect_timeout = float(os.getenv("RUNTIME3_OLLAMA_CONNECT_TIMEOUT_SECONDS", "30"))
        self.read_timeout = float(os.getenv("RUNTIME3_OLLAMA_READ_TIMEOUT_SECONDS", "600"))
        self.write_timeout = float(os.getenv("RUNTIME3_OLLAMA_WRITE_TIMEOUT_SECONDS", "30"))
        self.pool_timeout = float(os.getenv("RUNTIME3_OLLAMA_POOL_TIMEOUT_SECONDS", "30"))
        self.max_attempts = int(os.getenv("RUNTIME3_OLLAMA_MAX_ATTEMPTS", "3"))
        self.retry_backoff_seconds = float(os.getenv("RUNTIME3_OLLAMA_RETRY_BACKOFF_SECONDS", "2"))

        if self.max_attempts < 1:
            raise ValueError("RUNTIME3_OLLAMA_MAX_ATTEMPTS must be >= 1")

    def _chat(self, prompt: str) -> LLMResult:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
            "format": "json",
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
            parts: list[str] = []
            final_data: dict = {}

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
                                break

                text = "".join(parts)
                if not text:
                    raise RuntimeError("Ollama stream completed without assistant content")

                return LLMResult(
                    text=text,
                    input_tokens=int(final_data.get("prompt_eval_count") or 0),
                    output_tokens=int(final_data.get("eval_count") or 0),
                    model=final_data.get("model", self.model),
                )

            except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError, json.JSONDecodeError) as exc:
                last_error = exc

                # Never replay a request after receiving assistant content.
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

    def generate_sql(self, question: str, schema: str, repair_reason: str | None = None) -> LLMResult:
        repair = f"Previous validation error: {repair_reason}\nFix it." if repair_reason else ""
        prompt = f"""You are a senior analytics SQL engineer generating SQLite SQL for a production analytics system.
Generate exactly one read-only SELECT statement.

Rules:
1. Use only the supplied schema and its columns.
2. Never mutate data; no INSERT, UPDATE, DELETE, DDL, PRAGMA, or multiple statements.
3. Return ONLY a JSON object with exactly one key: sql.
4. The sql value must be a valid SQLite SELECT statement.
5. For relative dates such as last month, use the latest date available in the dataset as the reference point, not the current calendar date.
6. week_start is stored as ISO text YYYY-MM-DD.
7. For the previous complete month, use SQLite expressions such as date((SELECT MAX(week_start) FROM store_week), 'start of month', '-1 month').
8. The current dataset has one analytical table: store_week. Prefer a direct aggregation over this table.
9. Do NOT self-join store_week. Do NOT create derived-table aliases such as T1/T2 unless the supplied schema explicitly requires a multi-table join.
10. For "highest sales", "top stores by sales", or equivalent, use SUM(sales), GROUP BY store_id, ORDER BY the aggregate alias DESC, and LIMIT 10.
11. Do not reference a table alias that is not defined in the same SELECT.
12. Do not put explanations or markdown in the response.

{repair}
Schema:
{schema}
Question:
{question}"""
        result = self._chat(prompt)
        obj = _extract_json_object(result.text)
        result.text = obj["sql"]
        return result

    def summarize(self, question: str, columns: list[str], rows: list[list]) -> LLMResult:
        prompt = f"""Answer using only the supplied SQL result. Do not invent facts. Return JSON {{"answer": "..."}}.
Question: {question}
Columns: {columns}
Rows: {rows}"""
        result = self._chat(prompt)
        obj = _extract_json_object(result.text)
        result.text = obj["answer"]
        return result
