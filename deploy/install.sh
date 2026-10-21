#!/usr/bin/env bash
# =============================================================================
#  Hundepension im Park – Server-Installation für Ubuntu 22.04
#
#  Installiert Apache und PHP, richtet die Website ein, schaltet die Firewall
#  ein und holt ein kostenloses HTTPS-Zertifikat (Let's Encrypt, verlängert
#  sich automatisch). Kann gefahrlos mehrmals ausgeführt werden.
#
#  Aufruf:   sudo bash deploy/install.sh <domain> <e-mail>
#  Beispiel: sudo bash /var/www/hundepension/deploy/install.sh hundepension-im-park.ch info@example.ch
#
#  Die E-Mail-Adresse braucht Let's Encrypt nur für Hinweise zum Zertifikat.
# =============================================================================
set -euo pipefail

DOMAIN="${1:-}"
EMAIL="${2:-}"
WEBROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SITE=hundepension

schritt() { printf '\n\033[1;32m==> %s\033[0m\n' "$*"; }
hinweis() { printf '\033[1;33m%s\033[0m\n' "$*"; }
fehler()  { printf '\033[1;31m%s\033[0m\n' "$*"; }

if [[ $EUID -ne 0 ]]; then
  fehler "Bitte mit sudo starten:  sudo bash $0 <domain> <e-mail>"; exit 1
fi
if [[ -z "$DOMAIN" || -z "$EMAIL" ]]; then
  fehler "Aufruf:  sudo bash $0 <domain> <e-mail>"
  fehler "Beispiel: sudo bash $0 hundepension-im-park.ch info@example.ch"; exit 1
fi
# Domain säubern (https://, www., Schrägstriche entfernen)
DOMAIN="${DOMAIN#http://}"; DOMAIN="${DOMAIN#https://}"; DOMAIN="${DOMAIN#www.}"; DOMAIN="${DOMAIN%%/*}"

# ---------------------------------------------------------------------------
schritt "1/6  System aktualisieren und Programme installieren"
export DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a
APT_OPTS=(-yq -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold)
apt-get update -q
apt-get upgrade "${APT_OPTS[@]}"
apt-get install "${APT_OPTS[@]}" apache2 php libapache2-mod-php php-mbstring git curl \
  certbot python3-certbot-apache ufw unattended-upgrades
timedatectl set-timezone Europe/Zurich || true

# ---------------------------------------------------------------------------
schritt "2/6  Firewall einschalten (SSH, HTTP, HTTPS)"
ufw allow OpenSSH >/dev/null
ufw allow 'Apache Full' >/dev/null
ufw --force enable >/dev/null
ufw status | sed -n '1,10p'

# ---------------------------------------------------------------------------
schritt "3/6  Dateirechte setzen"
chown -R root:root "$WEBROOT"
find "$WEBROOT" -path "$WEBROOT/.git" -prune -o -type d -exec chmod 755 {} +
find "$WEBROOT" -path "$WEBROOT/.git" -prune -o -type f -exec chmod 644 {} +
echo "Website-Ordner: $WEBROOT"

# ---------------------------------------------------------------------------
schritt "4/6  Apache einrichten"
a2enmod rewrite headers deflate mime expires >/dev/null

SERVER_IP="$(curl -4 -s --max-time 10 https://api.ipify.org || true)"
DOMAIN_IP="$(getent ahostsv4 "$DOMAIN" | awk 'NR==1{print $1}' || true)"
WWW_IP="$(getent ahostsv4 "www.$DOMAIN" | awk 'NR==1{print $1}' || true)"
WWW=""
if [[ -n "$WWW_IP" && "$WWW_IP" == "$SERVER_IP" ]]; then WWW="www.$DOMAIN"; fi

cat > "/etc/apache2/sites-available/$SITE.conf" <<EOF
<VirtualHost *:80>
    ServerName $DOMAIN
    ${WWW:+ServerAlias $WWW}
    DocumentRoot $WEBROOT

    <Directory $WEBROOT>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    # Interne Ordner und Dateien nie ausliefern
    RedirectMatch 404 /\.git
    RedirectMatch 404 ^/(_original|tools|deploy)(/|\$)
    RedirectMatch 404 ^/[^/]+\.md\$

    ErrorLog \${APACHE_LOG_DIR}/$SITE-error.log
    CustomLog \${APACHE_LOG_DIR}/$SITE-access.log combined
