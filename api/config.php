<?php
// Einstellungen für den Formularversand (api/anfrage.php).
// WICHTIG: Vor dem Livegang die Empfängeradresse eintragen. Solange sie leer ist, bietet die Website
// beim Absenden automatisch SMS, Kopieren und Anrufen als Ausweichweg an.
return [
    'empfaenger'     => '',                                   // z. B. 'info@hundepension-im-park.ch'
    'absender'       => 'website@hundepension-im-park.ch',    // Adresse auf der eigenen Domain (SPF/DKIM)
    'absender_name'  => 'Website Hundepension im Park',
    'betreff_prefix' => 'Website',
];
