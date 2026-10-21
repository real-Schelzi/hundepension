"""Lokaler Vorschau-Server: liefert die Website aus und nimmt Formular-Sendungen testweise an.

    python tools/dev_server.py [port] [--fail]

POST /api/anfrage.php wird nicht verschickt, sondern in tools/formular-test.log geschrieben und mit
{"ok": true} beantwortet. Mit --fail antwortet der Server mit einem Fehler (zum Testen des Ausweichwegs).
Unbekannte Pfade liefern 404.html.
"""
import email.parser
import email.policy
import functools
import http.server
import json
import pathlib
import sys
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "tools" / "formular-test.log"
FAIL = "--fail" in sys.argv
PORT = next((int(a) for a in sys.argv[1:] if a.isdigit()), 8780)


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".webp": "image/webp", ".woff2": "font/woff2", ".webmanifest": "application/manifest+json",
                      ".js": "text/javascript", ".css": "text/css"}

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        page = ROOT / "404.html"
        if code == 404 and page.exists():
            body = page.read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().send_error(code, message, explain)

    def do_POST(self):
        if self.path.split("?")[0] != "/api/anfrage.php":
            return self.send_error(405)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        msg = email.parser.BytesParser(policy=email.policy.default).parsebytes(
            b"Content-Type: " + self.headers.get("Content-Type", "").encode() + b"\r\n\r\n" + raw)
        fields = {}
        if msg.is_multipart():
            for part in msg.iter_parts():
                name = part.get_param("name", header="content-disposition")
                payload = part.get_payload(decode=True) or b""
                fields.setdefault(name, []).append(payload.decode("utf-8", "replace").strip())
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"\n=== {datetime.now():%Y-%m-%d %H:%M:%S} ===\n")
            for k, v in fields.items():
                f.write(f"{k}: {', '.join(v)}\n")
        status, data = (503, {"ok": False, "error": "Testmodus: Versand absichtlich fehlgeschlagen"}) if FAIL else (200, {"ok": True})
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    handler = functools.partial(Handler, directory=str(ROOT))
    with http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler) as httpd:
        print(f"Vorschau: http://localhost:{PORT}  ({'Fehlermodus' if FAIL else 'Formulare werden in tools/formular-test.log protokolliert'})")
        httpd.serve_forever()
