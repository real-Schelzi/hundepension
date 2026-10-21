<?php
/**
 * Formular-Endpunkt für Anfrage- und Anmeldeformular der Hundepension im Park.
 * Versand per PHP mail() an die Adresse aus config.php. Antwortet immer mit JSON.
 *
 * Schutz: Honeypot-Feld «website», Mindest-Ausfüllzeit, einfache Begrenzung pro IP.
 */
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex');

function antwort(int $status, array $data): void {
    http_response_code($status);
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    antwort(405, ['ok' => false, 'error' => 'Nur POST erlaubt.']);
}

$config = require __DIR__ . '/config.php';
$lokal = __DIR__ . '/config.local.php'; // serverspezifisch, nicht im Git (wird von deploy/mail-setup.sh angelegt)
if (is_file($lokal)) {
    $config = array_merge($config, require $lokal);
}
date_default_timezone_set('Europe/Zurich');
if (empty($config['empfaenger'])) {
    antwort(503, ['ok' => false, 'error' => 'Empfängeradresse ist noch nicht eingerichtet.']);
}

// Bots: Honeypot und zu schnelles Absenden
if (!empty($_POST['website'])) {
    antwort(200, ['ok' => true]);
}
$ts = isset($_POST['ts']) ? (float) $_POST['ts'] : 0;
$diff = microtime(true) * 1000 - $ts;
if ($ts > 0 && $diff > -300000 && $diff < 2500) {
    antwort(400, ['ok' => false, 'error' => 'Bitte das Formular nochmals senden.']);
}

// Begrenzung: höchstens 6 Sendungen pro IP in 10 Minuten
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unbekannt';
$rl = sys_get_temp_dir() . '/hp-formular-' . hash('sha256', $ip);
$hist = is_file($rl) ? array_filter(array_map('intval', explode(',', (string) file_get_contents($rl))), fn($t) => $t > time() - 600) : [];
if (count($hist) >= 6) {
    antwort(429, ['ok' => false, 'error' => 'Zu viele Anfragen. Bitte später nochmals versuchen oder anrufen.']);
}
$hist[] = time();
@file_put_contents($rl, implode(',', $hist));

$typ = ($_POST['form_type'] ?? '') === 'anmeldung' ? 'anmeldung' : 'anfrage';
$pflicht = $typ === 'anmeldung'
    ? ['nachname', 'vorname', 'strasse', 'plz_ort', 'telefon', 'email', 'notfall_name', 'notfall_telefon', 'hund_name', 'hund_rasse', 'hund_gewicht', 'hund_geschlecht', 'agb', 'datenschutz']
    : ['name', 'email', 'nachricht', 'datenschutz'];
foreach ($pflicht as $f) {
    $v = $_POST[$f] ?? '';
    if (is_array($v) ? count($v) === 0 : trim((string) $v) === '') {
        antwort(422, ['ok' => false, 'error' => 'Bitte alle Pflichtfelder ausfüllen.', 'feld' => $f]);
    }
}
$email = trim((string) ($_POST['email'] ?? ''));
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    antwort(422, ['ok' => false, 'error' => 'Bitte eine gültige E-Mail-Adresse angeben.', 'feld' => 'email']);
}

// Nachricht zusammenstellen
$technisch = ['form_type', 'ts', 'website'];
$zeilen = [];
foreach ($_POST as $k => $v) {
    if (in_array($k, $technisch, true)) continue;
    $wert = is_array($v) ? implode(', ', array_map('strval', $v)) : trim((string) $v);
    if ($wert === '') continue;
    $label = ucfirst(str_replace('_', ' ', (string) $k));
    $wert = mb_substr($wert, 0, 5000);
    $zeilen[] = str_contains($wert, "\n") ? "$label:\n$wert\n" : "$label: $wert";
}
$name = $typ === 'anmeldung'
    ? trim(($_POST['vorname'] ?? '') . ' ' . ($_POST['nachname'] ?? ''))
    : trim((string) ($_POST['name'] ?? ''));
$name = preg_replace('/[\r\n]+/', ' ', $name);
$betreff = sprintf('%s: %s von %s', $config['betreff_prefix'] ?? 'Website', $typ === 'anmeldung' ? 'Anmeldung' : 'Anfrage', $name ?: $email);
$text = ($typ === 'anmeldung' ? "Neue Online-Anmeldung" : "Neue Anfrage") . " über hundepension-im-park.ch\n"
      . date('d.m.Y H:i') . "\n\n" . implode("\n", $zeilen) . "\n";

$header = [
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'From: ' . ($config['absender_name'] ?? 'Website Hundepension im Park') . ' <' . $config['absender'] . '>',
    'Reply-To: ' . $email,
];
$ok = mail($config['empfaenger'], '=?UTF-8?B?' . base64_encode($betreff) . '?=', $text, implode("\r\n", $header));
if (!$ok) {
    antwort(500, ['ok' => false, 'error' => 'Der Versand ist fehlgeschlagen.']);
}
antwort(200, ['ok' => true]);
