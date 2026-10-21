"""Bereitet alle Originalbilder fürs Web auf.

- _original/bilder/*.jpg|png  ->  assets/img/<name>-<breite>.webp (mehrere Breiten für srcset)
- Logo freigestellt (dunkel/hell) + Emblem, Favicons, Social-Media-Bild
- Fenstermaske der Luftaufnahme für das abendliche Licht im „Tag im Park“
- assets/data/images.json mit Abmessungen, Breiten, Alt-Texten und Kategorien

Aufruf (im Projektordner):  python tools/prepare_images.py
"""
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from image_meta import ALT, CATEGORIES, DOGS, IMPRESSIONEN  # noqa: E402

SRC = ROOT / "_original" / "bilder"
OUT = ROOT / "assets" / "img"
DATA = ROOT / "assets" / "data"
OUT.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

WIDTHS = [480, 960, 1600, 2000]
MAX_SIDE = 2000  # längste Seite der grössten Variante
QUALITY = 78


def slug(name):
    return name.replace("über", "ueber")


def widths_for(w, h):
    top = min(w, round(MAX_SIDE * w / max(w, h)))
    out = [x for x in WIDTHS if x <= top * 0.87]
    out.append(top)
    return out


def save_variants(im, name, force=False):
    has_alpha = im.mode in ("RGBA", "LA")
    im = im.convert("RGBA" if has_alpha else "RGB")
    ws = widths_for(im.width, im.height)
    for w in ws:
        dest = OUT / f"{name}-{w}.webp"
        if dest.exists() and not force:
            continue
        h = round(im.height * w / im.width)
        v = im if w == im.width else im.resize((w, h), Image.LANCZOS)
        v.save(dest, "WEBP", quality=QUALITY, method=5, alpha_quality=90)
    return ws


def ink_logo(src):
    """Logo (schwarz auf weiss) -> Alphakanal aus der Deckkraft der Tinte."""
    g = ImageOps.grayscale(src)
    # Weiss -> transparent, Graustufen bleiben als halbtransparente Kanten erhalten
    alpha = g.point(lambda v: 0 if v > 246 else min(255, int((246 - v) * 255 / 200)))
    bbox = alpha.getbbox()
    return alpha.crop(bbox)


def colored(alpha, rgb):
    im = Image.new("RGBA", alpha.size, rgb + (0,))
    im.putalpha(alpha)
    return im


