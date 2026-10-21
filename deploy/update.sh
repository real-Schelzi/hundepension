#!/usr/bin/env bash
# =============================================================================
#  Hundepension im Park – neueste Version von GitHub auf den Server holen
#  Aufruf:  sudo bash /var/www/hundepension/deploy/update.sh
# =============================================================================
set -euo pipefail
WEBROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ $EUID -ne 0 ]]; then echo "Bitte mit sudo starten:  sudo bash $0"; exit 1; fi
cd "$WEBROOT"

echo "Vorher:  $(git log -1 --format='%h  %ad  %s' --date=format:'%d.%m.%Y %H:%M')"
if ! git pull --ff-only --quiet; then
  echo
  echo "Update abgebrochen: Auf dem Server wurden Dateien direkt geändert."
  echo "Anzeigen mit:  cd $WEBROOT && git status"
  echo "Änderungen verwerfen und GitHub-Stand übernehmen:  cd $WEBROOT && sudo git reset --hard origin/main"
  exit 1
fi
echo "Jetzt:   $(git log -1 --format='%h  %ad  %s' --date=format:'%d.%m.%Y %H:%M')"

find "$WEBROOT" -path "$WEBROOT/.git" -prune -o -type d -exec chmod 755 {} +
find "$WEBROOT" -path "$WEBROOT/.git" -prune -o -type f -exec chmod 644 {} +
systemctl reload apache2
echo "Fertig – die Website ist aktuell."
