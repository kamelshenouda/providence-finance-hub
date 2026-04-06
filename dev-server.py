#!/usr/bin/env python3
"""Live-reload dev server for Providence Finance Hub."""
import os, time, threading, hashlib, queue
from http.server import HTTPServer, SimpleHTTPRequestHandler

WATCH_FILE = "index.html"
PORT = 4321
clients = []
last_hash = None

def file_hash():
    try:
        with open(WATCH_FILE, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def watcher():
    global last_hash
    last_hash = file_hash()
    while True:
        time.sleep(0.4)
        h = file_hash()
        if h and h != last_hash:
            last_hash = h
            print(f"  ↺  index.html changed — reloading browser...")
            for q in list(clients):
                try:
                    q.put("reload")
                except:
                    pass

LIVERELOAD_SNIPPET = b"""
<script>
(function(){
  const es = new EventSource('/__livereload__');
  es.onmessage = () => location.reload();
})();
</script>
"""

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        if self.path == "/__livereload__":
            q = queue.Queue()
            clients.append(q)
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            try:
                while True:
                    try:
                        q.get(timeout=25)
                        self.wfile.write(b"data: reload\n\n")
                        self.wfile.flush()
                    except:
                        self.wfile.write(b": ping\n\n")
                        self.wfile.flush()
            except:
                if q in clients:
                    clients.remove(q)
            return

        if self.path in ("/", "/index.html"):
            try:
                with open(WATCH_FILE, "rb") as f:
                    content = f.read()
                content = content.replace(b"</body>", LIVERELOAD_SNIPPET + b"</body>", 1)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            except:
                pass

        super().do_GET()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    threading.Thread(target=watcher, daemon=True).start()
    print(f"\n  Providence Finance Hub — dev server")
    print(f"  http://localhost:{PORT}\n")
    HTTPServer(("", PORT), Handler).serve_forever()
