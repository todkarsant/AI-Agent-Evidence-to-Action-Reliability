from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys

PROJECT1 = Path(__file__).resolve().parents[2] / "external" / "Enterprise-Analytics-Copilot"
sys.path.insert(0, str(PROJECT1))

from app.services.llm import OllamaProvider
from runtime3_ollama import Runtime3OllamaProvider


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        body = json.dumps({
            "model": "llama3.2:1b",
            "message": {"role": "assistant", "content": '{"sql": "SELECT 1"}'},
            "done": True,
            "done_reason": "stop",
            "prompt_eval_count": 7,
            "eval_count": 4,
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


def test_runtime3_inherits_pinned_prompt_methods():
    assert Runtime3OllamaProvider.generate_sql is not OllamaProvider.generate_sql
    assert Runtime3OllamaProvider.summarize is OllamaProvider.summarize


def test_runtime3_nonstreaming_payload_is_bounded():
    captured = {}

    class CaptureHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            captured.update(json.loads(self.rfile.read(length)))
            body = json.dumps({
                "model": "llama3.2:1b",
                "message": {"role": "assistant", "content": json.dumps({"sql": "SELECT 1"})},
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 7,
                "eval_count": 4,
            }).encode() + b"\n"
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), CaptureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        provider = Runtime3OllamaProvider(f"http://{host}:{port}", "llama3.2:1b")
        result = provider.generate_sql("question", "schema")
        assert result.text == "SELECT 1"
        assert captured["options"]["temperature"] == 0
        assert captured["options"]["num_ctx"] == provider.context_length
        assert captured["options"]["num_predict"] == provider.max_output_tokens
        assert captured["stream"] is False
        assert captured["format"] == {
            "type": "object",
            "properties": {"sql": {"type": "string", "maxLength": 12000}},
            "required": ["sql"],
            "additionalProperties": False,
        }
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_runtime3_accepts_length_terminated_complete_json():
    class LengthCompleteHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            self.rfile.read(length)
            body = json.dumps({
                "model": "llama3.2:1b",
                "message": {"role": "assistant", "content": '{"sql": "SELECT 1"}'},
                "done": True,
                "done_reason": "length",
                "prompt_eval_count": 7,
                "eval_count": 2048,
            }).encode() + b"\n"
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), LengthCompleteHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        provider = Runtime3OllamaProvider(f"http://{host}:{port}", "llama3.2:1b")
        result = provider._chat("return JSON")
        assert result.text == '{"sql": "SELECT 1"}'
        assert result.output_tokens == 2048
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_runtime3_rejects_length_terminated_incomplete_json():
    class LengthHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            self.rfile.read(length)
            body = json.dumps({
                "model": "llama3.2:1b",
                "message": {"role": "assistant", "content": '{"sql": "SELECT 1"'},
                "done": True,
                "done_reason": "length",
                "prompt_eval_count": 7,
                "eval_count": 2048,
            }).encode() + b"\n"
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), LengthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        provider = Runtime3OllamaProvider(f"http://{host}:{port}", "llama3.2:1b")
        try:
            provider._chat("return JSON")
        except RuntimeError as exc:
            assert "complete JSON object" in str(exc)
        else:
            raise AssertionError("length-terminated incomplete generation was accepted")
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_runtime3_nonstreaming_transport():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        provider = Runtime3OllamaProvider(
            f"http://{host}:{port}",
            "llama3.2:1b",
        )
        result = provider._chat("return JSON")
        assert result.text == '{"sql": "SELECT 1"}'
        assert result.input_tokens == 7
        assert result.output_tokens == 4
        assert result.model == "llama3.2:1b"
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_runtime3_retries_incomplete_length_generation_and_accepts_complete_retry():
    calls = {"count": 0}

    class RetryHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            calls["count"] += 1
            length = int(self.headers.get("Content-Length", "0"))
            self.rfile.read(length)
            if calls["count"] == 1:
                content = '{"sql": "SELECT 1"'
                reason = "length"
            else:
                content = '{"sql": "SELECT 1"}'
                reason = "length"
            body = (json.dumps({
                "model": "llama3.2:1b",
                "message": {"role": "assistant", "content": content},
                "done": True,
                "done_reason": reason,
                "prompt_eval_count": 7,
                "eval_count": 2048,
            }) + "\n").encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), RetryHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        provider = Runtime3OllamaProvider(f"http://{host}:{port}", "llama3.2:1b")
        result = provider._chat("return JSON")
        assert result.text == '{"sql": "SELECT 1"}'
        assert calls["count"] == 2
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_runtime3_uses_higher_configured_ceiling_on_retry():
    calls = []

    class CeilingHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            calls.append(payload["options"]["num_predict"])
            content = '{"sql": "SELECT 1"' if len(calls) == 1 else '{"sql": "SELECT 1"}'
            body = (json.dumps({
                "model": "llama3.2:1b",
                "message": {"role": "assistant", "content": content},
                "done": True,
                "done_reason": "length",
                "prompt_eval_count": 7,
                "eval_count": payload["options"]["num_predict"],
            }) + "\n").encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), CeilingHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        import os
        os.environ["RUNTIME3_OLLAMA_RETRY_OUTPUT_TOKENS"] = "8192"
        provider = Runtime3OllamaProvider(f"http://{host}:{port}", "llama3.2:1b")
        result = provider._chat("return JSON")
        assert result.text == '{"sql": "SELECT 1"}'
        assert calls == [provider.max_output_tokens, 8192]
    finally:
        os.environ.pop("RUNTIME3_OLLAMA_RETRY_OUTPUT_TOKENS", None)
        server.shutdown()
        thread.join(timeout=2)


