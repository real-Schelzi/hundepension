#!/usr/bin/env bash
# =============================================================================
#  Hundepension im Park – E-Mail-Versand der Formulare einrichten (optional)
#
#  Die Formulare schicken Anfragen über das SMTP-Postfach eures Mail-Anbieters
#  (z. B. Infomaniak, Hostpoint, Gmail mit App-Passwort). Das Skript fragt alles
#  ab, schreibt die Einstellungen und schickt eine Test-Mail.
#
#  Aufruf:  sudo bash /var/www/hundepension/deploy/mail-setup.sh
# =============================================================================
set -euo pipefail
WEBROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ $EUID -ne 0 ]]; then echo "Bitte mit sudo starten:  sudo bash $0"; exit 1; fi

ist_mail() { [[ "$1" =~ ^[^[:space:]@\'\"]+@[^[:space:]@\'\"]+\.[A-Za-z]{2,}$ ]]; }

echo "E-Mail-Versand für die Formulare einrichten"
echo "-------------------------------------------"
read -rp "An welche Adresse sollen Anfragen und Anmeldungen gehen? " TO
ist_mail "$TO" || { echo "Ungültige Adresse."; exit 1; }
read -rp "SMTP-Server (z. B. mail.infomaniak.com, asmtp.mail.hostpoint.ch, smtp.gmail.com): " HOST
read -rp "SMTP-Port [587]: " PORT; PORT="${PORT:-587}"
read -rp "SMTP-Benutzer / Postfach-Adresse: " SMTP_USER
ist_mail "$SMTP_USER" || { echo "Bitte die vollständige Postfach-Adresse angeben."; exit 1; }
read -rsp "SMTP-Passwort (wird nicht angezeigt): " PASS; echo

export DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a
apt-get install -yq msmtp msmtp-mta ca-certificates >/dev/null

STARTTLS=on; [[ "$PORT" == "465" ]] && STARTTLS=off
PASS_ESC="${PASS//\\/\\\\}"; PASS_ESC="${PASS_ESC//\"/\\\"}"
umask 027
cat > /etc/msmtprc <<EOF
# Erzeugt von deploy/mail-setup.sh
defaults
auth           on
tls            on
tls_starttls   $STARTTLS
tls_trust_file /etc/ssl/certs/ca-certificates.crt
syslog         LOG_MAIL

account default
host     $HOST
port     $PORT
from     $SMTP_USER
user     $SMTP_USER
password "$PASS_ESC"
EOF
chown root:www-data /etc/msmtprc
chmod 640 /etc/msmtprc
umask 022

# Serverspezifische Formular-Einstellungen (nicht im Git, siehe .gitignore)
cat > "$WEBROOT/api/config.local.php" <<EOF
<?php
// Erzeugt von deploy/mail-setup.sh – überschreibt Werte aus config.php
return [
    'empfaenger' => '$TO',
    'absender'   => '$SMTP_USER',
];
EOF
chmod 644 "$WEBROOT/api/config.local.php"

echo
echo "Sende Test-Mail an $TO …"
if printf 'To: %s\nFrom: %s\nSubject: Test Website Hundepension im Park\n\nDer E-Mail-Versand der Website funktioniert.\n' "$TO" "$SMTP_USER" \
   | sudo -u www-data msmtp -t; then
  echo "OK – bitte Posteingang (und Spam-Ordner) prüfen. Die Formulare senden ab sofort per E-Mail."
else
  echo "Versand fehlgeschlagen. Häufige Gründe: falsches Passwort, Gmail ohne App-Passwort, Port gesperrt."
  echo "Details:  sudo journalctl -t msmtp -n 20"
  exit 1
fi
