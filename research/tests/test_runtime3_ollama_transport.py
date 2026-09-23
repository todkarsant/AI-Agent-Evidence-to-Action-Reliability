from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys

PROJECT1 = Path(__file__).resolve().parents[2] / "external" / "Enterprise-Analytics-Copilot"
sys.path.insert(0, str(PROJECT1))

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
