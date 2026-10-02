# Giggle-Dumplings-Kalender 2027 — Etsy/Gelato

- Usage sparsam einsetzen. Vorhandene Quellen und Werkzeuge zuerst prüfen. Keine routinemäßige Bildgenerierung, Vollbildkorrektur, wiederholte Exporte oder umfangreichen Bildanalysen.
- Vor Produktionsänderungen `month-puzzles.md`, `production/assets.json`, `production/STATUS.md` und `production/LESSONS-LEARNED.md` lesen.
- Quellen und Originale erhalten. Neue Ausgaben versionieren; keine stillen Überschreibungen. Alle Ergebnisse lokal speichern.
- `production/assets.json` führt Herkunft, SHA-256, Verwendung, Gestaltungsstatus, Druckstatus und offene Punkte getrennt. Neue Quellen oder Ausgaben explizit registrieren; Änderungen nie automatisch durch neue Prüfsummen akzeptieren.
- `tools/check-production-assets.py --write-overview` vor Übergaben ausführen. Prüfsummen und Strukturtests ersetzen keine Sichtprüfung.
- Englische Rätseltitel und Aufgaben aus `month-puzzles.md` sind festgelegt. Rätsel deterministisch als editierbare Vektoren bauen; Paare duplizieren, Lösungen aus derselben Geometrie ableiten.
- Storytexte, Bao-Jobs, Challenges, echte Kalenderdaten 2027 und Sterntracker erhalten. Kalenderdaten rechnerisch prüfen.
- Nachgereichter Quellenstand: `production/RECOVERED-UPDATE-2026-10-02.md` und `update_26-10-02/todos-corrections.md` berücksichtigen. Unser Arbeitsmaster v04 basiert auf älteren Texten/Bildern und ist noch mit diesem Stand abzugleichen.
- Keine neuen Monatsillustrationen. Februar: eingebettete Quelle im nachgereichten Master mit freigegebenem Kranz erhalten; Winterkleidung und Uhr 20:51 offen. April: Sunnys falschen Pompon-Schwanz entfernen. Juni: Mochis falschen Pompon-Schwanz entfernen. Dezember: `update_26-10-02/calender-image-12.png` ist der zugeordnete, laut Chatnotiz freigegebene Stand; unverändert erhalten.
- Saisonale Farben beibehalten, auch in den Rätselbereichen. Sterntracker explizit von Januar 1/12 bis Dezember 12/12 prüfen. Storytexte und konkrete Bao-Aufgaben aus dem nachgereichten Stand übernehmen, nicht den älteren wiederholten Platzhaltertext.
- Für den beauftragten Arbeitsmaster alle zwölf geänderten unteren Monatsseiten einmal gezielt visuell prüfen. Unveränderte Inhalte nicht routinemäßig erneut rendern. Nutzerfreigabe separat offen halten.
- Arbeitsmaster ausdrücklich als Arbeitsmaster kennzeichnen. Impressum, konkrete Gelato-Produktvorlage, Sicherheitsbereiche, Beschnitt, Bindung und abschließende Druckprüfung sind offen.
- Dies ist kein KDP-Projekt. Keine KDP-Maße, Barcodefelder, Buchseitenparität, Paperback-Umschlagberechnung oder Schwarzweiß-Konvertierung übernehmen. Aktuelle Gelato/Etsy-Vorgaben erst beim betreffenden Veröffentlichungsschritt anhand offizieller Quellen prüfen.
- `tools/reference-halloween/` ist ein historischer Referenzbestand, kein direkt ausführbarer Kalenderworkflow. Feste Pfade, Inhalte, Maße und Seitenauswahl vor einer Portierung prüfen. Das Quellprojekt nicht verändern.

Aktuelle Fortschreibung: Arbeitsmaster v07 verwendet den nachgereichten Master, konkrete Bao-Aufgaben, Saisonfarben und geprüfte Sterntracker. Februar/April/Juni haben Korrekturentwürfe unter `production/month-images/drafts/`; die oben genannten Bildarbeiten sind umgesetzt, ihre Nutzerfreigabe bleibt offen. Aktuelle Auswahl ausschließlich aus `production/assets.json` verwenden.
