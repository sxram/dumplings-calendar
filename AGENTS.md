# Giggle-Dumplings-Kalender 2027 — Etsy/Gelato

Aktuelle Nutzervorgabe: Originalseiten in `back-images-with-puzzles-v1/` als Grundlage ERHALTEN, einschließlich Schrift und gesamter Gestaltung. Keine weiteren Gesamtneugenerierungen oder Variantenserien. Bisherige Januar-Neugestaltungen sind verworfen. Nur belegte Text-/Kalender-/Rätselfehler gezielt korrigieren. V19 stellt die Januar-Originalseite pixelidentisch wieder her; Lösbarkeit des Originalrätsels noch offen, siehe `production/JANUARY-ORIGINAL-REVIEW.md`. Das ist keine Druckfreigabe und keine Freigabe der anderen Monatsentwürfe.

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

Fortschreibung 03.10.2026: Aktueller Arbeitsmaster v08. Nur Front- und Rückseite gegenüber v07 geändert; beide visuell geprüft. Englisches Halloween-Impressum ohne Gelato-Angaben nach Nutzervorgabe eingebaut. Nutzerreview und Druckprüfung offen.

Fortschreibung 04.10.2026: Arbeitsmaster v09 ersetzt ausschließlich Januar-Rätselseite; Komponente `production/puzzles/january-v09/`, übrige elf Rätsel aus v07. Der reine untere Master v07 enthält die alte Januarversion und bildet v09 daher nicht vollständig ab.

Fortschreibung 04.10.2026: Arbeitsmaster v10 enthält zusätzlich neue Mai-Komponente `production/puzzles/may-v10/`; übrige zehn Rätsel aus v07. Finale Mai-Seite visuell geprüft.

Fortschreibung 04.10.2026: Aktueller Master v13 mit erster illustrierter Januar-Rückseite als Muster. Ein Built-in-Imagegen-Aufruf für dekorative Vorlage, native Texte/Kalender/Rätsel darüber; Dateien und Prompt unter `production/month-backs/january-v01/`. Nutzerreview der Musterseite vor weiteren Monatsgenerierungen; Einzelansicht `output/pdf/giggle-dumplings-january-back-MUSTER-v03.pdf`. Rasterdekor ca. 127 ppi bei A4, keine Druckfreigabe.

Fortschreibung 04.10.2026: Aktueller Master v15; Februar-Monatsrückseite zusätzlich erstellt. Komponenten `production/month-backs/february-v01/`, ein Bildgenerierungsaufruf; finale Musterseite v02 geprüft. Januar bleibt unverändert aus v13.

Fortschreibung 04.10.2026: Arbeitsmaster v18 mit neu illustrierter Januar-Musterseite `output/pdf/giggle-dumplings-january-back-ILLUSTRIERT-v03.pdf`; reiches Wintermotiv und illustrierte Ziele, native gekrümmte Spuren. Zwei Built-in-Bildaufrufe und lokale Satzkorrekturen; Quellen/Prompts in `production/month-backs/january-rich-v01/`. Nutzerreview offen. Februar ist noch vereinfachter v15-Stand.

Aktuell v20: nur Mochis zwei Puschel hinter der Schleife im oberen Februarbild lokal entfernt. Clip-Overlay-Spezifikation unter `production/month-images/drafts/february-v02/local-patch-manifest.json`; komplette generierte PNG nicht pauschal als neue Februarquelle einsetzen.
