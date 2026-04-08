#!/usr/bin/env python3
"""Live-reload dev server for Providence Finance Hub."""
import os, time, threading, hashlib, queue, json
import urllib.request, urllib.error
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

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

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/lead":
            try:
                length = int(self.headers.get("Content-Length", 0))
                lead = json.loads(self.rfile.read(length))
                tag = "QUALIFIED" if lead.get("qualified") else "FOLLOW UP"
                print(f"\n  {'='*48}")
                print(f"  [{tag}] New lead from Providence AI")
                print(f"  Name   : {lead.get('name','—')}")
                print(f"  Email  : {lead.get('email','—')}")
                print(f"  Phone  : {lead.get('phone','—')}")
                print(f"  Time   : {lead.get('ts','—')}")
                print(f"  {'='*48}\n")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
            return

        if self.path == "/api/chat":
            try:
                length = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(length))

                # Split system message out (Anthropic requires it separately)
                system, messages = "", []
                for m in payload.get("messages", []):
                    if m["role"] == "system":
                        system = m["content"]
                    else:
                        messages.append(m)

                anthropic_payload = {
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": payload.get("max_tokens", 512),
                    "system": system,
                    "messages": messages,
                }
                req = urllib.request.Request(
                    "https://api.anthropic.com/v1/messages",
                    data=json.dumps(anthropic_payload).encode(),
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": ANTHROPIC_API_KEY,
                        "anthropic-version": "2023-06-01",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req) as resp:
                    result = json.loads(resp.read())

                # Return OpenAI-compatible shape so browser JS needs no changes
                text = result["content"][0]["text"]
                response = {"choices": [{"message": {"role": "assistant", "content": text}}]}
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except urllib.error.HTTPError as e:
                err = e.read()
                self.send_response(e.code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(err)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": {"message": str(e)}}).encode())
            return
        self.send_response(404)
        self.end_headers()

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
    ThreadingHTTPServer(("", PORT), Handler).serve_forever()
