"""Alle Inhalte der Website an einer Stelle (übernommen von hundepension-im-park.ch, Stand Oktober 2026).

Änderungen an Preisen, Zeiten, Betriebsferien oder Texten hier vornehmen und danach
`python tools/build_pages.py` ausführen.
"""

SITE = {
    "name": "Hundepension im Park",
    "tagline": "Betreuung mit Herz",
    "owner": "Daniela Wulf",
    "street": "Bahnhofstrasse 1",
    "zip": "5622",
    "city": "Waltenschwil",
    "canton": "AG",
    "phone_display": "079 355 68 82",
    "phone_tel": "+41793556882",
    "email": "",  # Auf der alten Seite nicht veröffentlicht – bei Bedarf ergänzen
    "domain": "https://www.hundepension-im-park.ch",
    "permit": "25.049",
    "fba_permit": "12/0023",
    "notice": "Aktuell können wir nur kleine Hunde aufnehmen.",
}

FACTS = [
    ("3000", "m²", "sicher eingezäuntes Gelände mit altem Baumbestand"),
    ("12", "Plätze", "für Tages- und Feriengäste"),
    ("12", "Boxen", "im speziell ausgebauten Fahrzeug für die Fahrt ins Grüne"),
    ("25.049", "Bewilligung", "vetamtlich geprüfte Betreuung"),
]

# Tagesablauf (Seite „Angebot“) – Zeiten 1:1 vom Original
DAY = [
    {
        "id": "ankommen", "from": "06:30", "to": "08:30", "title": "Ankommen",
        "text": "Zwischen 06.30 und 08.30 Uhr treffen die Tagesgäste ein. Gebracht und abgeholt wird "
                "von Montag bis Freitag – samstags von 08.00 bis 08.30 Uhr.",
        "photos": ["impressionen-31", "impressionen-61", "impressionen-35"],
        "cam": [0.43, 0.50, 1.55],
    },
    {
        "id": "spazieren", "from": "09:00", "to": "11:30", "title": "Spazieren in gestaffelten Gruppen",
        "text": "Abwechslungsreiche Spaziergänge führen durch die nahegelegenen, wunderschönen Wälder. "
                "Für die sichere Fahrt ins Grüne steht ein speziell ausgebautes Fahrzeug mit 12 Boxen bereit.",
        "photos": ["impressionen-17", "impressionen-32", "impressionen-25"],
        "cam": [0.74, 0.30, 1.22],
    },
    {
        "id": "mittag", "from": "12:00", "to": None, "title": "Mittagessen",
        "text": "Die Fütterung erfolgt einzeln, damit jeder Hund in Ruhe und ohne Stress fressen kann. "
                "Das Futter bringt ihr selber mit – auf Wunsch füttern wir gegen Aufpreis auch Navita.",
        "photos": ["impressionen-50", "impressionen-02", "impressionen-36"],
        "cam": [0.42, 0.46, 1.85],
    },
    {
        "id": "ruhe", "from": "12:30", "to": "14:00", "title": "Ruhepause",
        "text": "Diverse Ruhe- und Rückzugsmöglichkeiten im Haus stehen allen Hunden jederzeit frei zur Verfügung – "
                "vom Hundekissen am Ofen bis zur Höhle am Fenster.",
        "photos": ["unser-zuhause-06", "impressionen-38", "unser-zuhause-09"],
        "cam": [0.38, 0.47, 2.05],
    },
    {
        "id": "freilauf", "from": "14:00", "to": "16:00", "title": "Freilauf im Park",
        "text": "3000 m² sicher eingezäuntes Gelände: Kiesplatz, kleiner und grosser Badeteich, Erdhügel mit Tunnel "
                "und eine überdachte, erhöhte Liegefläche aus Holz, die bei jedem Wetter Schutz bietet.",
        "photos": ["angebot-01", "impressionen-57", "rudel-37"],
        "cam": [0.66, 0.60, 1.32],
    },
    {
        "id": "heimweg", "from": "16:00", "to": "18:30", "title": "Glücklich und müde nach Hause",
        "text": "Zwischen 16.00 und 18.30 Uhr geht es dann wieder glücklich und müde nach Hause.",
        "photos": ["impressionen-59", "rudel-23", "impressionen-27"],
        "cam": [0.50, 0.52, 1.08],
    },
    {
        "id": "abend", "from": None, "to": None, "title": "Und die Feriengäste?",
        "text": "Sie bleiben über Nacht – mit liebevollem Familienanschluss und artgerechtem Rudelleben, "
                "das den Hunden sozialen Kontakt und Geborgenheit schenkt.",
        "photos": ["unser-zuhause-11", "impressionen-41", "impressionen-60"],
        "cam": [0.44, 0.47, 1.45],
    },
]

