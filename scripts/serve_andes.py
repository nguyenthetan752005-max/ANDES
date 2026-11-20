#!/usr/bin/env python3
"""serve_andes.py — phục vụ web-UI Andes (tĩnh) + proxy /andes-help -> help server.

Dùng:
    python3 serve_andes.py [webui_dir] [upstream] [port]

Mặc định:
    webui_dir = ~/andes-stable/web-UI
    upstream  = http://127.0.0.1:8080/help
    port      = 8000
"""
import http.server
import socketserver
import urllib.request
import os
import sys

HOME = os.path.expanduser("~")
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HOME, "andes-stable", "web-UI")
UPSTREAM = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8080/help"
PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
BIND = "127.0.0.1"  # chỉ localhost; đổi "0.0.0.0" nếu muốn truy cập từ máy khác


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_POST(self):
        if self.path.startswith("/andes-help"):
            n = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(n)
            req = urllib.request.Request(
                UPSTREAM, data=body,
                headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req) as r:
                    data = r.read()
                self.send_response(200)
            except Exception:
                data = b'{"jsonrpc":"2.0","error":{"code":-32000,"message":"help unreachable"}}'
                self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):
        pass


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


with Server((BIND, PORT), Handler) as s:
    print(f"ANDES-WEBUI-READY http://{BIND}:{PORT}/  root={ROOT}", flush=True)
    s.serve_forever()