def test_runtime3_fails_closed_after_bounded_incomplete_length_retries():
    calls = {"count": 0}

    class ExhaustHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            calls["count"] += 1
            length = int(self.headers.get("Content-Length", "0"))
            self.rfile.read(length)
            body = (json.dumps({
                "model": "llama3.2:1b",
                "message": {"role": "assistant", "content": '{"sql": "SELECT 1"'},
                "done": True,
                "done_reason": "length",
                "prompt_eval_count": 7,
                "eval_count": 2048,
            }) + "\n").encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), ExhaustHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        provider = Runtime3OllamaProvider(f"http://{host}:{port}", "llama3.2:1b")
        try:
            provider._chat("return JSON")
        except RuntimeError as exc:
            assert "complete JSON object" in str(exc)
        else:
            raise AssertionError("bounded incomplete generation was accepted")
        assert calls["count"] == 2
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_runtime3_rejects_retry_ceiling_above_context_window():
    import os
    old_context = os.environ.get("RUNTIME3_OLLAMA_CONTEXT_LENGTH")
    old_retry = os.environ.get("RUNTIME3_OLLAMA_RETRY_OUTPUT_TOKENS")
    os.environ["RUNTIME3_OLLAMA_CONTEXT_LENGTH"] = "4096"
    os.environ["RUNTIME3_OLLAMA_RETRY_OUTPUT_TOKENS"] = "8192"
    try:
        try:
            Runtime3OllamaProvider("http://127.0.0.1:11434", "llama3.2:1b")
        except ValueError as exc:
            assert "CONTEXT_LENGTH" in str(exc)
        else:
            raise AssertionError("context window must bound the retry output ceiling")
    finally:
        if old_context is None:
            os.environ.pop("RUNTIME3_OLLAMA_CONTEXT_LENGTH", None)
        else:
            os.environ["RUNTIME3_OLLAMA_CONTEXT_LENGTH"] = old_context
        if old_retry is None:
            os.environ.pop("RUNTIME3_OLLAMA_RETRY_OUTPUT_TOKENS", None)
        else:
            os.environ["RUNTIME3_OLLAMA_RETRY_OUTPUT_TOKENS"] = old_retry


def test_runtime3_pathological_sql_detector_flags_repeated_nested_pattern():
    sql = (
        "SELECT DISTINCT Studio FROM film WHERE Film_ID IN ( "
        "SELECT Film_ID FROM film WHERE Studio NOT IN ( "
        "SELECT Studio FROM film WHERE Film_ID IN ( "
        "SELECT Film_ID FROM film WHERE Studio NOT IN ( "
        "SELECT Studio FROM film WHERE Film_ID IN ( "
        "SELECT Film_ID FROM film WHERE Studio NOT IN ( "
    )
    assert Runtime3OllamaProvider._has_pathological_sql_repetition(sql) is True


def test_runtime3_pathological_sql_detector_does_not_flag_normal_group_by():
    sql = "SELECT Studio FROM film GROUP BY Studio HAVING COUNT(*) >= 2 ORDER BY Studio"
    assert Runtime3OllamaProvider._has_pathological_sql_repetition(sql) is False


def test_runtime3_pathological_repair_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("RUNTIME3_ENABLE_PATHOLOGICAL_SQL_REPAIR", raising=False)
    provider = Runtime3OllamaProvider("http://127.0.0.1:11434", "llama3.2:1b")
    assert provider._has_pathological_sql_repetition(
        "SELECT DISTINCT Studio FROM film WHERE Film_ID IN ( SELECT Film_ID FROM film WHERE Studio NOT IN ( "
        "SELECT Studio FROM film WHERE Film_ID IN ( SELECT Film_ID FROM film WHERE Studio NOT IN ( "
        "SELECT Studio FROM film WHERE Film_ID IN ( SELECT Film_ID FROM film WHERE Studio NOT IN ( "
    ) is True
