# Hundepension im Park – Website-Redesign

Neue Website für die **Hundepension im Park** (Daniela Wulf, Bahnhofstrasse 1, 5622 Waltenschwil) als Ersatz
für die bisherige Jimdo-Seite www.hundepension-im-park.ch. Statisches HTML/CSS/JS ohne Build-Pipeline, alle
Seiten werden mit einem kleinen Python-Generator aus einer Inhaltsdatei erzeugt.

## Konzept

**«Ein Tag im Park»** – die Startseite ist ein durchgehender Rundgang auf dem echten Drohnenfoto der Villa.
Beim Scrollen läuft der offizielle Tagesablauf ab (06.30 Ankommen → Spazieren → Mittagessen → Ruhepause →
Freilauf im Park → nach Hause → Abend für Feriengäste):

- Die Kamera schwebt wie eine Drohne über das Gelände (Haustür, Felder, Haus, Garten).
- Das Licht wird per WebGL-Shader passend zur Uhrzeit gefärbt: Morgennebel, Mittagssonne, goldene Stunde,
  Abenddämmerung mit warm erleuchteten Fenstern und Glühwürmchen über den Wiesen.
- Beim ersten Aufruf zeigt das Startbild die **aktuelle Tageszeit in Waltenschwil** und einen Live-Hinweis zu
  den nächsten Bring- und Abholzeiten (inkl. Betriebsferien).
- Zu jeder Station erscheinen echte Fotos als Polaroids.
- Im Bild steht klein «Echtes Luftbild · Tageslicht simuliert».

Weitere Elemente: Park-Übersicht als Bento-Raster, «Meine 7 Zwerge» als Polaroid-Reihe mit Namen, Preisrechner
nach der offiziellen Preisliste, Live-Status der Bring-/Abholzeiten, Betriebsferien mit automatischem Status
(vorbei / jetzt / als Nächstes), Impressionen-Galerie mit Filter und Lightbox, Online-Anmeldung in 6 Schritten
(alle Felder des bisherigen PDF-Formulars), Anfrageformular.

Gestaltung: warmes Papier-Creme, tiefes Waldgrün, Terrakotta für Aktionen, das Moosgrün der alten Seite als
Akzent. Schriften Fraunces (Titel), Figtree (Text) und Caveat (Handschrift, angelehnt an die alte Seite) –
alle **lokal gehostet**, keine Verbindung zu Google.

Inhalte sind 1:1 vom Original übernommen: keine erfundenen Bewertungen, Preise, Zertifikate oder Zahlen.

## Struktur

| Pfad | Inhalt |
|---|---|
| `index.html` | Startseite mit «Ein Tag im Park», Willkommen, Park, Rudel, Preise + Rechner, Zeiten, Impressionen, News, Kontakt |
| `über-mich/`, `unser-zuhause/`, `angebot/`, `rudel/`, `preise/`, `agb/`, `anmeldeformular/`, `impressionen/`, `pflegehunde/`, `betriebsferien/`, `news/`, `öffnungszeiten/`, `kontakt-1/`, `links/` | Unterseiten unter den **bisherigen URLs** |
| `about/` | Impressum (bisherige Jimdo-URL) |
| `j/privacy/` | Datenschutzerklärung (bisherige Jimdo-URL) |
| `404.html` | Fehlerseite |
| `assets/css/main.css` | Alle Styles |
| `assets/js/main.js` | Navigation, Einblenden, Live-Status, Betriebsferien, Preisrechner, Formulare, Lightbox, Galerie |
| `assets/js/park-day.js` | «Ein Tag im Park»: Scroll-Steuerung, Kamerafahrt, WebGL-Licht, Fallbacks |
| `assets/js/site-data.js` | Zeiten, Preise, Betriebsferien für das JavaScript (wird erzeugt) |
| `assets/img/` | Alle Originalbilder als WebP in mehreren Breiten, Logo/Emblem freigestellt, Fenstermaske `park-lichter.png`, Social-Media-Bild |
| `assets/fonts/` | Lokale Webfonts (SIL Open Font License) |
| `assets/docs/Anmeldeformular_im_Park.pdf` | Original-PDF des Anmeldeformulars |
| `assets/icons/`, `favicon.ico`, `site.webmanifest` | Favicons aus dem Logo-Emblem |
| `api/anfrage.php`, `api/config.php` | Formularversand per E-Mail (PHP) |
| `sitemap.xml`, `robots.txt`, `.htaccess` | SEO und Apache-Konfiguration inkl. Weiterleitungen alter Jimdo-Adressen |
| `tools/content.py` | **Alle Inhalte** (Texte, Preise, Zeiten, Betriebsferien, AGB, Werdegang, News) |
| `tools/build_pages.py` | Generator für alle Seiten, Sitemap, Manifest und `site-data.js` |
| `tools/image_meta.py` | Alt-Texte und Galerie-Kategorien aller Bilder |
| `tools/prepare_images.py` | Bildaufbereitung (Originale → WebP, Logo, Favicons, Social-Media-Bild, Fenstermaske) |
| `tools/dev_server.py` | Lokaler Vorschau-Server, nimmt Formular-Sendungen testweise an |
| `tools/check_links.py` | Prüft alle internen Links, Bilder und Anker |
| `_original/` | **Sicherung der alten Website**: alle Seiten als HTML, Rohtexte, alle 132 Bilder in Originalgrösse, PDF |

