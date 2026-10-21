# Website online stellen – von A bis Z

Für einen frisch installierten Server mit **Ubuntu 22.04**. Dauer: etwa 15 Minuten.

**Du brauchst:**
- die **IP-Adresse** des Servers und das **root-Passwort** (oder einen SSH-Schlüssel), beides vom Hosting-Anbieter
- Zugriff auf die **DNS-Einstellungen** der Domain
- eine E-Mail-Adresse für das HTTPS-Zertifikat (nur für Hinweise von Let's Encrypt)

Der Code liegt auf GitHub: **https://github.com/real-Schelzi/hundepension**

---

## Schritt 1 – Domain auf den Server zeigen lassen

Beim Domain-Anbieter in den DNS-Einstellungen diese zwei Einträge setzen (`123.45.67.89` = IP deines Servers):

| Typ | Name | Wert |
|---|---|---|
| A | `@` (oder leer) | `123.45.67.89` |
| A | `www` | `123.45.67.89` |

- Alte **AAAA-Einträge** (IPv6) und alte A-Einträge für `@` und `www` löschen, sonst klappt HTTPS nicht.
- Die Änderung braucht meist 5–60 Minuten. Du kannst in der Zwischenzeit schon mit Schritt 2 weitermachen.

> **Achtung bei hundepension-im-park.ch:** Die Domain zeigt im Moment noch auf die alte Jimdo-Seite. Sobald du den
> DNS-Eintrag änderst, ist die alte Seite weg. Das erst machen, wenn die Kundin einverstanden ist.
> Zum Testen vorher eine eigene Subdomain nehmen (z. B. `hundepension.deine-domain.ch`) oder die Seite über die
> IP-Adresse ansehen (`http://123.45.67.89`).

---

## Schritt 2 – Auf dem Server einloggen

Unter Windows **PowerShell** öffnen und eingeben (IP ersetzen):

```bash
ssh root@123.45.67.89
```

Beim ersten Mal mit `yes` bestätigen, dann das Passwort eingeben (es wird beim Tippen nicht angezeigt).

---

## Schritt 3 – Installieren (drei Befehle)

Nacheinander auf dem Server eingeben. Im letzten Befehl Domain und E-Mail anpassen:

```bash
sudo apt update && sudo apt install -y git
```

```bash
sudo git clone https://github.com/real-Schelzi/hundepension.git /var/www/hundepension
```

```bash
sudo bash /var/www/hundepension/deploy/install.sh hundepension-im-park.ch deine@email.ch
```

Das Skript erledigt alles selbst:

1. System aktualisieren, Apache, PHP und Certbot installieren
2. Firewall einschalten (nur SSH, HTTP und HTTPS offen)
3. Dateirechte setzen
4. Apache für die Website einrichten (interne Ordner wie `.git`, `tools`, `deploy` und die Anleitungen sind gesperrt)
5. prüfen, ob die Domain schon auf den Server zeigt
6. HTTPS-Zertifikat von Let's Encrypt holen, http automatisch auf https umleiten, automatische Verlängerung prüfen

**Zeigt die Domain noch nicht auf den Server**, hört das Skript nach Punkt 5 freundlich auf. Die Website ist dann
schon unter `http://IP-des-Servers` erreichbar. Sobald der DNS-Eintrag aktiv ist, den dritten Befehl einfach
**nochmals** ausführen – er holt dann das Zertifikat.

---

## Schritt 4 – Testen

- `https://hundepension-im-park.ch` im Browser öffnen → Schloss-Symbol in der Adresszeile
- `http://hundepension-im-park.ch` muss automatisch auf `https://` wechseln
- Ein paar Unterseiten anklicken, z. B. `/über-mich/` und `/preise/`

Das Zertifikat verlängert sich automatisch alle 60–90 Tage. Du musst dafür nichts tun.

---

## Schritt 5 – E-Mail für die Formulare (empfohlen)

Damit Anfragen und Online-Anmeldungen per E-Mail ankommen, das Postfach eines Mail-Anbieters verbinden:

```bash
sudo bash /var/www/hundepension/deploy/mail-setup.sh
```

Das Skript fragt nach Empfängeradresse, SMTP-Server, Benutzer und Passwort und schickt danach eine Test-Mail.

| Anbieter | SMTP-Server | Port |
|---|---|---|
| Infomaniak | `mail.infomaniak.com` | 587 |
| Hostpoint | `asmtp.mail.hostpoint.ch` | 587 |
| Gmail | `smtp.gmail.com` | 587 (nur mit **App-Passwort**, Zwei-Faktor-Anmeldung muss aktiv sein) |

Solange das nicht eingerichtet ist, funktionieren die Formulare trotzdem: Die Website bietet dann an, die fertige
Anfrage per SMS zu schicken, den Text zu kopieren oder anzurufen.

---

## Später: Änderungen veröffentlichen

**Auf dem PC** (im Projektordner `hundepension-redesign`, z. B. in Git Bash oder PowerShell):

```bash
python tools/build_pages.py
```

```bash
git add -A
```

```bash
git commit -m "Kurz beschreiben, was geändert wurde"
```

```bash
git push
```

**Auf dem Server:**

```bash
sudo bash /var/www/hundepension/deploy/update.sh
```

---

## Hilfe bei Problemen

| Problem | Lösung |
|---|---|
| `ssh: connect … timed out` | IP prüfen; beim Hosting-Anbieter schauen, ob eine Firewall Port 22 sperrt |
| Website lädt nicht | In der Firewall des Hosting-Anbieters (z. B. Hetzner/OVH «Cloud-Firewall») Port 80 und 443 öffnen; Status: `sudo systemctl status apache2` |
| Zertifikat scheitert | DNS prüfen auf https://dnschecker.org (A-Eintrag = Server-IP, kein fremder AAAA-Eintrag), etwas warten, Installationsbefehl nochmals ausführen |
| Fehlerseite oder 403 | Letzte Fehler ansehen: `sudo tail -n 30 /var/log/apache2/hundepension-error.log` |
| Update bricht ab | Es wurde direkt auf dem Server etwas geändert. GitHub-Stand übernehmen: `cd /var/www/hundepension && sudo git reset --hard origin/main` (die Mail-Einstellungen bleiben erhalten) |
| Test-Mail kommt nicht an | Spam-Ordner prüfen; Details: `sudo journalctl -t msmtp -n 20` |

---

## Gut zu wissen

- **Das GitHub-Repo ist öffentlich.** Alle Dateien, auch `README.md` mit den offenen Punkten, sind für alle sichtbar.
  Passwörter oder Mail-Zugangsdaten liegen nie im Repo (sie stehen nur auf dem Server in `/etc/msmtprc` und
  `api/config.local.php`).
- **Lieber privat?** Auf GitHub unter *Settings → General → Change visibility* auf *Private* stellen. Der Server
  braucht dann einen Lese-Schlüssel:
  ```bash
  sudo ssh-keygen -t ed25519 -N "" -f /root/.ssh/id_ed25519
  ```
  ```bash
  sudo cat /root/.ssh/id_ed25519.pub
  ```
  Die angezeigte Zeile auf GitHub unter *Settings → Deploy keys → Add deploy key* einfügen (ohne Schreibrecht), dann:
  ```bash
  sudo git -C /var/www/hundepension remote set-url origin git@github.com:real-Schelzi/hundepension.git
  ```
  Bei einer neuen Installation statt der `https://…`-Adresse gleich `git@github.com:real-Schelzi/hundepension.git` klonen.
- Die Sicherung der alten Jimdo-Seite (`_original/`, 234 MB) ist absichtlich **nicht** auf GitHub. Sie bleibt nur auf dem PC.
