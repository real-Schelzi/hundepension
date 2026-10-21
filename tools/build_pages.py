"""Erzeugt alle HTML-Seiten, sitemap.xml, robots.txt, 404.html, Manifest und assets/js/site-data.js.

Voraussetzung: `python tools/prepare_images.py` wurde einmal ausgeführt (assets/data/images.json).
Aufruf (im Projektordner):  python tools/build_pages.py
"""
import html
import json
import pathlib
import sys
from datetime import date
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from content import (ADMISSION, ADVENTURE, AGB, ANMELDUNG_AGB, BESONDERHEITEN, CHARAKTER, CONDITIONS,  # noqa: E402
                     DAY, EXTRAS, FACTS, FERIEN, HOURS, HOURS_ROWS, LINKS, NEWS, PARK, PRICES, SCHLAF, SITE,
                     WERDEGANG)

META = json.loads((ROOT / "assets" / "data" / "images.json").read_text(encoding="utf-8"))
IMG = META["images"]
D = SITE["domain"]
VERSION = date.today().strftime("%Y%m%d")
PAGES = []  # (pfad, priorität) für die Sitemap


def esc(s):
    return html.escape(s, quote=True)


# ------------------------------------------------------------------ Bilder
def srcset(key):
    return ", ".join(f"/assets/img/{key}-{w}.webp {w}w" for w in IMG[key]["widths"])


def src(key, pick=960):
    ws = IMG[key]["widths"]
    return f"/assets/img/{key}-{min(ws, key=lambda w: abs(w - pick))}.webp"


def img(key, sizes="100vw", cls="", eager=False, alt=None, pick=960, extra=""):
    e = IMG[key]
    a = e["alt"] if alt is None else alt
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{src(key, pick)}" srcset="{srcset(key)}" sizes="{sizes}" width="{e["w"]}" '
            f'height="{e["h"]}" alt="{esc(a)}" {load} decoding="async"{extra}>')


def lb(key, group, sizes, cls="", attrs="", inner=None, caption=None):
    """Bild, das sich in der Lightbox öffnet."""
    e = IMG[key]
    cap = f' data-caption="{esc(caption)}"' if caption else ""
    body = inner if inner is not None else img(key, sizes)
    return (f'<a class="{cls}" href="/assets/img/{key}-{e["widths"][-1]}.webp" data-lightbox="{group}" '
            f'data-srcset="{srcset(key)}" data-w="{e["w"]}" data-h="{e["h"]}"{cap}{attrs}>{body}'
            f'<span class="sr-only"> – Bild vergrössern</span></a>')


def pola(key, caption=None, rot=0, sizes="(min-width: 900px) 260px, 45vw", cls="", group=None):
    cap = f"<figcaption>{esc(caption)}</figcaption>" if caption else ""
    inner = img(key, sizes)
    if group:
        inner = lb(key, group, sizes, cls="pola__link", caption=caption)
    return f'<figure class="pola {cls}" style="--r:{rot}deg">{inner}{cap}</figure>'


# ------------------------------------------------------------------ Icons (inline SVG, Stroke-Stil)
ICONS = {
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    "pin": '<path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "down": '<path d="M12 5v14M6 13l6 6 6-6"/>',
    "paw": '<circle cx="7" cy="9" r="1.8"/><circle cx="11" cy="6" r="1.8"/><circle cx="15.5" cy="7" r="1.8"/>'
           '<circle cx="18.5" cy="11" r="1.8"/><path d="M9 15.5c0-2.5 2-4.5 4-4.5s4 2 4 4.5c0 1.8-1.4 3-3 3-.8 0-1.4-.3-2-.3s-1.4.6-2.2.3C9.7 18.2 9 17 9 15.5z"/>',
    "leaf": '<path d="M5 19c0-8 5-14 15-14 0 10-6 15-14 15"/><path d="M5 19c3-4 6-7 10-9"/>',
    "tree": '<path d="M12 21v-6"/><path d="M12 3l6 8h-3l4 5H5l4-5H6z"/>',
    "water": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
    "home": '<path d="M4 11l8-7 8 7"/><path d="M6 10v10h12V10"/><path d="M10 20v-5h4v5"/>',
    "bowl": '<path d="M3 12h18a9 9 0 0 1-18 0z"/><path d="M8 8c0-1.5 1-2.5 2-3M14 8c0-1.5 1-2.5 2-3"/>',
    "van": '<path d="M2 7h11v9H2zM13 10h4l3 3v3h-7"/><circle cx="6" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
    "shield": '<path d="M12 3l7 3v5c0 5-3.5 8.5-7 10-3.5-1.5-7-5-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
    "heart": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "download": '<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    "mountain": '<path d="M3 19l6-10 4 6 3-4 5 8z"/>',
    "tunnel": '<path d="M3 19h18"/><path d="M6 19v-4a6 6 0 0 1 12 0v4"/><path d="M10 19v-3a2 2 0 0 1 4 0v3"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "check": '<path d="M5 12l5 5 9-10"/>',
    "external": '<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
}


def icon(name, cls="ico"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICONS[name]}</svg>')


# ------------------------------------------------------------------ Navigation
PRIMARY = [("/angebot/", "Angebot"), ("/unser-zuhause/", "Zuhause"), ("/rudel/", "Rudel"), ("/preise/", "Preise"),
           ("/impressionen/", "Impressionen"), ("/über-mich/", "Über mich")]
MORE = [("/öffnungszeiten/", "Öffnungszeiten"), ("/betriebsferien/", "Betriebsferien"),
        ("/anmeldeformular/", "Anmeldeformular"), ("/news/", "News"), ("/pflegehunde/", "Pflegehunde"),
        ("/agb/", "AGB"), ("/links/", "Links"), ("/kontakt-1/", "Kontakt")]


def nav_link(href, label, current):
    cur = ' aria-current="page"' if href == current else ""
    return f'<li><a href="{href}"{cur}>{label}</a></li>'


def header(current, mode):
    prim = "".join(nav_link(h, l, current) for h, l in PRIMARY)
    more = "".join(nav_link(h, l, current) for h, l in MORE)
    more_active = " is-current" if current in [h for h, _ in MORE] else ""
    return f"""
<a class="skip-link" href="#inhalt">Zum Inhalt springen</a>
<div class="notice" role="note">
  <div class="wrap notice__in"><span class="notice__dot" aria-hidden="true"></span><p><strong>{SITE["notice"]}</strong> <a href="/kontakt-1/">Fragt uns gerne an</a></p></div>
</div>
<header class="hdr hdr--{mode}" data-header>
  <div class="wrap hdr__in">
    <a class="brand" href="/" aria-label="{SITE["name"]} – zur Startseite">
      <img class="brand__badge" src="/assets/img/emblem-badge-360.webp" alt="" width="360" height="360">
      <span class="brand__txt"><span class="brand__name">Hundepension <span>im Park</span></span><span class="brand__tag">{SITE["tagline"]}</span></span>
    </a>
    <nav class="nav" id="hauptmenue" aria-label="Hauptnavigation" data-nav>
      <ul class="nav__list">
        {prim}
        <li class="nav__more{more_active}">
          <button class="nav__more-btn" type="button" aria-expanded="false" aria-controls="mehr-menue" data-more>Mehr<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M3 4.5l3 3 3-3" fill="none" stroke="currentColor" stroke-width="1.5"/></svg></button>
          <ul class="nav__sub" id="mehr-menue">{more}</ul>
        </li>
      </ul>
      <div class="nav__mobile-extra">
        <a class="btn btn--clay" href="/anmeldeformular/">Online anmelden</a>
        <a class="nav__phone" href="tel:{SITE["phone_tel"]}">{icon("phone")}{SITE["phone_display"]}</a>
      </div>
    </nav>
    <div class="hdr__actions">
      <a class="hdr__phone" href="tel:{SITE["phone_tel"]}" aria-label="Anrufen: {SITE["phone_display"]}">{icon("phone")}<span>{SITE["phone_display"]}</span></a>
      <a class="btn btn--clay btn--sm" href="/kontakt-1/">Platz anfragen</a>
      <button class="burger" type="button" aria-expanded="false" aria-controls="hauptmenue" data-burger><span class="sr-only">Menü</span><span class="burger__bars" aria-hidden="true"></span></button>
    </div>
  </div>
</header>"""


def hours_list(cls=""):
    rows = "".join(
        f'<div class="hours__row"><dt>{d}</dt><dd>{a}{"<br>" + b if b else ""}</dd></div>' for d, a, b in HOURS_ROWS)
    return f'<dl class="hours {cls}">{rows}</dl>'