PRICES = [
    {"id": "tag", "title": "Tagesbetreuung", "price": 60, "unit": "pro Tag", "note": "Bringen 06.30–08.30, abholen 16.00–18.30 Uhr"},
    {"id": "ferien-fix", "title": "Feriengäste mit Tagesplatz", "price": 70, "unit": "pro Tag", "note": "für Hunde mit wöchentlichem Fixtag"},
    {"id": "ferien", "title": "Feriengäste ohne Tagesplatz", "price": 80, "unit": "pro Tag", "note": "Ferienbetreuung mit Übernachtung"},
]
EXTRAS = [
    {"id": "feiertag", "title": "Feiertage", "price": 20, "unit": "pro Tag"},
    {"id": "welpe", "title": "Welpen-Zuschlag", "price": 10, "unit": "pro Tag"},
    {"id": "integration", "title": "Rudelintegration", "price": 100, "unit": "einmalig"},
]
CONDITIONS = [
    "Ein- und Austrittstag werden zu 100 % verrechnet.",
    "Tagesgäste können 24 h vor Betreuungsbeginn kostenlos abgemeldet werden. Spätere Stornierungen oder "
    "verpasste Termine werden komplett verrechnet.",
    "Ferienhunde müssen mindestens 7 Tage vor Betreuungsbeginn abgemeldet werden, ansonsten werden 50 % davon "
    "in Rechnung gestellt.",
    "Bei Ferienaufenthalten ist eine Vorkasse von 100 % des Betrages vor Ferienantritt zu leisten (AGB).",
]

HOURS = {
    # ISO-Wochentag (1 = Montag) -> Zeitfenster
    "weekdays": [["06:30", "08:30"], ["16:00", "18:30"]],
    "saturday": [["08:00", "08:30"]],
    "sunday": [],
}
HOURS_ROWS = [
    ("Montag bis Freitag", "06.30–08.30 Uhr", "16.00–18.30 Uhr"),
    ("Samstag", "08.00–08.30 Uhr", None),
    ("Sonn- und Feiertage", "geschlossen", None),
]

FERIEN = [
    {"label": "Winterferien", "from": "2026-01-31", "to": "2026-02-08", "text": "31. Januar – 08. Februar 2026"},
    {"label": "Wochenende", "from": "2026-06-12", "to": "2026-06-14", "text": "12. Juni – 14. Juni 2026"},
    {"label": "Sommerferien", "from": "2026-07-04", "to": "2026-07-19", "text": "04. Juli – 19. Juli 2026"},
    {"label": "Herbstferien", "from": "2026-09-26", "to": "2026-10-04", "text": "26. September – 04. Oktober 2026"},
]

ADMISSION = [
    "Aktuell können wir nur kleine Hunde aufnehmen.",
    "Aufgenommen werden sozialisierte Hunde ab 16 Wochen, die keine Aggressions- oder Verhaltensauffälligkeiten zeigen.",
    "Leider nehmen wir keine unkastrierten Rüden oder läufigen Hündinnen auf.",
    "Hunde, die im Kanton Zürich oder Aargau als Listenhunde eingetragen sind, können wir nicht aufnehmen.",
    "Ferienhunde müssen die nasale Zwingerhusten-Impfung vorweisen.",
]

PARK = [
    # (Titel, Text, Bild oder None, Grösse)
    ("Erhöhte Liegefläche aus Holz", "Überdacht und erhöht – Schutz bei jedem Wetter und der Lieblingsplatz des Rudels.", "news-02", "xl"),
    ("Alter Baumbestand", "Umgeben von alten Bäumen, Büschen und Wiesen finden die Vierbeiner eine naturnahe, abwechslungsreiche Umgebung.", "unser-zuhause-02", "lg"),
    ("Outdoor-Lounges", "Gemütliche Loungeplätze im Garten – zum Sonnen, Dösen und Beobachten.", "impressionen-54", "md"),
    ("Rückzug im Haus", "Ruhe- und Rückzugsmöglichkeiten im Haus, allen Hunden jederzeit frei zugänglich.", "unser-zuhause-07", "md"),
    ("Wälder ganz in der Nähe", "Abwechslungsreiche Spaziergänge durch die nahegelegenen Wälder – mit neuen Eindrücken für jede Nase.", "impressionen-17", "md"),
]
ADVENTURE = ["Kiesplatz", "Kleiner & grosser Badeteich", "Erdhügel mit Tunnel", "Holzstämme", "Biowaldboden", "Sandplatz"]

