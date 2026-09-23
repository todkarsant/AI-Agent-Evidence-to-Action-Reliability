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
        events = [
            {"model": "llama3.2:1b", "message": {"role": "assistant", "content": "{\"sql\""}, "done": False},
            {"model": "llama3.2:1b", "message": {"role": "assistant", "content": ": \"SELECT 1\""}, "done": False},
            {"model": "llama3.2:1b", "message": {"role": "assistant", "content": "}"}, "done": False},
            {
                "model": "llama3.2:1b",
                "message": {"role": "assistant", "content": ""},
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 7,
                "eval_count": 4,
            },
        ]
        body = "".join(json.dumps(e) + "\n" for e in events).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def log_message(self, *_):
        pass


def test_runtime3_inherits_pinned_prompt_methods():
    assert Runtime3OllamaProvider.generate_sql is OllamaProvider.generate_sql
    assert Runtime3OllamaProvider.summarize is OllamaProvider.summarize


def test_runtime3_streaming_payload_is_bounded():
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
        provider._chat("return JSON")
        assert captured["options"]["temperature"] == 0
        assert captured["options"]["num_predict"] == 2048
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_runtime3_rejects_length_terminated_generation():
    class LengthHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            self.rfile.read(length)
            body = json.dumps({
                "model": "llama3.2:1b",
                "message": {"role": "assistant", "content": json.dumps({"sql": "SELECT 1"})},
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
            assert "output-token limit" in str(exc)
        else:
            raise AssertionError("length-terminated generation was accepted")
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_runtime3_streaming_transport():
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