def main():
    manifest = json.loads((SRC / "manifest.json").read_text(encoding="utf-8"))
    db = {}
    for e in manifest:
        name = e["name"]
        key = slug(name)
        src = Image.open(SRC / e["file"])
        if name == "logo":
            continue
        ws = save_variants(src, key)
        entry = {"w": src.width, "h": src.height, "widths": ws, "alt": ALT.get(name, ""), "page": e["page"]}
        if name in DOGS:
            entry["dog"] = DOGS[name]
        if name.startswith("impressionen-"):
            entry["cats"] = IMPRESSIONEN[int(name.split("-")[1])][1]
        db[key] = entry
        print("ok", key, ws)

    # --- Logo -----------------------------------------------------------
    logo = Image.open(SRC / "logo.png")
    alpha = ink_logo(logo)
    dark = colored(alpha, (34, 43, 35))
    light = colored(alpha, (246, 240, 228))
    for im, n in ((dark, "logo-dark"), (light, "logo-light")):
        im.save(OUT / f"{n}.png", optimize=True)
        im.resize((900, round(im.height * 900 / im.width)), Image.LANCZOS).save(OUT / f"{n}-900.webp", "WEBP", quality=90)
    # Emblem = Chihuahua mit Ranken (links der Schrift, x < 572 im zugeschnittenen Logo)
    emblem_a = alpha.crop((0, 0, 572, alpha.height))
    ImageDraw.Draw(emblem_a).rectangle((536, 150, 572, 270), fill=0)  # Anfang des „H“ entfernen
    emblem_a = emblem_a.crop(emblem_a.getbbox())
    for rgb, n in (((34, 43, 35), "emblem-dark"), ((246, 240, 228), "emblem-light")):
        em = colored(emblem_a, rgb)
        em.save(OUT / f"{n}.png", optimize=True)
        em.resize((480, round(em.height * 480 / em.width)), Image.LANCZOS).save(OUT / f"{n}-480.webp", "WEBP", quality=90)
    # Emblem als runder, cremefarbener Badge für dunkle Hintergründe (Originalgrafik bleibt erhalten)
    side = int(max(emblem_a.size) * 1.22)
    badge = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    ImageDraw.Draw(badge).ellipse((0, 0, side - 1, side - 1), fill=(246, 240, 228, 255))
    badge.alpha_composite(colored(emblem_a, (34, 43, 35)), ((side - emblem_a.width) // 2, (side - emblem_a.height) // 2 + side // 60))
    badge.resize((360, 360), Image.LANCZOS).save(OUT / "emblem-badge-360.webp", "WEBP", quality=90)
    db["logo"] = {"w": dark.width, "h": dark.height, "alt": ALT["logo"]}
    db["emblem"] = {"w": emblem_a.width, "h": emblem_a.height}

    # --- Favicons (Emblem auf cremefarbenem Kreis) -----------------------
    fav_dir = ROOT / "assets" / "icons"
    fav_dir.mkdir(exist_ok=True)

    def icon(size, pad=0.13, round_bg=True):
        canvas = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
        d = ImageDraw.Draw(canvas)
        if round_bg:
            d.ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=(246, 240, 228, 255))
        else:
            d.rectangle((0, 0, size * 4, size * 4), fill=(246, 240, 228, 255))
        inner = int(size * 4 * (1 - 2 * pad))
        em = colored(emblem_a, (34, 43, 35))
        em.thumbnail((inner, inner), Image.LANCZOS)
        canvas.alpha_composite(em, ((size * 4 - em.width) // 2, (size * 4 - em.height) // 2))
        return canvas.resize((size, size), Image.LANCZOS)

    icon(32).save(fav_dir / "favicon-32.png")
    icon(180, 0.12, False).save(fav_dir / "apple-touch-icon.png")
    icon(192).save(fav_dir / "icon-192.png")
    icon(512).save(fav_dir / "icon-512.png")
    icon(512, 0.2, False).save(fav_dir / "icon-maskable-512.png")
    icon(48).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    # --- Social-Media-Bild ----------------------------------------------
    aerial = Image.open(SRC / "unser-zuhause-01.jpg").convert("RGB")
    og = ImageOps.fit(aerial, (1200, 630), Image.LANCZOS, centering=(0.45, 0.45))
    shade = Image.new("RGBA", og.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(og.height):
        a = int(150 * max(0, (y - og.height * 0.35) / (og.height * 0.65)) ** 1.4)
        sd.line([(0, y), (og.width, y)], fill=(18, 26, 20, a))
    og = Image.alpha_composite(og.convert("RGBA"), shade)
    lg = dark.copy()
    lg.thumbnail((470, 200), Image.LANCZOS)
    panel = Image.new("RGBA", (lg.width + 64, lg.height + 52), (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle((0, 0, panel.width - 1, panel.height - 1), 26, fill=(246, 240, 228, 242))
    panel.alpha_composite(lg, (32, 26))
    og.alpha_composite(panel, (54, og.height - panel.height - 46))
    og.convert("RGB").save(OUT / "og-hundepension.jpg", quality=86)

    # --- Fenstermaske für den Abend (Koordinaten in der 2047er Luftaufnahme)
    W, H = aerial.size
    windows = [
        (815, 607, 835, 627), (950, 585, 972, 615),            # Gauben
        (762, 670, 790, 700), (795, 675, 810, 710),            # OG vorne links
        (865, 697, 895, 732), (925, 695, 945, 730),            # OG vorne / Seite
        (982, 647, 995, 680),                                   # Balkontür
        (770, 732, 795, 762), (802, 740, 817, 772),            # EG links
        (870, 757, 897, 800), (925, 747, 947, 795),            # EG Glastüren
        (680, 685, 735, 725), (732, 572, 760, 595),            # Wintergarten / Anbau
    ]
    sharp = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(sharp)
    for x0, y0, x1, y1 in windows:
        d.rectangle((x0, y0, x1, y1), fill=255)
    sharp = sharp.filter(ImageFilter.GaussianBlur(3.5))
    bloom = sharp.filter(ImageFilter.GaussianBlur(28))
    bloom = bloom.point(lambda v: min(255, v * 3))
    mask = Image.merge("RGB", (sharp, bloom, Image.new("L", (W, H), 0))).resize((1024, 768), Image.LANCZOS)
    mask.save(OUT / "park-lichter.png", optimize=True)

    meta = {
        "images": db,
        "categories": CATEGORIES,
        "impressionen": [f"impressionen-{n:02d}" for n in sorted(IMPRESSIONEN)],
        "rudel_eigene": [f"rudel-{n:02d}" for n in range(1, 8)],
        "rudel_gaeste": [f"rudel-{n:02d}" for n in range(8, 45)],
        "zuhause": [f"unser-zuhause-{n:02d}" for n in range(1, 12)],
    }
    (DATA / "images.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print("fertig:", len(db), "Bilder")


if __name__ == "__main__":
    main()
