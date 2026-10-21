<?php
// Einstellungen für den Formularversand (api/anfrage.php).
// Auf dem Server am einfachsten mit «sudo bash deploy/mail-setup.sh» einrichten: Das Skript legt
// api/config.local.php an (nicht im Git) und überschreibt damit die Werte unten.
// Solange keine Empfängeradresse gesetzt ist, bietet die Website beim Absenden automatisch SMS,
// Kopieren und Anrufen als Ausweichweg an.
return [
    'empfaenger'     => '',                                   // z. B. 'info@hundepension-im-park.ch'
    'absender'       => 'website@hundepension-im-park.ch',    // Adresse auf der eigenen Domain (SPF/DKIM)
    'absender_name'  => 'Website Hundepension im Park',
    'betreff_prefix' => 'Website',
];