WERDEGANG = [
    ("2000 – 2015", "Dekorationsatelier bei der Firma PKZ", None),
    ("2006 – 2007", "Kurse bei Shante – Wicohan", "Tierkommunikation, Energiearbeit, Seelenbilder, Aura Soma"),
    ("2014", "SKN", None),
    ("2015", "Fachspezifische berufsunabhängige Ausbildung (FBA)", "Bewilligungs-Nr.: 12/0023"),
    ("2016", "Eröffnung Hundepension harmony-dog", None),
    ("2017", "Seminar Dog-Psychology-Center Frankreich – «Hündisch lernen» (Markus Habermann)",
     "Körpersprache von Mensch und Hund · Mit der richtigen Energie arbeiten · Artgerechtes Leben für den Hund · Rangordnung im Rudel"),
    ("2026", "Neueröffnung Hundepension im Park", None),
]

NEWS = [
    {
        "year": "2026", "title": "Unser Garten wird neu gestaltet",
        "text": "Ein Adventure-Park mit verschiedenen Böden wie Biowaldboden, Sand- und Kiesplatz. Erhöhter Liegeplatz "
                "aus Holz. Grösserer Teich für Abkühlungen im Sommer. Erdhügel mit Tunnel und Holzstämme, alles aus "
                "natürlichen Materialien.",
        "photos": ["news-01", "news-02", "news-03"],
        "caption": "Der erhöhte Liegeplatz ist fast fertig. Die Hunde lieben ihn jetzt schon.",
    },
    {
        "year": "2018", "title": "Auch ungeimpfte Hunde willkommen",
        "text": "Wir haben uns entschieden, auch Hunde aufzunehmen, welche nicht geimpft sind. Da wir unsere Hunde selbst "
                "auch nicht mehr impfen. Somit überlasse ich jedem die freie Wahl.",
        "photos": [],
        "caption": None,
    },
]

AGB = [
    ("Allgemeine Bestimmungen", [
        "Hundepension im Park verpflichtet sich, die übertragenen Aufgaben vollends und mit bestem Wissen und Gewissen "
        "sowie mit der gebührenden Sorgfalt und Kompetenz zu erfüllen. Der Auftraggeber verpflichtet sich, uns über alles "
        "Notwendige zu informieren und entsprechend zu instruieren (Bsp. Allergien, Krankheiten, Verhaltensstörungen, etc.).",
    ]),
    ("Zahlungsbedingungen / Annulation", [
        "Es gelten die bekannten Tarife. Preisänderungen können jederzeit vorgenommen werden. Bei Ferienaufenthalten ist "
        "eine Vorkasse von 100% des Betrages vor Ferienantritt zu leisten. Der Tag der An- und Abreise wird vollumfänglich verrechnet.",
        "Tagesgäste können 24h vor Betreuungsbeginn kostenlos abgemeldet werden. Spätere Stornierungen oder auch verpasste "
        "Termine werden komplett verrechnet. Ferienhunde müssen mindestens 7 Tage vor Betreuungsbeginn abgemeldet werden, "
        "ansonsten wird 50% der Leistung in Rechnung gestellt. Der Auftraggeber verpflichtet sich uns unverzüglich zu "
        "informieren, wenn er nicht zum vereinbarten Termin zurückkehrt. Bei Notfällen resp. nicht auftragsgemässer "
        "Beendigung des Vertrages, verbleibt das Tier gegen nachträgliche Verrechnung der bekannten Tarife automatisch in unserer Betreuung.",
        "Die Kosten für ärztliche Leistungen inklusive Tiertransport und Nebenkosten werden vom Auftraggeber selbst getragen.",
    ]),
    ("Tages- und Ferienbetreuung", [
        "Es werden nur sozialisierte Hunde ab 16 Wochen aufgenommen, die keine Aggressions- oder Verhaltensauffälligkeiten "
        "zeigen. Wir behalten uns das Recht vor, aggressive oder sehr ängstliche Hunde abzulehnen. Die Aufnahme von Hunden, "
        "die im Kanton Zürich und Aargau als Listenhunde eingetragen sind, können wir nicht aufnehmen.",
        "Ferienhunde müssen die Nasale Zwingerhusten Impfung vorweisen.",
        "Über allfällige Krankheitserscheinungen oder Läufigkeit müssen wir informiert werden. Wird eine Hündin läufig zu "
        "uns in die Ferien gegeben oder wird während der Ferienzeit läufig, verrechnen wir für den Mehraufwand 20% zusätzlich.",
    ]),
    ("Haftung im Schadenfall", [
        "Der Auftraggeber besitzt eine rechtsgültige Haftpflichtversicherung, in der sein Hund miteingeschlossen ist und eine "
        "volle Leistung bei Fremdhütung garantiert. Hundepension im Park haftet nur gegenüber Schäden, welche durch sie selbst "
        "bei Auftragserfüllung aufgrund klarer Sorgfaltspflichtverletzung entstanden sind. Dies ausschliesslich im Rahmen der "
        "von uns abgeschlossenen Haftpflichtversicherung. Bei gebrechlichen, kranken oder operierten Hunden übernimmt die "
        "Betreuung keine Haftung für aufkommende Beschwerden. Wenn ein Hund eine nicht gemeldete Krankheit oder Seuche auf "
        "das Betreuungsgelände schleppt, müssen die anfallenden Behandlungskosten der anderen Hunde sowie allfällige "
        "Umsatzverluste vom Tierbesitzer übernommen werden. Für Krankheiten die nach dem Aufenthalt der Hundebetreuung "
        "auftreten, wird keine Haftung übernommen. Sollte trotz sorgfältiger Betreuung ein Tier während des Spaziergangs "
        "oder aus der Pension entweichen und trotz intensiver Suche nicht wieder gefunden werden, kann harmony dog nicht auf "
        "Schadensersatz verklagt werden. Alle vom Tier entstandenen Schäden, wie auch mitgegebenen Gegenstände, haftet der "
        "Auftraggeber. Bei nachweislichem Tiermisshandlungs-Verdacht behalten wir uns das Recht vor, entsprechende Massnahmen "
        "und Abklärungen einzuleiten und dem Tierbesitzer bei bestätigtem Verdacht das Tier nicht mehr auszuhändigen.",
    ]),
    ("Krankheit / Notfälle / Tierarzt", [
        "Sollte eine unerwünschte Empfängnis stattfinden, haften wir nicht für die entstandene Schwangerschaft und die Kosten "
        "fallen zu Lasten des Auftraggebers. Bei ansteckenden Krankheiten wie Bsp. Zwingerhusten oder Flöhen kann die "
        "Betreuung nicht gewährleistet werden. Sofern nicht durch Vollmachten oder sonstige Schreiben festgelegt, darf die "
        "Betreuung den Hund durch den Tierarzt seiner Wahl und durch alle erforderlichen Mittel versorgen lassen und ihn am "
        "Leben erhalten. Die Betreuung handelt in diesem Fall im Namen des Tierbesitzers.",
    ]),
    ("Fotos / Videos", [
        "Der Auftraggeber erklärt sich damit einverstanden, dass sämtliche bei uns entstandenen Fotos des Tieres auf unserer "
        "Webseite und in unseren sozialen Netzwerken zur Werbung genutzt werden dürfen.",
    ]),
    ("Schlussbestimmungen", [
        "Alle nicht definierten Bestimmungen unterliegen den gesetzlichen Bestimmungen. Gerichtsstand für alle sich aus dem "
        "Vertragsverhältnis ergebenden Streitigkeiten ist Muri Kanton Aargau.",
    ]),
]