</VirtualHost>
EOF
a2ensite "$SITE" >/dev/null
a2dissite 000-default >/dev/null 2>&1 || true
apache2ctl configtest
systemctl reload apache2
echo "Apache läuft. Website schon jetzt erreichbar unter: http://${SERVER_IP:-<server-ip>}"

# ---------------------------------------------------------------------------
schritt "5/6  DNS prüfen"
echo "IP dieses Servers:        ${SERVER_IP:-unbekannt}"
echo "$DOMAIN zeigt auf:        ${DOMAIN_IP:-(noch nichts)}"
echo "www.$DOMAIN zeigt auf:    ${WWW_IP:-(noch nichts)}"
if [[ -z "$DOMAIN_IP" || ( -n "$SERVER_IP" && "$DOMAIN_IP" != "$SERVER_IP" ) ]]; then
  hinweis ""
  hinweis "Die Domain zeigt noch nicht auf diesen Server – HTTPS wird darum noch nicht eingerichtet."
  hinweis "1. Beim Domain-Anbieter einen A-Eintrag setzen:  @  und  www  ->  ${SERVER_IP:-<server-ip>}"
  hinweis "2. Warten, bis der Eintrag aktiv ist (meist 5–60 Minuten)."
  hinweis "3. Dieses Skript nochmals starten:  sudo bash $0 $DOMAIN $EMAIL"
  exit 0
fi
[[ -z "$WWW" ]] && hinweis "Hinweis: www.$DOMAIN zeigt nicht auf diesen Server – Zertifikat nur für $DOMAIN."
# Alter IPv6-Eintrag (AAAA) auf einen anderen Server lässt Let's Encrypt scheitern
SERVER_IP6="$(curl -6 -s --max-time 6 https://api6.ipify.org || true)"
DOMAIN_IP6="$(getent ahostsv6 "$DOMAIN" | awk '$1 !~ /^::ffff:/ {print $1; exit}' || true)"
if [[ -n "$DOMAIN_IP6" && "$DOMAIN_IP6" != "$SERVER_IP6" ]]; then
  hinweis "Achtung: $DOMAIN hat einen IPv6-Eintrag (AAAA) auf $DOMAIN_IP6, der nicht zu diesem Server gehört."
  hinweis "Bitte diesen AAAA-Eintrag beim Domain-Anbieter löschen (oder auf ${SERVER_IP6:-die IPv6 des Servers} setzen),"
  hinweis "sonst kann das Zertifikat nicht ausgestellt werden."
fi

# ---------------------------------------------------------------------------
schritt "6/6  HTTPS-Zertifikat holen (Let's Encrypt)"
CERT_ARGS=(-d "$DOMAIN")
[[ -n "$WWW" ]] && CERT_ARGS+=(-d "$WWW")
if ! certbot --apache --non-interactive --agree-tos --no-eff-email -m "$EMAIL" \
  "${CERT_ARGS[@]}" --redirect --keep-until-expiring; then
  fehler "Das Zertifikat konnte nicht ausgestellt werden. Häufige Ursachen:"
  fehler " - DNS zeigt noch nicht (überall) auf diesen Server – etwas warten und erneut starten"
  fehler " - alter AAAA-Eintrag (IPv6) beim Domain-Anbieter"
  fehler " - Port 80/443 in einer Firewall des Hosting-Anbieters gesperrt (z. B. Hetzner/OVH Cloud-Firewall)"
  fehler "Danach einfach nochmals:  sudo bash $0 $DOMAIN $EMAIL"
  exit 1
fi
systemctl enable --now certbot.timer >/dev/null 2>&1 || true
if certbot renew --dry-run -q; then echo "Automatische Verlängerung getestet: OK"; fi

schritt "Fertig!  https://$DOMAIN"
echo "Updates von GitHub holen:      sudo bash $WEBROOT/deploy/update.sh"
echo "E-Mail-Versand einrichten:     sudo bash $WEBROOT/deploy/mail-setup.sh"