## Lokal ansehen

```bash
python tools/dev_server.py 8780
```

Danach http://localhost:8780 öffnen. Formular-Sendungen landen in `tools/formular-test.log`.
Mit `--fail` antwortet der Server absichtlich mit einem Fehler, um den Ausweichweg (SMS / Kopieren / Anrufen)
zu testen. Die Seiten nutzen Pfade ab Wurzel (`/assets/…`) – die Website muss im Wurzelverzeichnis der Domain liegen.

## Inhalte ändern

1. Texte, Preise, Zeiten oder Betriebsferien in `tools/content.py` anpassen
   (z. B. Betriebsferien 2027 in `FERIEN` ergänzen, Hinweis «nur kleine Hunde» in `SITE["notice"]`).
2. `python tools/build_pages.py` ausführen – alle Seiten, Sitemap und `site-data.js` werden neu erzeugt.
3. Optional `python tools/check_links.py`.

Neue Fotos: Datei nach `_original/bilder/` legen, in `_original/bilder/manifest.json` und `tools/image_meta.py`
eintragen, dann `python tools/prepare_images.py` und `python tools/build_pages.py`.

## Formulare

- **Anfrage** (Startseite und Kontakt) und **Online-Anmeldung** senden per `POST` an `/api/anfrage.php`.
- In `api/config.php` muss vor dem Livegang die **Empfängeradresse** eingetragen werden. Solange sie fehlt
  (oder der Server kein PHP hat), zeigt das Formular automatisch einen Ausweichweg: Anfrage per SMS an
  079 355 68 82 (fertig ausgefüllt), Text kopieren, anrufen – bei der Anmeldung zusätzlich «Drucken / als PDF».
  Eingaben gehen nicht verloren (Entwurf im Browser-Tab gespeichert).
- Schutz: Honeypot-Feld, Mindest-Ausfüllzeit, Begrenzung auf 6 Sendungen pro IP in 10 Minuten.
- Wird `SITE["email"]` in `tools/content.py` gesetzt, bietet der Ausweichweg zusätzlich «Per E-Mail senden».
- Alternative ohne PHP: in `tools/build_pages.py` `data-endpoint` auf einen Formulardienst setzen (Antwort muss
  JSON `{"ok": true}` liefern).

## Barrierefreiheit, Leistung, SEO

- Kontraste nach WCAG AA, Fokus-Rahmen, Skip-Link, semantische Überschriften, Formular-Fehlermeldungen mit
  `aria-invalid`/`aria-describedby`, Lightbox als `<dialog>` mit Tastatur (Pfeile, Esc) und Wischgesten.
- «Bewegung reduzieren» und fehlendes JavaScript: Der Rundgang erscheint als ruhige, statische Liste.
- Ohne WebGL: Kamerafahrt und Lichtstimmung per CSS. Langsame Geräte: Auflösung des Shaders wird automatisch reduziert.
- Bilder als WebP mit `srcset`, Lazy Loading, Schriften vorgeladen, kein Tracking, keine Cookies.
- Eigene Titel und Beschreibungen je Seite, Canonical, Open Graph, `sitemap.xml`, strukturierte Daten
  (`LocalBusiness` mit belegten Angaben: Adresse, Telefon, Bring-/Abholzeiten, Preise, Inhaberin; Breadcrumbs).