# Seite 4 des Anmeldeformulars (PDF) – wird im Online-Formular zur Bestätigung angezeigt
ANMELDUNG_AGB = [
    "Der Hundebesitzer erklärt sich damit einverstanden, dass im Falle eines Unfalles oder einer Erkrankung des Hundes "
    "alle Bemühungen ohne Ansehen der Kosten durch einen Tierarzt erfolgen. Der Hundebesitzer übernimmt dafür die "
    "entstandenen Kosten vollumfänglich.",
    "Sollte der Verdacht auf eine Erkrankung bestehen, ist der Hundebesitzer verpflichtet, darauf hinzuweisen.",
    "Bitte beachten Sie auch, dass in unserer Pension Rudelhaltung betrieben wird. Es können somit aus Raufereien "
    "Verletzungen entstehen. Auch ist die Ansteckungsgefahr grösser als bei Einzelhaltung. Dafür können wir keine Haftung übernehmen.",
    "Für mitgebrachte Hundekissen oder Decken, Leinen, Halsbänder und Winterdecken wird nicht gehaftet. Defekte Sachen werden nicht ersetzt.",
    "Kündigung: jederzeit gegenseitig.",
]

# Ankreuzfelder aus dem PDF-Anmeldeformular
CHARAKTER = ["Jagt Wild", "Jagt Katzen", "Jagt Jogger / Fahrradfahrer", "Eher ängstlich", "Eher aggressiv",
             "Angstbeisser", "Kann nicht alleine sein", "Kann Türen öffnen", "Liebt Wasser", "Hat guten Gehorsam",
             "Mag Kinder", "Sozial mit anderen Hunden", "Rudelhaltung gewohnt", "Autofahren gewohnt"]
SCHLAF = ["Schläft im eigenen Korb", "Schläft in eigener Box", "Schläft bei uns im Bett",
          "Schläft vor oder neben unserem Bett", "Schläft in separatem Raum", "Schläft auf spezieller Decke"]
BESONDERHEITEN = ["Hat schon Personen/Hunde angegriffen oder bedroht", "Hat schon Personen oder Hunde gebissen",
                  "Wurde schon von anderen Hunden gebissen", "Leinenzwang auf Spaziergängen"]

LINKS = [("animal-happyend.ch", "http://www.animal-happyend.ch")]
