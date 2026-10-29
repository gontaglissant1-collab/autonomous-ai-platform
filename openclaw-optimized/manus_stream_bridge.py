#!/usr/bin/env python3
import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

UPSTREAM = os.environ.get("OPENAI_API_BASE", "").rstrip("/")
UPSTREAM_KEY = os.environ.get("OPENAI_API_KEY", "")
HOST = "127.0.0.1"
PORT = 19090
LOG_PATH = "/tmp/manus-stream-bridge.log"
ALLOWED_MODELS = {
    "gpt-6-luna": ("Manus LLM bridge", 272000),
    "gpt-6-sol": ("Manus LLM fallback", 272000),
    "gpt-6.1-sol": ("Manus LLM fallback 2", 272000),
    "gpt-5.5": ("Manus LLM economical fallback", 200000),
    "gpt-5-mini": ("Manus LLM fast fallback", 128000),
}

if not UPSTREAM or not UPSTREAM_KEY:
    raise SystemExit("OPENAI_API_BASE and OPENAI_API_KEY are required")

def log_event(event, **fields):
    safe = {"event": event, **fields}
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(safe, ensure_ascii=False, separators=(",", ":")) + "\n")
    except Exception:
        pass

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def log_message(self, fmt, *args):
        pass

    def _json(self, status, payload):
        data = json.dumps(payload, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.rstrip("/") == "/v1/models":
            rows = [{"id": k, "object": "model", "owned_by": "manus"} for k in ALLOWED_MODELS]
            self._json(200, {"object": "list", "data": rows})
            return
        self._json(404, {"error": {"message": "not found", "type": "invalid_request_error"}})

    def do_POST(self):
        if self.path.rstrip("/") != "/v1/chat/completions":
            self._json(404, {"error": {"message": "not found", "type": "invalid_request_error"}})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length) or b"{}")
            requested_model = str(body.get("model") or "gpt-6-luna")
            model = requested_model if requested_model in ALLOWED_MODELS else "gpt-6-luna"
            original_keys = sorted(body.keys())
            tools = body.get("tools") or []
            log_event("request", keys=original_keys, tool_count=len(tools), message_count=len(body.get("messages") or []), model=model)
            body["stream"] = False
            body["model"] = model
            req = Request(
                UPSTREAM + "/chat/completions",
                data=json.dumps(body).encode(),
                headers={"Authorization": "Bearer " + UPSTREAM_KEY, "Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urlopen(req, timeout=120) as response:
                    raw = response.read()
                    status = response.status
            except HTTPError as exc:
                raw = exc.read(4000)
                status = exc.code
                log_event("upstream_http_error", status=status, body=raw.decode(errors="replace")[:1000], keys=original_keys, tool_count=len(tools), model=model)
                self._json(502, {"error": {"message": "upstream model rejected request", "type": "upstream_error", "status": status}})
                return
            result = json.loads(raw)
            if "error" in result:
                log_event("upstream_error_json", status=status, error_type=result.get("error", {}).get("type"), keys=original_keys, tool_count=len(tools), model=model)
                self._json(502, {"error": {"message": "upstream model returned an error", "type": "upstream_error"}})
                return
            choice = (result.get("choices") or [{}])[0]
            message = choice.get("message") or {}
            content = message.get("content") or ""
            tool_calls = message.get("tool_calls") or []
            chunk_id = result.get("id") or ("chatcmpl-" + uuid.uuid4().hex)
            created = result.get("created") or int(time.time())
            log_event("upstream_ok", status=status, content_chars=len(content), returned_tool_calls=len(tool_calls), finish_reason=choice.get("finish_reason"), keys=original_keys, tool_count=len(tools), model=model)
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()
            def emit(delta, finish=None):
                payload = {"id": chunk_id, "object": "chat.completion.chunk", "created": created, "model": model, "choices": [{"index": 0, "delta": delta, "finish_reason": finish}]}
                self.wfile.write(("data: " + json.dumps(payload, separators=(",", ":")) + "\n\n").encode())
                self.wfile.flush()
            emit({"role": "assistant"})
            if content:
                emit({"content": content})
            if tool_calls:
                streamed_calls = []
                for index, call in enumerate(tool_calls):
                    function = call.get("function") or {}
                    streamed_calls.append({
                        "index": index,
                        "id": call.get("id") or ("call_" + uuid.uuid4().hex),
                        "type": call.get("type") or "function",
                        "function": {
                            "name": function.get("name") or "",
                            "arguments": function.get("arguments") or "{}",
                        },
                    })
                emit({"tool_calls": streamed_calls}, "tool_calls")
            else:
                emit({}, choice.get("finish_reason") or "stop")
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
            self.close_connection = True
        except Exception as exc:
            log_event("bridge_exception", error_type=type(exc).__name__, error=str(exc)[:300])
            try:
                self._json(502, {"error": {"message": "bridge upstream failure", "type": "upstream_error"}})
            except Exception:
                pass

ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