## Geprüft (18.10.2026)

- Desktop 1440 px und Handy 390 px in Edge, alle 18 Seiten ohne Konsolenfehler.
- Linkcheck: 2614 Verweise (Links, Bilder, srcset, Anker) ohne Fehler, externe Links erreichbar.
- Anfrage- und Anmeldeformular (alle 6 Schritte, Pflichtfelder, Hinweis unkastrierte Rüden), Versand an den
  Testserver, Ausweichweg bei Fehler, Preisrechner inkl. Übernahme ins Anfrageformular, Galerie-Filter,
  Lightbox, Handy-Menü, Ansicht «Bewegung reduzieren».
- Nicht geprüft: echter E-Mail-Versand über `api/anfrage.php` (lokal kein PHP), Safari/iOS-Gerät.

## Vor dem Livegang klären

1. **E-Mail-Adresse für Formulare:** Auf der alten Seite ist keine E-Mail veröffentlicht (nur Jimdo-Formular).
   Adresse in `api/config.php` eintragen, PHP-Hosting mit `mail()` sicherstellen, Absender `website@…` per SPF/DKIM
   erlauben und einmal live testen.
2. **Impressum und Datenschutz:** Beide neu verfasst (die alte Datenschutzerklärung beschrieb Google Analytics und
   reCAPTCHA, die nicht mehr verwendet werden). Bitte rechtlich prüfen; Hosting-Anbieter ggf. namentlich nennen.
3. **Widersprüche auf der alten Seite** (unverändert übernommen):
   - News 2018: «auch Hunde aufnehmen, welche nicht geimpft sind» ↔ AGB: «Ferienhunde müssen die nasale
     Zwingerhusten-Impfung vorweisen».
   - Angebot: «keine … läufigen Hündinnen» ↔ AGB: 20 % Zuschlag, wenn eine Hündin läufig gebracht wird oder wird.
   - AGB nennen an einer Stelle noch «harmony dog».
4. **Preisliste «Feiertage CHF 20.– pro Tag»:** Im Rechner als Zuschlag pro Feiertag gerechnet – bitte bestätigen.
5. **«Aktuell nur kleine Hunde»:** Gibt es eine Grenze (Gewicht/Grösse)? Hinweis bei Bedarf in `SITE["notice"]` ändern
   oder entfernen.
6. **Betriebsferien 2027** sind noch nicht bekannt – ergänzen, sobald festgelegt (die Seite zeigt automatisch,
   dass alle Ferien 2026 vorbei sind).
7. **Online-Anmeldung:** Das PDF verlangt eine Unterschrift. Klären, ob die Online-Anmeldung genügt oder das
   unterschriebene PDF zusätzlich nötig ist (Text dann im Formular ergänzen).
8. **Fotos:** Das Foto auf «Über mich» ist im Alt-Text als «Daniela Wulf mit drei Hunden» beschrieben – bitte
   bestätigen. Fotos der Gasthunde sind gemäss AGB (Fotos/Videos) freigegeben.
9. **Name:** Die alten Seitentitel lauten noch «harmony-dog Waltenschwil». Neu überall «Hundepension im Park»,
   «harmony-dog» nur noch als früherer Name (Werdegang, strukturierte Daten). OK?
10. **Umzug von Jimdo:** Hosting wählen (Apache empfohlen, `.htaccess` liegt bei), Domain umziehen, danach
    Sitemap in der Google Search Console einreichen. Ordner `_original/` und `tools/` nicht hochladen
    (werden sonst per `.htaccess` gesperrt). Die Ordner mit Umlauten (`über-mich`, `öffnungszeiten`) müssen als
    UTF-8 übertragen werden (FTP-Programm auf UTF-8 stellen).
11. **Bewertungen / Social Media:** Auf der alten Seite gibt es weder Bewertungen noch Social-Media-Profile
    (nur Teilen-Knöpfe) – daher bewusst weggelassen. Echte Google-Bewertungen lassen sich später ergänzen.
12. **Pflegehunde und Links:** Inhalte sind sehr knapp (keine Pflegehunde, ein Link) – bei Bedarf ausbauen.
