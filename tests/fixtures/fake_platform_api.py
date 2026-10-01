"""A tiny fake third-party API for testing generated platform MCP servers. Usage: fake_platform_api.py PORT.
Requires "Authorization: Bearer test-token" on every request (401 otherwise); serves GET /things, GET /things/{id}, POST /things.
Listens on 127.0.0.1 only and keeps nothing; for CI and local tests, never real data.
"""
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer


class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        raw = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)

    def _auth(self):
        if self.headers.get("Authorization") != "Bearer test-token":
            self._send(401, {"error": "unauthorized"}); return False
        return True

    def do_GET(self):
        if not self._auth(): return
        path = self.path.split("?")[0]
        if path == "/things":
            self._send(200, {"things": [{"id": "a"}, {"id": "b"}], "query": self.path})
        elif path.startswith("/things/"):
            self._send(200, {"id": path.split("/")[-1], "query": self.path})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if not self._auth(): return
        body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        self._send(201, {"created": json.loads(body or "{}")})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