def footer():
    allpages = PRIMARY + [p for p in MORE if p[0] not in ("/agb/",)]
    links = "".join(f'<li><a href="{h}">{l}</a></li>' for h, l in allpages)
    return f"""
<footer class="ftr">
  <div class="ftr__cta">
    <div class="wrap ftr__cta-in">
      <p class="eyebrow eyebrow--light">Kommt vorbei</p>
      <p class="ftr__claim">… und überzeugt euch selbst von unserem liebevoll gestalteten Hundeparadies.</p>
      <div class="ftr__cta-actions">
        <a class="btn btn--cream" href="tel:{SITE["phone_tel"]}">{icon("phone")}{SITE["phone_display"]}</a>
        <a class="btn btn--ghost-light" href="/kontakt-1/">Besichtigung anfragen</a>
      </div>
      <p class="ftr__hint">Besichtigungen Montag bis Freitag – bitte mit Voranmeldung.</p>
    </div>
  </div>
  <div class="wrap ftr__grid">
    <div class="ftr__brand">
      <img src="/assets/img/emblem-badge-360.webp" alt="" width="360" height="360" loading="lazy">
      <p><strong>{SITE["name"]}</strong><br>{SITE["owner"]}<br>{SITE["street"]}<br>{SITE["zip"]} {SITE["city"]}</p>
      <p><a href="tel:{SITE["phone_tel"]}">Natel {SITE["phone_display"]}</a></p>
    </div>
    <div>
      <h2 class="ftr__h">Bring- und Abholzeiten</h2>
      {hours_list("hours--compact")}
      <p class="live live--footer" data-live-status></p>
    </div>
    <nav aria-label="Alle Seiten">
      <h2 class="ftr__h">Seiten</h2>
      <ul class="ftr__links">{links}</ul>
    </nav>
  </div>
  <div class="wrap ftr__base">
    <p>© {date.today().year} {SITE["name"]} · Waltenschwil AG</p>
    <ul><li><a href="/about/">Impressum</a></li><li><a href="/j/privacy/">Datenschutz</a></li><li><a href="/agb/">AGB</a></li></ul>
  </div>
</footer>"""


# ------------------------------------------------------------------ Strukturierte Daten
def business_ld():
    return {
        "@type": "LocalBusiness",
        "@id": f"{D}/#pension",
        "name": SITE["name"],
        "alternateName": "harmony-dog",
        "slogan": SITE["tagline"],
        "description": "Tages- und Ferienbetreuung für Hunde in Waltenschwil AG: 3000 m² sicher eingezäuntes Gelände, "
                       "12 Plätze, Familienanschluss und Rudelleben. Vetamtlich geprüft (Bewilligung-Nr. 25.049).",
        "url": f"{D}/",
        "logo": f"{D}/assets/img/logo-dark.png",
        "image": [f"{D}{src('unser-zuhause-01', 2000)}", f"{D}{src('angebot-01', 1600)}"],
        "telephone": "+41 79 355 68 82",
        "address": {"@type": "PostalAddress", "streetAddress": SITE["street"], "postalCode": SITE["zip"],
                    "addressLocality": SITE["city"], "addressRegion": SITE["canton"], "addressCountry": "CH"},
        "founder": {"@type": "Person", "name": SITE["owner"]},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "06:30", "closes": "08:30"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "16:00", "closes": "18:30"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "08:00", "closes": "08:30"},
        ],
        "priceRange": "CHF 60–80 pro Tag",
        "makesOffer": [
            {"@type": "Offer", "name": p["title"],
             "priceSpecification": {"@type": "UnitPriceSpecification", "price": p["price"], "priceCurrency": "CHF", "unitText": "Tag"}}
            for p in PRICES
        ],
    }


def crumbs_ld(crumbs):
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": D + quote(h)} for i, (h, n) in enumerate(crumbs)]
    return {"@type": "BreadcrumbList", "itemListElement": items}


