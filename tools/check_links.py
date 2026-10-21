"""Prüft alle internen Links, Bilder (src/srcset), Skripte, Stylesheets und Anker der erzeugten Seiten.

Aufruf (im Projektordner):  python tools/check_links.py
"""
import pathlib
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {"_original", "tools", "node_modules"}


class Collect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for k in ("href", "src", "data-srcset", "srcset"):
            v = a.get(k)
            if not v:
                continue
            if "srcset" in k:
                self.refs += [p.strip().split(" ")[0] for p in v.split(",") if p.strip()]
            else:
                self.refs.append(v)


def target(path):
    p = unquote(path)
    f = ROOT / p.lstrip("/")
    if p.endswith("/"):
        f = f / "index.html"
    return f


pages = [p for p in ROOT.rglob("*.html") if not (set(p.relative_to(ROOT).parts) & SKIP)]
ids = {}
refs = {}
for page in pages:
    c = Collect()
    c.feed(page.read_text(encoding="utf-8"))
    url = "/" + page.relative_to(ROOT).as_posix().replace("index.html", "")
    ids[url] = c.ids
    refs[url] = c.refs

errors, external = [], set()
for url, rs in refs.items():
    for r in rs:
        if r.startswith(("tel:", "mailto:", "sms:", "data:", "javascript:")):
            continue
        if r.startswith("http"):
            external.add(r)
            continue
        parts = urlsplit(r)
        path = parts.path or url
        if not path.startswith("/"):
            path = url.rsplit("/", 1)[0] + "/" + path
        f = target(path)
        if not f.exists():
            errors.append(f"{url}: fehlt {r}")
            continue
        if parts.fragment and f.suffix == ".html":
            turl = "/" + f.relative_to(ROOT).as_posix().replace("index.html", "")
            if parts.fragment not in ids.get(turl, set()):
                errors.append(f"{url}: Anker fehlt {r}")

print(f"{len(pages)} Seiten, {sum(len(v) for v in refs.values())} Verweise geprüft")
print("Externe Links:", *sorted(external), sep="\n  ")
if errors:
    print("FEHLER:", *errors, sep="\n  ")
    sys.exit(1)
print("Keine defekten internen Verweise.")
