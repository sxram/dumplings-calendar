# Giggle-Dumplings-Kalender 2027 — Etsy/Gelato

- Usage sparsam einsetzen. Vorhandene Quellen und Werkzeuge zuerst prüfen. Keine routinemäßige Bildgenerierung, Vollbildkorrektur, wiederholte Exporte oder umfangreichen Bildanalysen.
- Vor Produktionsänderungen `month-puzzles.md`, `production/assets.json`, `production/STATUS.md` und `production/LESSONS-LEARNED.md` lesen.
- Quellen und Originale erhalten. Neue Ausgaben versionieren; keine stillen Überschreibungen. Alle Ergebnisse lokal speichern.
- `production/assets.json` führt Herkunft, SHA-256, Verwendung, Gestaltungsstatus, Druckstatus und offene Punkte getrennt. Neue Quellen oder Ausgaben explizit registrieren; Änderungen nie automatisch durch neue Prüfsummen akzeptieren.
- `tools/check-production-assets.py --write-overview` vor Übergaben ausführen. Prüfsummen und Strukturtests ersetzen keine Sichtprüfung.
- Englische Rätseltitel und Aufgaben aus `month-puzzles.md` sind festgelegt. Rätsel deterministisch als editierbare Vektoren bauen; Paare duplizieren, Lösungen aus derselben Geometrie ableiten.
- Storytexte, Bao-Jobs, Challenges, echte Kalenderdaten 2027 und Sterntracker erhalten. Kalenderdaten rechnerisch prüfen.
- Keine neuen Monatsillustrationen. Februar: `02_corrected.png` als vereinbarte Basis; Winterkleidung und Uhr 20:51 offen. April: nur Sunnys Puschelschwanz offen. Juni: nur Mochis Puschelschwanz offen. Dezember: zuletzt freigegebene Version, lokale Zuordnung noch belegen.
- Für den beauftragten Arbeitsmaster alle zwölf geänderten unteren Monatsseiten einmal gezielt visuell prüfen. Unveränderte Inhalte nicht routinemäßig erneut rendern. Nutzerfreigabe separat offen halten.
- Arbeitsmaster ausdrücklich als Arbeitsmaster kennzeichnen. Impressum, konkrete Gelato-Produktvorlage, Sicherheitsbereiche, Beschnitt, Bindung und abschließende Druckprüfung sind offen.
- Dies ist kein KDP-Projekt. Keine KDP-Maße, Barcodefelder, Buchseitenparität, Paperback-Umschlagberechnung oder Schwarzweiß-Konvertierung übernehmen. Aktuelle Gelato/Etsy-Vorgaben erst beim betreffenden Veröffentlichungsschritt anhand offizieller Quellen prüfen.
- `tools/reference-halloween/` ist ein historischer Referenzbestand, kein direkt ausführbarer Kalenderworkflow. Feste Pfade, Inhalte, Maße und Seitenauswahl vor einer Portierung prüfen. Das Quellprojekt nicht verändern.