# ------------------------------------------------------------------ Seitengerüst
def render(path, title, desc, body, *, mode="solid", crumbs=None, ld=None, body_class="", og=None, scripts=(), priority="0.6"):
    PAGES.append((path, priority))
    canonical = D + quote(path)
    graph = list(ld or [])
    if crumbs:
        graph.append(crumbs_ld([("/", "Start")] + crumbs))
    ld_html = ""
    if graph:
        ld_html = ('<script type="application/ld+json">' +
                   json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>")
    og_img = og or "/assets/img/og-hundepension.jpg"
    js = "".join(f'<script src="/assets/js/{s}?v={VERSION}" defer></script>' for s in ("site-data.js", "main.js") + tuple(scripts))
    crumb_html = ""
    if crumbs:
        items = '<li><a href="/">Start</a></li>' + "".join(
            f'<li><a href="{h}" aria-current="page">{n}</a></li>' if i == len(crumbs) - 1 else f'<li><a href="{h}">{n}</a></li>'
            for i, (h, n) in enumerate(crumbs))
        crumb_html = f'<nav class="crumbs wrap" aria-label="Brotkrümelnavigation"><ol>{items}</ol></nav>'
    doc = f"""<!doctype html>
<html lang="de-CH" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{'<meta name="robots" content="noindex">' if path == "/404" else f'<link rel="canonical" href="{canonical}">'}
<meta name="theme-color" content="#24382b">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_CH">
<meta property="og:site_name" content="{SITE["name"]}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{D}{og_img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/icons/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/fraunces.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/figtree.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/main.css?v={VERSION}">
<script>document.documentElement.classList.replace('no-js','js')</script>
{ld_html}
</head>
<body class="{body_class}">
{header(path, mode)}
<main id="inhalt" tabindex="-1">
{crumb_html}
{body}
</main>
{footer()}
{js}
</body>
</html>
"""
    out = ROOT / (path.strip("/") or "") / "index.html" if path != "/404" else ROOT / "404.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print("✓", path)


def phero(eyebrow, title, lead, media=None, cls=""):
    m = f'<div class="phero__media">{media}</div>' if media else ""
    return f"""
<section class="phero {cls}">
  <div class="wrap phero__in">
    <div class="phero__text">
      <p class="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      {f'<p class="lead">{lead}</p>' if lead else ""}
    </div>
    {m}
  </div>
</section>"""


def cta_band(title, text, primary=("/kontakt-1/", "Platz anfragen"), secondary=("/anmeldeformular/", "Online anmelden")):
    return f"""
<section class="band">
  <div class="wrap band__in">
    <div><h2>{title}</h2><p>{text}</p></div>
    <div class="band__actions"><a class="btn btn--clay" href="{primary[0]}">{primary[1]}</a><a class="btn btn--line" href="{secondary[0]}">{secondary[1]}</a></div>
  </div>
</section>"""


def price_cards(cls=""):
    cards = "".join(f"""
      <article class="price{' price--feature' if p['id'] == 'ferien' else ''}">
        <h3>{p['title']}</h3>
        <p class="price__amount"><span class="price__cur">CHF</span> {p['price']}.–<span class="price__unit">{p['unit']}</span></p>
        <p class="price__note">{p['note']}</p>
      </article>""" for p in PRICES)
    extras = "".join(f'<li><span>{e["title"]}</span><strong>CHF {e["price"]}.– <small>{e["unit"]}</small></strong></li>' for e in EXTRAS)
    return f'<div class="prices {cls}">{cards}</div><ul class="extras">{extras}</ul>'


def calculator():
    opts = "".join(f"""<label class="chip"><input type="radio" name="art" value="{p['id']}"{' checked' if i == 0 else ''}><span>{p['title']}<small>CHF {p['price']}.– / Tag</small></span></label>"""
                   for i, p in enumerate(PRICES))
    return f"""
<form class="calc" data-calc aria-labelledby="calc-title" novalidate>
  <div class="calc__head"><p class="eyebrow">Unverbindlich</p><h3 id="calc-title">Aufenthalt berechnen</h3></div>
  <fieldset class="chips chips--stack"><legend class="sr-only">Betreuungsart</legend>{opts}</fieldset>
  <div class="calc__grid">
    <div class="stepper-field"><label for="calc-tage">Anzahl Tage <small>inkl. An- und Abreisetag</small></label>
      <div class="stepper"><button type="button" data-step="-1" aria-label="Ein Tag weniger">−</button><input id="calc-tage" name="tage" type="number" inputmode="numeric" min="1" max="90" value="1"><button type="button" data-step="1" aria-label="Ein Tag mehr">+</button></div></div>
    <div class="stepper-field"><label for="calc-feiertage">davon Feiertage</label>
      <div class="stepper"><button type="button" data-step="-1" aria-label="Ein Feiertag weniger">−</button><input id="calc-feiertage" name="feiertage" type="number" inputmode="numeric" min="0" max="90" value="0"><button type="button" data-step="1" aria-label="Ein Feiertag mehr">+</button></div></div>
  </div>
  <label class="switch"><input type="checkbox" name="welpe"><span class="switch__ui" aria-hidden="true"></span><span>Welpe <small>+ CHF 10.– pro Tag</small></span></label>
  <label class="switch"><input type="checkbox" name="integration" checked><span class="switch__ui" aria-hidden="true"></span><span>Erster Aufenthalt <small>Rudelintegration CHF 100.– einmalig</small></span></label>
  <div class="calc__result">
    <p class="calc__label">Geschätzter Betrag</p>
    <output class="calc__total" name="total" for="calc-tage calc-feiertage" aria-live="polite">CHF 160.–</output>
    <ul class="calc__breakdown" data-calc-breakdown></ul>
  </div>
  <p class="calc__note">Schätzung gemäss Preisliste, ohne Gewähr. Massgebend sind die bestätigte Anmeldung und die <a href="/agb/">AGB</a>.</p>
  <a class="btn btn--clay btn--block" href="/kontakt-1/#anfrage" data-calc-request>Mit diesen Angaben anfragen {icon("arrow")}</a>
</form>"""


def live_card():
    return f"""
<div class="livecard">
  <p class="livecard__eyebrow">{icon("clock")} Jetzt in Waltenschwil</p>
  <p class="livecard__status" data-live-status>Bring- und Abholzeiten siehe unten.</p>
</div>"""


def ferien_list():
    items = "".join(
        f'<li class="ferien__item" data-from="{f["from"]}" data-to="{f["to"]}"><span class="ferien__label">{f["label"]}</span>'
        f'<span class="ferien__date">{f["text"]}</span><span class="ferien__state" data-ferien-state></span></li>' for f in FERIEN)
    return f'<ul class="ferien" data-ferien>{items}</ul><p class="ferien__summary" data-ferien-summary></p>'


# ------------------------------------------------------------------ Formulare
def field(name, label, typ="text", req=False, auto=None, extra="", hint=None, full=False, prefix="f"):
    fid = f"{prefix}-{name}"
    star = ' <span class="req" aria-hidden="true">*</span>' if req else ""
    r = " required" if req else ""
    a = f' autocomplete="{auto}"' if auto else ""
    h = f'<p class="field__hint" id="{fid}-hint">{hint}</p>' if hint else ""
    desc = f' aria-describedby="{fid}-hint"' if hint else ""
    cls = "field field--full" if full else "field"
    if typ == "textarea":
        ctl = f'<textarea id="{fid}" name="{name}" rows="4"{r}{a}{desc}{extra}></textarea>'
    elif typ.startswith("select:"):
        options = "".join(f"<option>{o}</option>" for o in typ[7:].split("|"))
        ctl = f'<select id="{fid}" name="{name}"{r}{desc}{extra}><option value="">Bitte wählen</option>{options}</select>'
    else:
        ctl = f'<input id="{fid}" name="{name}" type="{typ}"{r}{a}{desc}{extra}>'
    return f'<div class="{cls}"><label for="{fid}">{label}{star}</label>{ctl}{h}</div>'


def form_common(form_type):
    return (f'<input type="hidden" name="form_type" value="{form_type}"><input type="hidden" name="ts" value="">'
            '<div class="hp" aria-hidden="true"><label>Bitte leer lassen <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>')


def consent(prefix):
    return (f'<div class="check check--consent"><input type="checkbox" id="{prefix}-datenschutz" name="datenschutz" value="ja" required>'
            f'<label for="{prefix}-datenschutz">Ich bin einverstanden, dass meine Angaben zur Bearbeitung verwendet werden '
            f'(<a href="/j/privacy/">Datenschutzerklärung</a>). <span class="req" aria-hidden="true">*</span></label></div>')


def form_feedback():
    return f"""
  <div class="form__status" role="status" aria-live="polite" tabindex="-1"></div>
  <div class="form__fallback" hidden>
    <p><strong>Die Online-Übermittlung hat leider nicht geklappt.</strong> Eure Angaben sind nicht verloren – sendet sie einfach direkt:</p>
    <div class="form__fallback-actions">
      <a class="btn btn--clay btn--sm" data-fallback-sms href="#">Per SMS senden</a>
      <button class="btn btn--line btn--sm" type="button" data-fallback-copy>Text kopieren</button>
      <a class="btn btn--line btn--sm" href="tel:{SITE["phone_tel"]}">{icon("phone")}Anrufen</a>
    </div>
  </div>"""


def anfrage_form(prefix="a", heading=True):
    kinds = ["Tagesbetreuung", "Ferienbetreuung", "Besichtigung", "Allgemeine Frage"]
    chips = "".join(f'<label class="chip"><input type="radio" name="anliegen" value="{k}"{" checked" if i == 0 else ""}><span>{k}</span></label>' for i, k in enumerate(kinds))
    h = '<h2 class="form__title" id="anfrage-titel">Anfrage senden</h2>' if heading else ""
    return f"""
<form class="form" id="anfrage" data-form="anfrage" data-endpoint="/api/anfrage.php" aria-labelledby="anfrage-titel" novalidate>
  {h}
  {form_common("anfrage")}
  <fieldset class="chips"><legend>Worum geht es?</legend>{chips}</fieldset>
  <div class="form__grid">
    {field("name", "Vor- und Nachname", req=True, auto="name", prefix=prefix)}
    {field("email", "E-Mail", "email", req=True, auto="email", prefix=prefix)}
    {field("telefon", "Telefon", "tel", auto="tel", prefix=prefix)}
    {field("hund", "Name und Rasse des Hundes", prefix=prefix, hint="Aktuell nehmen wir nur kleine Hunde auf.")}
    {field("von", "Gewünscht ab", "date", prefix=prefix)}
    {field("bis", "bis", "date", prefix=prefix)}
    {field("nachricht", "Nachricht", "textarea", req=True, full=True, prefix=prefix)}
  </div>
  {consent(prefix)}
  <div class="form__actions"><button class="btn btn--clay" type="submit">Anfrage senden {icon("arrow")}</button><p class="form__req"><span aria-hidden="true">*</span> Pflichtfeld</p></div>
  {form_feedback()}
</form>"""


def checks(name, items, prefix):
    return "".join(
        f'<div class="check"><input type="checkbox" id="{prefix}-{name}-{i}" name="{name}" value="{esc(t)}"><label for="{prefix}-{name}-{i}">{t}</label></div>'
        for i, t in enumerate(items))


def radios(name, items, prefix, req=False):
    r = " required" if req else ""
    return "".join(
        f'<label class="chip"><input type="radio" name="{name}" value="{esc(t)}"{r}><span>{t}</span></label>' for t in items)


def anmeldung_form():
    p = "m"
    steps = [
        ("Halter:in", f"""
          <div class="form__grid">
            {field("nachname", "Name", req=True, auto="family-name", prefix=p)}
            {field("vorname", "Vorname", req=True, auto="given-name", prefix=p)}
            {field("strasse", "Strasse / Nr.", req=True, auto="street-address", prefix=p)}
            {field("plz_ort", "PLZ / Ort", req=True, auto="address-level2", prefix=p)}
            {field("telefon", "Telefon", "tel", req=True, auto="tel", prefix=p)}
            {field("email", "E-Mail", "email", req=True, auto="email", prefix=p)}
          </div>"""),
        ("Notfall & Tierarzt", f"""
          <h3 class="step__sub">Ersatzperson bei Notfällen</h3>
          <div class="form__grid">
            {field("notfall_name", "Name", req=True, prefix=p)}
            {field("notfall_vorname", "Vorname", prefix=p)}
            {field("notfall_telefon", "Telefon", "tel", req=True, prefix=p)}
          </div>
          <h3 class="step__sub">Behandelnder Tierarzt</h3>
          <div class="form__grid">
            {field("tierarzt_name", "Name", prefix=p)}
            {field("tierarzt_strasse", "Strasse", prefix=p)}
            {field("tierarzt_plz_ort", "PLZ / Ort", prefix=p)}
            {field("tierarzt_telefon", "Telefon", "tel", prefix=p)}
          </div>
          <p class="note">{icon("info")} Wir erlauben uns, bei Notfällen die nächstgelegene Praxis aufzusuchen.</p>"""),
        ("Hund", f"""
          <div class="form__grid">
            {field("hund_name", "Name des Hundes", req=True, prefix=p)}
            {field("hund_geburtstag", "Geburtstag", "date", prefix=p)}
            {field("hund_rasse", "Rasse", req=True, prefix=p)}
            {field("hund_gewicht", "Gewicht (kg)", "number", req=True, prefix=p, extra=' min="0" step="0.1" inputmode="decimal"', hint="Aktuell nehmen wir nur kleine Hunde auf.")}
            {field("hund_geschlecht", "Geschlecht", "select:Rüde|Hündin", req=True, prefix=p)}
            {field("chipnummer", "Chipnummer", prefix=p, extra=' inputmode="numeric"')}
          </div>
          <fieldset class="chips"><legend>Kastriert</legend>{radios("kastriert", ["Nein", "Ja, normal", "Ja, chemisch"], p)}</fieldset>
          <p class="note note--warn" data-kastriert-hint hidden>{icon("info")} Leider nehmen wir keine unkastrierten Rüden auf.</p>
          <div class="form__grid">
            {field("allergien", "Allergien", "textarea", prefix=p)}
            {field("krankheiten", "Krankheiten", "textarea", prefix=p)}
          </div>
          <fieldset class="chips"><legend>Gewünschte Betreuung</legend>{radios("betreuung", ["Tagesbetreuung", "Ferienbetreuung", "Beides"], p)}</fieldset>
          {field("betreuung_details", "Gewünschte Tage oder Zeitraum", prefix=p, full=True)}"""),
        ("Charakter", f"""
          <fieldset class="checks"><legend>Charakter / Eigenschaften <small>(alles Zutreffende ankreuzen)</small></legend>
            <div class="checks__grid">{checks("charakter", CHARAKTER, p)}</div>
          </fieldset>
          {field("charakter_sonstiges", "Sonstiges", "textarea", prefix=p, full=True)}"""),
        ("Futter & Schlaf", f"""
          <fieldset class="checks"><legend>Futterangaben</legend>
            <div class="form__grid">{field("futter_name", "Name des Futters", prefix=p)}</div>
            <div class="checks__grid">{checks("futter", ["Nur Trockenfutter", "Nur Nassfutter"], p)}</div>
          </fieldset>
          <fieldset class="chips"><legend>Mahlzeiten</legend>{radios("mahlzeiten", ["1× täglich", "2× täglich", "3× täglich"], p)}</fieldset>
          {field("futter_sonstiges", "Sonstiges zum Futter", "textarea", prefix=p, full=True)}
          <fieldset class="checks"><legend>Schlafgewohnheiten zu Hause</legend>
            <div class="checks__grid">{checks("schlaf", SCHLAF, p)}</div>
          </fieldset>
          {field("schlaf_sonstiges", "Sonstiges zum Schlafen", prefix=p, full=True)}"""),
        ("Abschluss", f"""
          <fieldset class="checks"><legend>Besonderheiten</legend>
            <div class="checks__grid">{checks("besonderheiten", BESONDERHEITEN, p)}</div>
          </fieldset>
          <fieldset class="chips"><legend>Spaziergang</legend>{radios("spaziergang", ["Freilauf", "Leine"], p)}</fieldset>
          {field("aengste", "Ängste – wenn ja, welche?", prefix=p, full=True)}
          {field("bemerkungen", "Was müssen wir über deinen Hund noch wissen?", "textarea", prefix=p, full=True)}
          {field("aufmerksam", "Wie bist du auf uns aufmerksam geworden?", prefix=p, full=True)}
          <fieldset class="chips"><legend>Darf dein Hund auf unserer Homepage mit Bildern veröffentlicht werden?</legend>{radios("fotos", ["Ja", "Nein, lieber nicht"], p)}</fieldset>
          <div class="agbbox">
            <h3 class="step__sub">AGB des Anmeldeformulars</h3>
            {"".join(f"<p>{t}</p>" for t in ANMELDUNG_AGB)}
            <p>Es gelten zudem die <a href="/agb/">Allgemeinen Geschäftsbedingungen</a>.</p>
          </div>
          <div class="check check--consent"><input type="checkbox" id="m-agb" name="agb" value="ja" required><label for="m-agb">Ich bestätige, dass ich die Angaben wahrheitsgetreu ausgefüllt und die AGB gelesen habe. <span class="req" aria-hidden="true">*</span></label></div>
          {consent(p)}"""),
    ]
    nav = "".join(f'<li data-step-dot="{i}"><span class="steps__num">{i + 1}</span><span class="steps__label">{t}</span></li>' for i, (t, _) in enumerate(steps))
    body = "".join(f"""
    <fieldset class="step" data-step="{i}" id="schritt-{i + 1}">
      <legend class="step__title"><span class="step__count">Schritt {i + 1} von {len(steps)}</span>{t}</legend>
      {c}
    </fieldset>""" for i, (t, c) in enumerate(steps))
    return f"""
<form class="form form--wizard" id="anmeldung" data-form="anmeldung" data-wizard data-endpoint="/api/anfrage.php" aria-label="Online-Anmeldeformular" novalidate>
  {form_common("anmeldung")}
  <ol class="steps" aria-hidden="true">{nav}</ol>
  <div class="steps__bar" aria-hidden="true"><span data-step-bar></span></div>
  {body}
  <div class="wizard__nav">
    <button class="btn btn--line" type="button" data-prev hidden>Zurück</button>
    <button class="btn btn--clay" type="button" data-next>Weiter {icon("arrow")}</button>
    <button class="btn btn--clay" type="submit" data-submit>Anmeldung senden {icon("arrow")}</button>
  </div>
  <p class="form__req"><span aria-hidden="true">*</span> Pflichtfeld</p>
  {form_feedback()}
</form>"""


# ================================================================== Seiten
def home():
    hero_key = "unser-zuhause-01"
    rail = "".join(
        f'<li data-rail="{i + 1}"><span class="rail__dot"></span><span class="rail__time">{s["from"] or "Abend"}</span></li>' for i, s in enumerate(DAY))
    rot_sets = [(-5, 3, -2), (4, -3, 2), (-3, 5, -4)]
    panels = []
    for i, s in enumerate(DAY):
        when = ""
        if s["from"] and s["to"]:
            when = f'<p class="day__when"><time>{s["from"]}</time> – <time>{s["to"]}</time> Uhr</p>'
        elif s["from"]:
            when = f'<p class="day__when"><time>{s["from"]}</time> Uhr</p>'
        else:
            when = '<p class="day__when">Am Abend</p>'
        rots = rot_sets[i % 3]
        photos = "".join(pola(k, None, rots[j], sizes="(min-width: 900px) 220px, 34vw", cls=f"pola--{j}") for j, k in enumerate(s["photos"]))
        panels.append(f"""
      <article class="day__panel" data-step="{i + 1}" id="tag-{s['id']}">
        <div class="day__card">
          {when}
          <h2>{s["title"]}</h2>
          <p>{s["text"]}</p>
        </div>
        <div class="day__photos">{photos}</div>
      </article>""")
    day_cfg = [{"id": s["id"], "from": s["from"], "to": s["to"], "cam": s["cam"]} for s in DAY]

    facts = "".join(f"""
      <div class="fact"><dt><span class="fact__num" data-count="{n}">{n}</span> <span class="fact__unit">{u}</span></dt><dd>{t}</dd></div>""" for n, u, t in FACTS)

    park_tiles = []
    for t, txt, key, size in PARK:
        park_tiles.append(f"""
      <article class="tile tile--{size}">
        {img(key, "(min-width: 1000px) 50vw, 100vw", cls="tile__img")}
        <div class="tile__body"><h3>{t}</h3><p>{txt}</p></div>
      </article>""")
    adventure_icons = ["mountain", "water", "tunnel", "tree", "leaf", "sun"]
    adv = "".join(f'<li>{icon(adventure_icons[i % 6])}<span>{a}</span></li>' for i, a in enumerate(ADVENTURE))
    park_tiles.insert(2, f"""
      <article class="tile tile--adventure">
        <div class="tile__body">
          <p class="eyebrow eyebrow--light">Neu 2026</p>
          <h3>Der Adventure-Park</h3>
          <p>Der Garten wird neu gestaltet – alles aus natürlichen Materialien.</p>
          <ul class="adventure">{adv}</ul>
          <a class="link link--light" href="/news/">Mehr in den News {icon("arrow")}</a>
        </div>
      </article>""")
    park_tiles.append(f"""
      <article class="tile tile--facts">
        <ul class="minifacts">
          <li>{icon("bowl")}<span><strong>Einzelfütterung</strong> für stressfreie Nahrungsaufnahme</span></li>
          <li>{icon("van")}<span><strong>Fahrzeug mit 12 Boxen</strong> für die sichere Fahrt ins Grüne</span></li>
          <li>{icon("heart")}<span><strong>Familienanschluss</strong> und artgerechtes Rudelleben</span></li>
          <li>{icon("shield")}<span><strong>Vetamtlich geprüft</strong> Bewilligung-Nr. {SITE["permit"]}</span></li>
        </ul>
      </article>""")

    rots = [-4, 3, -2, 5, -3, 2, -5]
    dogs = "".join(pola(k, IMG[k]["dog"], rots[i], sizes="(min-width: 900px) 240px, 60vw", group="rudel") for i, k in enumerate(META["rudel_eigene"]))

    strip_a = META["impressionen"][::2][:16]
    strip_b = META["impressionen"][1::2][:16]

    def strip(keys):
        return "".join(f'<li>{img(k, "260px", pick=480)}</li>' for k in keys)

    news = NEWS[0]
    news_photos = "".join(lb(k, "news", "(min-width: 900px) 30vw, 80vw", cls="news-teaser__img") for k in news["photos"])

    body = f"""
<section class="day" id="tag" aria-labelledby="hero-title" data-day='{json.dumps(day_cfg)}'>
  <div class="day__sticky">
    <div class="day__media" aria-hidden="true">
      {img(hero_key, "100vw", cls="day__img", eager=True, alt="", pick=1600)}
      <canvas class="day__gl" data-day-canvas></canvas>
      <div class="day__scrim"></div>
    </div>
    <div class="day__hud" aria-hidden="true">
      <div class="day__clock"><span class="day__clock-label">Ein Tag im Park</span><span class="day__time" data-day-time>06:30</span><span class="day__sun" data-day-sun><span></span></span><span class="day__credit">Echtes Luftbild · Tageslicht simuliert</span></div>
      <ol class="rail">{rail}</ol>
    </div>
    <div class="day__panels">
      <div class="day__panel day__hero is-active" data-step="0">
        <p class="eyebrow eyebrow--light">Tages- und Ferienbetreuung · Waltenschwil AG</p>
        <h1 id="hero-title">Hundepension <em>im Park</em></h1>
        <p class="day__lead">Tages- und Feriengäste sind herzlich willkommen: 3000 m² sicher eingezäunter Park mit altem Baumbestand, liebevoller Familienanschluss und artgerechtes Rudelleben.</p>
        <div class="day__actions">
          <a class="btn btn--clay" href="#anfrage">Platz anfragen</a>
          <a class="btn btn--ghost-light" href="#tag-{DAY[0]['id']}">Einen Tag miterleben {icon("down")}</a>
        </div>
        <p class="live live--hero" data-live-status></p>
      </div>
      {"".join(panels)}
    </div>
    <p class="day__hint" aria-hidden="true"><span></span>Scrollen und den Tag erleben</p>
  </div>
</section>

<section class="intro" id="willkommen" aria-labelledby="willkommen-titel">
  <div class="wrap intro__grid">
    <div class="intro__text reveal">
      <p class="eyebrow">Willkommen</p>
      <h2 id="willkommen-titel">Mit viel Leidenschaft haben wir ein wahres Paradies für Hunde erschaffen.</h2>
      <p>Bei uns erwartet euch ein traumhaftes Umfeld, das keine Wünsche offen lässt. Unser grosses und sicher eingezäuntes Gelände von 3000 m² bietet Hunden viel Platz zum Spielen und Entdecken. Umgeben von altem Baumbestand, Büschen und Wiesen finden die Vierbeiner hier eine naturnahe und abwechslungsreiche Umgebung.</p>
      <p>Unsere besondere Stärke ist der liebevolle Familienanschluss und das artgerechte Rudelleben, das den Hunden sozialen Kontakt und Geborgenheit schenkt.</p>
      <a class="link" href="/über-mich/">Daniela Wulf kennenlernen {icon("arrow")}</a>
    </div>
    <figure class="intro__media reveal">
      {img("über-mich-01".replace("über", "ueber"), "(min-width: 1000px) 45vw, 100vw")}
      <figcaption><span class="script">Daniela Wulf</span> Inhaberin, Hundepension im Park</figcaption>
    </figure>
  </div>
  <dl class="facts wrap">{facts}</dl>
</section>

<section class="park" id="park" aria-labelledby="park-titel">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Der Park</p>
      <h2 id="park-titel">Viel Platz zum Spielen, Entdecken und Ausruhen.</h2>
      <p>Für spannende Aktivitäten stehen ein Kiesplatz sowie ein kleiner und grosser Badeteich zur Verfügung. Ein Erdhügel mit Tunnel lädt zum Klettern und Verstecken ein – ein echtes Abenteuer!</p>
    </div>
    <div class="bento">{"".join(park_tiles)}</div>
    <p class="park__more"><a class="link" href="/unser-zuhause/">Haus und Park ansehen {icon("arrow")}</a></p>
  </div>
</section>

<section class="pack" id="rudel" aria-labelledby="rudel-titel">
  <div class="wrap pack__head reveal">
    <p class="eyebrow eyebrow--light">Das Rudel</p>
    <h2 id="rudel-titel">Meine 7 Zwerge</h2>
    <p>Mabel, June, Kiwi, Chayu, Anjani, Asho und Osay – sie sind immer mit dabei. Das artgerechte Rudelleben schenkt den Hunden sozialen Kontakt und Geborgenheit.</p>
  </div>
  <div class="pack__row" tabindex="0" role="region" aria-label="Fotos des Rudels, seitlich scrollbar">{dogs}</div>
  <p class="wrap pack__more"><a class="link link--light" href="/rudel/">Das Rudel und unsere Gäste {icon("arrow")}</a></p>
</section>

<section class="pricing" id="preise" aria-labelledby="preise-titel">
  <div class="wrap pricing__grid">
    <div class="pricing__main">
      <div class="section-head reveal">
        <p class="eyebrow">Preise</p>
        <h2 id="preise-titel">Klar und fair.</h2>
        <p>Ein- und Austrittstag werden zu 100 % verrechnet. Alle Konditionen findet ihr auf der <a href="/preise/">Preisseite</a>.</p>
      </div>
      {price_cards()}
    </div>
    <div class="pricing__calc reveal">{calculator()}</div>
  </div>
</section>

<section class="times" id="zeiten" aria-labelledby="zeiten-titel">
  <div class="wrap times__grid">
    <div class="reveal">
      <p class="eyebrow">Öffnungszeiten</p>
      <h2 id="zeiten-titel">Bring- und Abholzeiten</h2>
      {live_card()}
      {hours_list()}
      <p class="times__note">{icon("calendar")} Besichtigungen Montag bis Freitag – bitte mit Voranmeldung.</p>
    </div>
    <div class="reveal">
      <p class="eyebrow">Betriebsferien</p>
      <h2>Wann wir zu sind</h2>
      {ferien_list()}
      <a class="link" href="/betriebsferien/">Alle Betriebsferien {icon("arrow")}</a>
    </div>
  </div>
</section>

<section class="strip" aria-labelledby="strip-titel">
  <div class="wrap section-head section-head--row reveal">
    <div><p class="eyebrow">Impressionen</p><h2 id="strip-titel">Momente aus dem Rudel</h2></div>
    <a class="btn btn--line" href="/impressionen/">Alle Impressionen ansehen</a>
  </div>
  <div class="marquee" data-marquee>
    <ul class="marquee__track">{strip(strip_a)}</ul>
    <ul class="marquee__track marquee__track--rev">{strip(strip_b)}</ul>
  </div>
</section>

<section class="news-teaser" aria-labelledby="news-titel">
  <div class="wrap news-teaser__grid">
    <div class="reveal">
      <p class="eyebrow">News {news["year"]}</p>
      <h2 id="news-titel">{news["title"]}</h2>
      <p>{news["text"]}</p>
      <p class="script script--lg">{news["caption"]}</p>
      <a class="link" href="/news/">Alle News {icon("arrow")}</a>
    </div>
    <div class="news-teaser__photos reveal">{news_photos}</div>
  </div>
</section>

<section class="contact contact--light" id="kontakt" aria-labelledby="anfrage-titel">
  <div class="wrap contact__grid">
    <div class="contact__info reveal">
      <p class="eyebrow">Kontakt</p>
      <h2 class="contact__title">Wir freuen uns auf euch.</h2>
      <p>Für einen Tages- oder Ferienplatz, eine Besichtigung oder einfach eine Frage: ruft an oder schreibt uns.</p>
      {contact_card()}
    </div>
    <div class="contact__form reveal">{anfrage_form("h")}</div>
  </div>
</section>"""
    ld = [business_ld(), {"@type": "WebSite", "@id": f"{D}/#website", "url": f"{D}/", "name": SITE["name"], "inLanguage": "de-CH"}]
    render("/", "Hundepension im Park – Tages- und Ferienbetreuung in Waltenschwil",
           "Tages- und Ferienbetreuung für Hunde in Waltenschwil AG: 3000 m² Park, 12 Plätze, Familienanschluss und "
           "Rudelleben. Vetamtlich geprüft (Bewilligung-Nr. 25.049).",
           body, mode="overlay", ld=ld, body_class="page-home", scripts=("park-day.js",), priority="1.0")


def contact_card():
    maps = "https://www.google.com/maps/search/?api=1&query=" + quote(f'{SITE["street"]}, {SITE["zip"]} {SITE["city"]}')
    return f"""
<ul class="contact-card">
  <li>{icon("phone")}<div><span class="contact-card__label">Natel</span><a href="tel:{SITE["phone_tel"]}">{SITE["phone_display"]}</a></div></li>
  <li>{icon("pin")}<div><span class="contact-card__label">Adresse</span><address>{SITE["name"]}<br>{SITE["owner"]}<br>{SITE["street"]}<br>{SITE["zip"]} {SITE["city"]}</address>
    <a class="link link--sm" href="{maps}" target="_blank" rel="noopener">Route planen {icon("external")}<span class="sr-only"> (öffnet Google Maps in neuem Fenster)</span></a></div></li>
  <li>{icon("clock")}<div><span class="contact-card__label">Bring- und Abholzeiten</span>Mo–Fr 06.30–08.30 und 16.00–18.30 Uhr<br>Sa 08.00–08.30 Uhr</div></li>
</ul>"""


def page_ueber_mich():
    tl = "".join(f"""
      <li class="tl__item reveal"><span class="tl__year">{y}</span><div class="tl__body"><h3>{t}</h3>{f'<p>{d}</p>' if d else ''}</div></li>""" for y, t, d in WERDEGANG)
    body = f"""
{phero("Über mich", "Im Einklang mit der Natur, zusammen mit den Hunden – was will man mehr …", None,
       img("ueber-mich-01", "(min-width: 1000px) 50vw, 100vw", eager=True), "phero--split")}
<section class="prose-sec">
  <div class="wrap prose-grid">
    <div class="prose reveal">
      <p class="lead">Schon immer haben mich Tiere fasziniert. Sie leben im Hier und Jetzt und brauchen keinen Luxus. Zerstören die Umwelt nicht. Sind immer für uns da.</p>
      <p>Meine Arbeit beruht auf einer ruhigen, sanften und disziplinierten Betreuung.</p>
      <p>Es braucht sehr viel Vertrauen, um seinen allerliebsten Hund in fremde Hände zu geben. Deswegen möchte ich mein Allerbestes geben, damit sich dein Hund bei mir wohl und sicher fühlt.</p>
      <p class="script script--lg">Daniela Wulf</p>
    </div>
    <aside class="aside-card reveal">
      <h2 class="aside-card__title">Auf einen Blick</h2>
      <ul class="minifacts minifacts--dark">
        <li>{icon("shield")}<span><strong>Vetamtlich geprüfte Betreuung</strong> Bewilligung-Nr. {SITE["permit"]}</span></li>
        <li>{icon("check")}<span><strong>FBA</strong> Fachspezifische berufsunabhängige Ausbildung, Bewilligungs-Nr. {SITE["fba_permit"]}</span></li>
        <li>{icon("heart")}<span><strong>Seit 2016</strong> Hundepension, 2026 Neueröffnung als Hundepension im Park</span></li>
      </ul>
    </aside>
  </div>
</section>
<section class="timeline-sec" aria-labelledby="werdegang">
  <div class="wrap">
    <div class="section-head reveal"><p class="eyebrow">Werdegang</p><h2 id="werdegang">Von harmony-dog zur Hundepension im Park</h2></div>
    <ol class="tl">{tl}</ol>
  </div>
</section>
{cta_band("Lernt uns kennen.", "Besichtigungen sind von Montag bis Freitag mit Voranmeldung möglich.", ("/kontakt-1/", "Besichtigung anfragen"), ("/unser-zuhause/", "Unser Zuhause ansehen"))}"""
    render("/über-mich/", "Über mich – Daniela Wulf | Hundepension im Park, Waltenschwil",
           "Daniela Wulf, Inhaberin der Hundepension im Park in Waltenschwil: ruhige, sanfte und disziplinierte Betreuung. "
           "Werdegang von harmony-dog (2016) bis zur Neueröffnung 2026.",
           body, crumbs=[("/über-mich/", "Über mich")])


def gallery(keys, group, cls="masonry", filters=False):
    items = []
    for k in keys:
        e = IMG[k]
        cats = " ".join(e.get("cats", []))
        attr = f' data-cats="{cats}"' if filters else ""
        items.append(f'<li class="masonry__item"{attr}>{lb(k, group, "(min-width: 1200px) 25vw, (min-width: 700px) 33vw, 50vw", cls="masonry__link")}</li>')
    return f'<ul class="{cls}" data-gallery="{group}">{"".join(items)}</ul>'


def page_zuhause():
    keys = META["zuhause"]
    park = keys[1:4]
    house = keys[4:]
    body = f"""
<section class="aerial">
  {img(keys[0], "100vw", eager=True, cls="aerial__img", pick=2000)}
  <div class="aerial__shade"></div>
  <div class="wrap aerial__text">
    <p class="eyebrow eyebrow--light">Unser Zuhause</p>
    <h1>Eine Villa im Park – mit 3000 m² Platz für Hunde.</h1>
    <p class="lead">Umgeben von altem Baumbestand, Büschen und Wiesen finden die Vierbeiner hier eine naturnahe und abwechslungsreiche Umgebung.</p>
  </div>
</section>
<section class="zuhause">
  <div class="wrap">
    <div class="split reveal">
      <div class="section-head">
        <p class="eyebrow">Draussen</p>
        <h2>Der Park</h2>
        <p>Für spannende Aktivitäten stehen ein Kiesplatz sowie ein kleiner und grosser Badeteich zur Verfügung. Ein Erdhügel mit Tunnel lädt zum Klettern und Verstecken ein. Darüber hinaus gibt es eine überdachte und erhöhte Liegefläche aus Holz, die Schutz bei jedem Wetter bietet.</p>
        <p>Entspannung garantieren die gemütlichen Outdoor-Loungeplätze.</p>
      </div>
    </div>
    <div class="editorial editorial--3">{"".join(lb(k, "zuhause", "(min-width: 1000px) 33vw, 100vw", cls="editorial__item reveal") for k in park)}</div>
    <div class="split reveal">
      <div class="section-head">
        <p class="eyebrow">Drinnen</p>
        <h2>Das Haus</h2>
        <p>Diverse Ruhe- und Rückzugsmöglichkeiten im Haus sind allen Hunden jederzeit frei zugänglich – Hundehöhlen, Kissen, Körbchen und sonnige Plätze am Fenster.</p>
      </div>
    </div>
    <div class="editorial editorial--mosaic">{"".join(lb(k, "zuhause", "(min-width: 1000px) 33vw, 100vw", cls="editorial__item reveal") for k in house)}</div>
  </div>
</section>
{cta_band("Am schönsten ist es vor Ort.", "Kommt vorbei und überzeugt euch selbst – Besichtigungen Montag bis Freitag mit Voranmeldung.", ("/kontakt-1/", "Besichtigung anfragen"), ("/impressionen/", "Impressionen ansehen"))}"""
    render("/unser-zuhause/", "Unser Zuhause – Villa und Park | Hundepension im Park, Waltenschwil",
           "Die Hundepension im Park: eine Villa mit 3000 m² sicher eingezäuntem Park, alten Bäumen, Liegefläche aus Holz, "
           "Outdoor-Lounges und Rückzugsorten im Haus.",
           body, crumbs=[("/unser-zuhause/", "Unser Zuhause")], og="/assets/img/og-hundepension.jpg")


def page_angebot():
    steps = []
    for i, s in enumerate(DAY[:-1]):
        when = f'{s["from"]}' + (f' – {s["to"]}' if s["to"] else "") + " Uhr"
        photos = "".join(lb(k, "ablauf", "(min-width: 900px) 18vw, 30vw", cls="ablauf__photo") for k in s["photos"][:2])
        steps.append(f"""
      <li class="ablauf__item reveal">
        <p class="ablauf__time">{when}</p>
        <div class="ablauf__body"><h3>{s["title"]}</h3><p>{s["text"]}</p></div>
        <div class="ablauf__photos">{photos}</div>
      </li>""")
    adm = "".join(f'<li>{icon("check")}<span>{a}</span></li>' for a in ADMISSION)
    body = f"""
{phero("Angebot", "Tagesablauf", "Struktur, Bewegung und Ruhe: So sieht ein Tag bei uns aus – für Tagesgäste wie für Feriengäste.",
       img("angebot-01", "(min-width: 1000px) 50vw, 100vw", eager=True), "phero--split")}
<section class="ablauf-sec">
  <div class="wrap">
    <ol class="ablauf">{"".join(steps)}</ol>
  </div>
</section>
<section class="info-sec">
  <div class="wrap info-grid">
    <article class="info-card reveal">
      {icon("bowl", "info-card__ico")}
      <h2>Futter</h2>
      <p>Damit die Verträglichkeit des Futters gewährleistet ist, bringt der Besitzer sein Futter selber mit.</p>
      <p>Auf Wunsch kann gegen Aufpreis auch unser Futter (Navita) gefüttert werden. Die Fütterung erfolgt einzeln.</p>
    </article>
    <article class="info-card info-card--dark reveal">
      {icon("shield", "info-card__ico")}
      <h2>Aufnahme</h2>
      <ul class="checklist">{adm}</ul>
      <a class="link link--light" href="/agb/">Zu den AGB {icon("arrow")}</a>
    </article>
    <article class="info-card reveal">
      {icon("van", "info-card__ico")}
      <h2>Unterwegs</h2>
      <p>Für eine sichere Fahrt ins Grüne steht ein speziell ausgebautes Fahrzeug mit 12 Boxen bereit. Spaziert wird in gestaffelten Gruppen.</p>
    </article>
  </div>
</section>
{cta_band("Passt das für deinen Hund?", "Fragt einen Tages- oder Ferienplatz an – oder meldet euren Hund direkt online an.")}"""
    render("/angebot/", "Angebot und Tagesablauf | Hundepension im Park, Waltenschwil",
           "Tagesablauf der Hundepension im Park: Bringen ab 06.30 Uhr, Spaziergänge in Gruppen, Einzelfütterung, "
           "Ruhepause, Freilauf im Park, Abholen bis 18.30 Uhr.",
           body, crumbs=[("/angebot/", "Angebot")])


def page_rudel():
    rots = [-4, 3, -2, 5, -3, 2, -5]
    dogs = "".join(pola(k, IMG[k]["dog"], rots[i], sizes="(min-width: 1100px) 22vw, (min-width: 700px) 30vw, 46vw", group="eigene") for i, k in enumerate(META["rudel_eigene"]))
    body = f"""
{phero("Rudel", "Meine 7 Zwerge", "Mabel, June, Kiwi, Chayu, Anjani, Asho und Osay – unser eigenes Rudel, in dem eure Hunde Anschluss finden.")}
<section class="pack-page">
  <div class="wrap"><div class="pola-grid">{dogs}</div></div>
</section>
<section class="guests" aria-labelledby="gaeste">
  <div class="wrap">
    <div class="section-head reveal"><p class="eyebrow">Betreute Hunde</p><h2 id="gaeste">Unsere Gäste</h2><p>Ein paar der Hunde, die bei uns zu Gast waren und sind.</p></div>
    {gallery(META["rudel_gaeste"], "gaeste")}
  </div>
</section>
{cta_band("Wird dein Hund Teil des Rudels?", "Für neue Hunde gibt es eine Rudelintegration (CHF 100.– einmalig).", ("/kontakt-1/", "Platz anfragen"), ("/preise/", "Zu den Preisen"))}"""
    render("/rudel/", "Rudel – Meine 7 Zwerge und unsere Gäste | Hundepension im Park",
           "Das Rudel der Hundepension im Park: Mabel, June, Kiwi, Chayu, Anjani, Asho und Osay – und Fotos der betreuten Hunde.",
           body, crumbs=[("/rudel/", "Rudel")])


def page_preise():
    cond = "".join(f"<li>{c}</li>" for c in CONDITIONS)
    body = f"""
{phero("Preise", "Tages- und Ferienplätze", "Alle Preise in Schweizer Franken. Für neue Hunde fällt einmalig die Rudelintegration an.",
       img("preise-01", "(min-width: 1000px) 360px, 60vw", cls="phero__cutout", eager=True, alt=""), "phero--split phero--cutout")}
<section class="pricing pricing--page">
  <div class="wrap pricing__grid">
    <div class="pricing__main">
      {price_cards()}
      <div class="conditions reveal">
        <h2>Konditionen</h2>
        <ul class="checklist checklist--plain">{cond}</ul>
        <p class="conditions__more">Weitere Bestimmungen in den <a href="/agb/">AGB</a>.</p>
      </div>
    </div>
    <div class="pricing__calc">{calculator()}</div>
  </div>
</section>
{cta_band("Platz frei?", "Fragt euren Wunschtermin an – wir melden uns.")}"""
    render("/preise/", "Preise ab CHF 60.– pro Tag | Hundepension im Park",
           "Preise der Hundepension im Park: Tagesbetreuung CHF 60.–, Feriengäste mit Tagesplatz CHF 70.–, ohne Tagesplatz "
           "CHF 80.– pro Tag. Mit Aufenthaltsrechner und Konditionen.",
           body, crumbs=[("/preise/", "Preise")])


def page_agb():
    toc = "".join(f'<li><a href="#agb-{i + 1}">{t}</a></li>' for i, (t, _) in enumerate(AGB))
    secs = "".join(f"""
      <section class="agb__sec" id="agb-{i + 1}" aria-labelledby="agb-{i + 1}-t"><h2 id="agb-{i + 1}-t"><span>{i + 1:02d}</span>{t}</h2>{"".join(f"<p>{p}</p>" for p in ps)}</section>""" for i, (t, ps) in enumerate(AGB))
    body = f"""
{phero("AGB", "Allgemeine Geschäftsbedingungen der Hundepension im Park", None)}
<section class="agb">
  <div class="wrap agb__grid">
    <nav class="agb__toc" aria-label="Inhalt der AGB"><p class="eyebrow">Inhalt</p><ol>{toc}</ol>
      <a class="btn btn--line btn--sm" href="/assets/docs/Anmeldeformular_im_Park.pdf" download>{icon("download")}Anmeldeformular (PDF)</a></nav>
    <div class="agb__body prose">{secs}</div>
  </div>
</section>"""
    render("/agb/", "AGB | Hundepension im Park, Waltenschwil",
           "Allgemeine Geschäftsbedingungen der Hundepension im Park: Zahlung und Annulation, Aufnahmebedingungen, Haftung, "
           "Krankheit und Notfälle, Fotos sowie Gerichtsstand.",
           body, crumbs=[("/agb/", "AGB")], priority="0.3")


def page_anmeldung():
    body = f"""
{phero("Anmeldeformular", "Online anmelden", "Das Anmeldeformular – jetzt bequem online. Alle Angaben aus dem bisherigen PDF in sechs kurzen Schritten.")}
<section class="anmeldung">
  <div class="wrap anmeldung__grid">
    <div class="anmeldung__form">{anmeldung_form()}</div>
    <aside class="aside-card aside-card--sticky">
      <h2 class="aside-card__title">Lieber auf Papier?</h2>
      <p>Das Anmeldeformular gibt es weiterhin als PDF zum Ausdrucken.</p>
      <a class="btn btn--line btn--block" href="/assets/docs/Anmeldeformular_im_Park.pdf" download>{icon("download")}Anmeldeformular_im Park.pdf <small>110 KB</small></a>
      <hr>
      <h3 class="aside-card__sub">Gut zu wissen</h3>
      <ul class="checklist checklist--small">{"".join(f'<li>{icon("check")}<span>{a}</span></li>' for a in ADMISSION)}</ul>
      <p><a class="link link--sm" href="tel:{SITE["phone_tel"]}">{icon("phone")} Fragen? {SITE["phone_display"]}</a></p>
    </aside>
  </div>
</section>"""
    render("/anmeldeformular/", "Anmeldeformular – online anmelden | Hundepension im Park",
           "Hund online anmelden: Halter, Notfallkontakt, Tierarzt, Angaben zum Hund, Charakter, Futter und Schlafgewohnheiten. "
           "Das Anmeldeformular steht auch als PDF bereit.",
           body, crumbs=[("/anmeldeformular/", "Anmeldeformular")])


def page_impressionen():
    cats = META["categories"]
    counts = {c: sum(1 for k in META["impressionen"] if c in IMG[k].get("cats", [])) for c in cats}
    btns = f'<button type="button" class="filter is-active" data-filter="alle" aria-pressed="true">Alle <span>{len(META["impressionen"])}</span></button>' + "".join(
        f'<button type="button" class="filter" data-filter="{c}" aria-pressed="false">{l} <span>{counts[c]}</span></button>' for c, l in cats.items())
    body = f"""
{phero("Impressionen", "Momente aus dem Rudel", "Spaziergänge, Wasser, Schnee und viel Kuschelzeit – {0} Fotos aus dem Alltag in der Hundepension.".format(len(META["impressionen"])))}
<section class="impressionen">
  <div class="wrap">
    <div class="filters" role="group" aria-label="Fotos filtern" data-filters>{btns}</div>
    <p class="sr-only" aria-live="polite" data-filter-status></p>
    {gallery(META["impressionen"], "impressionen", filters=True)}
  </div>
</section>"""
    render("/impressionen/", "Impressionen – Fotos | Hundepension im Park, Waltenschwil",
           "Fotos aus der Hundepension im Park: Spaziergänge im Wald, Abkühlung am Wasser, Winter, Freilauf im Park und "
           "gemütliche Stunden im Haus.",
           body, crumbs=[("/impressionen/", "Impressionen")])


def page_pflegehunde():
    body = f"""
{phero("Pflegehunde", "Zur Zeit sind keine Pflegehunde bei uns.", "Sobald wieder ein Pflegehund ein neues Zuhause sucht, stellen wir ihn hier vor.")}
<section class="empty-state">
  <div class="wrap empty-state__in reveal">
    <img src="/assets/img/emblem-dark-480.webp" alt="" width="480" height="{round(IMG['emblem']['h'] * 480 / IMG['emblem']['w'])}" loading="lazy">
    <p>Hunde in Not und auf Platzsuche findet ihr auch bei unseren Partnern:</p>
    <a class="btn btn--line" href="/links/">Zu den Links {icon("arrow")}</a>
  </div>
</section>"""
    render("/pflegehunde/", "Pflegehunde | Hundepension im Park, Waltenschwil",
           "Pflegehunde der Hundepension im Park: Zur Zeit sind keine Pflegehunde bei uns.",
           body, crumbs=[("/pflegehunde/", "Pflegehunde")], priority="0.3")


def page_betriebsferien():
    body = f"""
{phero("Betriebsferien", "Betriebsferien 2026", "In diesen Zeiten bleibt die Hundepension geschlossen. Bitte plant eure Ferien frühzeitig.",
       img("betriebsferien-01", "(min-width: 1000px) 380px, 60vw", cls="phero__deco", eager=True, alt=""), "phero--split phero--cutout")}
<section class="ferien-sec">
  <div class="wrap ferien-sec__in">{ferien_list()}</div>
</section>
{cta_band("Ferien geplant?", "Reserviert den Platz für euren Hund rechtzeitig.", ("/kontakt-1/", "Ferienplatz anfragen"), ("/preise/", "Preise ansehen"))}"""
    render("/betriebsferien/", "Betriebsferien 2026 | Hundepension im Park, Waltenschwil",
           "Betriebsferien der Hundepension im Park 2026: Winterferien, ein Wochenende im Juni, Sommer- und Herbstferien.",
           body, crumbs=[("/betriebsferien/", "Betriebsferien")], priority="0.5")


def page_news():
    items = []
    for n in NEWS:
        photos = ""
        if n["photos"]:
            photos = '<div class="newsitem__photos">' + "".join(lb(k, "news", "(min-width: 900px) 30vw, 90vw", cls="newsitem__photo") for k in n["photos"]) + "</div>"
        cap = f'<p class="script script--lg">{n["caption"]}</p>' if n["caption"] else ""
        items.append(f"""
      <article class="newsitem reveal">
        <p class="newsitem__year">{n["year"]}</p>
        <div class="newsitem__body"><h2>{n["title"]}</h2><p>{n["text"]}</p>{cap}{photos}</div>
      </article>""")
    body = f"""
{phero("News", "Neuigkeiten aus dem Park", None)}
<section class="news-sec"><div class="wrap">{"".join(items)}</div></section>"""
    render("/news/", "News | Hundepension im Park, Waltenschwil",
           "Neuigkeiten der Hundepension im Park: 2026 wird der Garten zum Adventure-Park mit Liegeplatz aus Holz, Teich, "
           "Erdhügel mit Tunnel und natürlichen Böden.",
           body, crumbs=[("/news/", "News")], priority="0.5")


def page_oeffnungszeiten():
    body = f"""
{phero("Öffnungszeiten", "Bring- und Abholzeiten", None)}
<section class="times times--page">
  <div class="wrap times__grid">
    <div class="reveal">
      {live_card()}
      {hours_list("hours--large")}
    </div>
    <div class="reveal">
      <article class="info-card">
        {icon("calendar", "info-card__ico")}
        <h2>Besichtigungen</h2>
        <p>Montag bis Freitag – bitte mit Voranmeldung.</p>
        <a class="btn btn--clay btn--sm" href="/kontakt-1/">Besichtigung anfragen</a>
      </article>
      <article class="info-card">
        {icon("sun", "info-card__ico")}
        <h2>Betriebsferien</h2>
        {ferien_list()}
      </article>
    </div>
  </div>
</section>"""
    render("/öffnungszeiten/", "Öffnungszeiten – Bring- und Abholzeiten | Hundepension im Park",
           "Bring- und Abholzeiten der Hundepension im Park: Montag bis Freitag 06.30–08.30 und 16.00–18.30 Uhr, Samstag "
           "08.00–08.30 Uhr. Sonn- und Feiertage geschlossen.",
           body, crumbs=[("/öffnungszeiten/", "Öffnungszeiten")], ld=[business_ld()], priority="0.7")


def page_kontakt():
    body = f"""
{phero("Kontakt", "Wir freuen uns auf euch.", "Für Tages- und Ferienplätze, Besichtigungen oder Fragen – am schnellsten per Telefon, oder über das Formular.")}
<section class="contact contact--page">
  <div class="wrap contact__grid">
    <div class="contact__info">{contact_card()}
      <div class="notice-card">{icon("info")}<p><strong>{SITE["notice"]}</strong></p></div>
    </div>
    <div class="contact__form">{anfrage_form("k")}</div>
  </div>
</section>"""
    render("/kontakt-1/", "Kontakt | Hundepension im Park, Bahnhofstrasse 1, Waltenschwil",
           "Kontakt zur Hundepension im Park: Daniela Wulf, Bahnhofstrasse 1, 5622 Waltenschwil, Natel 079 355 68 82. "
           "Anfrage für Tages- und Ferienplätze oder Besichtigung.",
           body, crumbs=[("/kontakt-1/", "Kontakt")], ld=[business_ld()], priority="0.8")


def page_links():
    cards = "".join(f'<li><a class="linkcard" href="{u}" target="_blank" rel="noopener">{icon("paw")}<span>{n}</span>{icon("external")}<span class="sr-only"> (öffnet in neuem Fenster)</span></a></li>' for n, u in LINKS)
    body = f"""
{phero("Links", "Empfehlungen", None)}
<section class="links-sec"><div class="wrap"><ul class="linkcards">{cards}</ul></div></section>"""
    render("/links/", "Links | Hundepension im Park, Waltenschwil", "Links und Empfehlungen der Hundepension im Park.",
           body, crumbs=[("/links/", "Links")], priority="0.2")


def page_impressum():
    body = f"""
{phero("Impressum", "Impressum", None)}
<section class="legal"><div class="wrap"><div class="prose">
  <h2>Betreiberin</h2>
  <p>{SITE["name"]}<br>{SITE["owner"]}<br>{SITE["street"]}<br>{SITE["zip"]} {SITE["city"]}<br>Schweiz</p>
  <p>Natel: <a href="tel:{SITE["phone_tel"]}">{SITE["phone_display"]}</a></p>
  <h2>Bewilligung</h2>
  <p>Vetamtlich geprüfte Betreuung, Bewilligung-Nr. {SITE["permit"]}.</p>
  <h2>Verantwortlich für den Inhalt</h2>
  <p>{SITE["owner"]}</p>
  <h2>Haftungsausschluss</h2>
  <p>Die Inhalte dieser Website wurden mit Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte wird keine Gewähr übernommen. Für die Inhalte verlinkter externer Seiten sind ausschliesslich deren Betreiber verantwortlich.</p>
  <h2>Urheberrecht</h2>
  <p>Texte und Fotos auf dieser Website gehören der {SITE["name"]}. Eine Verwendung ist nur mit ausdrücklicher Zustimmung erlaubt.</p>
</div></div></section>"""
    render("/about/", "Impressum | Hundepension im Park, Waltenschwil", "Impressum der Hundepension im Park, Daniela Wulf, Bahnhofstrasse 1, 5622 Waltenschwil.",
           body, crumbs=[("/about/", "Impressum")], priority="0.2")


def page_datenschutz():
    body = f"""
{phero("Datenschutz", "Datenschutzerklärung", "Wie wir mit euren Daten umgehen – kurz und verständlich.")}
<section class="legal"><div class="wrap"><div class="prose">
  <h2>Verantwortliche Stelle</h2>
  <p>{SITE["name"]}, {SITE["owner"]}, {SITE["street"]}, {SITE["zip"]} {SITE["city"]}, Schweiz. Natel <a href="tel:{SITE["phone_tel"]}">{SITE["phone_display"]}</a>.</p>
  <h2>Grundsatz</h2>
  <p>Wir bearbeiten Personendaten im Einklang mit dem schweizerischen Datenschutzgesetz (DSG). Wir erheben nur die Daten, die wir für die Betreuung eures Hundes und die Beantwortung eurer Anfragen benötigen.</p>
  <h2>Anfrage- und Anmeldeformular</h2>
  <p>Wenn ihr uns über ein Formular kontaktiert, bearbeiten wir die eingegebenen Angaben (z. B. Name, Kontaktdaten, Angaben zum Hund, Notfallkontakt, Tierarzt) ausschliesslich zur Bearbeitung der Anfrage, zur Betreuung eures Hundes und für die Abrechnung. Die Angaben werden per E-Mail an uns übermittelt. Eine Weitergabe an Dritte erfolgt nicht, ausser dies ist im Notfall für die Versorgung eures Hundes nötig (z. B. Tierarzt). Wir bewahren die Daten auf, solange es für diese Zwecke und gesetzliche Aufbewahrungspflichten erforderlich ist.</p>
  <h2>Server-Logfiles</h2>
  <p>Beim Aufruf der Website speichert unser Hosting-Anbieter technisch notwendige Angaben (z. B. IP-Adresse, Datum und Uhrzeit, aufgerufene Seite, Browser) in Logfiles. Diese dienen der Sicherheit und dem stabilen Betrieb und werden nicht mit anderen Daten zusammengeführt.</p>
  <h2>Keine Cookies, kein Tracking</h2>
  <p>Diese Website setzt keine Cookies und verwendet keine Analyse- oder Werbedienste. Schriften und Bilder werden direkt von unserem Server geladen. Für Komfortfunktionen (z. B. die Übernahme der Angaben aus dem Preisrechner ins Anfrageformular) wird der lokale Speicher eures Browsers genutzt; diese Daten verlassen euer Gerät nicht.</p>
  <h2>Externe Links</h2>
  <p>Die Schaltfläche «Route planen» öffnet Google Maps. Erst beim Anklicken werden Daten an Google übermittelt; es gelten dann die Datenschutzbestimmungen von Google.</p>
  <h2>Eure Rechte</h2>
  <p>Ihr könnt jederzeit Auskunft über eure bei uns gespeicherten Daten verlangen sowie deren Berichtigung oder Löschung beantragen. Meldet euch dafür einfach bei uns.</p>
  <p class="muted">Stand: {date.today().strftime("%B %Y").replace("October", "Oktober")}</p>
</div></div></section>"""
    render("/j/privacy/", "Datenschutzerklärung | Hundepension im Park", "Datenschutzerklärung der Hundepension im Park: Formulare, Server-Logfiles, keine Cookies und kein Tracking.",
           body, crumbs=[("/j/privacy/", "Datenschutz")], priority="0.2")


def page_404():
    body = f"""
<section class="notfound">
  <div class="wrap notfound__in">
    <img src="/assets/img/emblem-dark-480.webp" alt="" width="480" height="{round(IMG['emblem']['h'] * 480 / IMG['emblem']['w'])}">
    <p class="eyebrow">Fehler 404</p>
    <h1>Diese Fährte führt ins Leere.</h1>
    <p class="lead">Die gesuchte Seite gibt es nicht (mehr). Vielleicht hilft einer dieser Wege weiter:</p>
    <div class="band__actions"><a class="btn btn--clay" href="/">Zur Startseite</a><a class="btn btn--line" href="/kontakt-1/">Kontakt</a></div>
  </div>
</section>"""
    render("/404", "Seite nicht gefunden | Hundepension im Park", "Diese Seite wurde nicht gefunden.", body)
    PAGES.pop()


# ------------------------------------------------------------------ Nebendateien
def site_data():
    data = {
        "hours": HOURS,
        "ferien": [{"label": f["label"], "from": f["from"], "to": f["to"]} for f in FERIEN],
        "prices": {p["id"]: {"title": p["title"], "price": p["price"]} for p in PRICES},
        "extras": {e["id"]: e["price"] for e in EXTRAS},
        "phone": SITE["phone_tel"],
        "email": SITE["email"],
        "day": [{"id": s["id"], "title": s["title"], "from": s["from"], "to": s["to"]} for s in DAY],
    }
    js = ("/* Automatisch erzeugt von tools/build_pages.py – Inhalte in tools/content.py ändern. */\n"
          f"window.SITE = {json.dumps(data, ensure_ascii=False, indent=1)};\n")
    (ROOT / "assets" / "js" / "site-data.js").write_text(js, encoding="utf-8")


def sitemap():
    urls = "".join(f"  <url><loc>{D}{quote(p)}</loc><lastmod>{date.today().isoformat()}</lastmod><priority>{pr}</priority></url>\n" for p, pr in PAGES)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nDisallow: /api/\nDisallow: /_original/\nDisallow: /tools/\n\nSitemap: {D}/sitemap.xml\n", encoding="utf-8")
    manifest = {"name": SITE["name"], "short_name": "Hundepension", "lang": "de-CH", "start_url": "/", "display": "standalone",
                "background_color": "#f5f0e6", "theme_color": "#24382b",
                "icons": [{"src": "/assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                          {"src": "/assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                          {"src": "/assets/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
    (ROOT / "site.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    (ROOT / "assets" / "js").mkdir(parents=True, exist_ok=True)
    home()
    page_ueber_mich()
    page_zuhause()
    page_angebot()
    page_rudel()
    page_preise()
    page_agb()
    page_anmeldung()
    page_impressionen()
    page_pflegehunde()
    page_betriebsferien()
    page_news()
    page_oeffnungszeiten()
    page_kontakt()
    page_links()
    page_impressum()
    page_datenschutz()
    page_404()
    site_data()
    sitemap()
    print("Seiten:", len(PAGES))
