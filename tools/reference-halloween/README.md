# Wiederverwendbare Projektwerkzeuge

`etsy/add_printable_covers.py` ergänzt v01 verlustfrei um optionale Coverseiten
als neue v02-Pakete (67/23 Seiten). Prüft registrierte Quellen und unveränderte
Inhaltsseiten; vorhandene v02 wird nicht überschrieben.

Etsy-Halloween: `etsy/build_halloween.py` erstellt die beiden konfigurierten
englischen Produkte (66/22 Seiten, A4/US Letter, Listing-SVGs/JPEGs und Texte)
aus registrierter EN-Quelle. `etsy/validate_halloween.py` prüft die fertigen Dateien
ohne Neubau. Details und Auftragsabgrenzung: `etsy/README.md`.

`import-user-puzzles-svg.py` bereitet die registrierten Nutzer-Rätsel und Lösungen
als deutsche SVG-Seiten auf. `--output` muss ein neuer Ordner sein. Keine PDFs,
Rasteränderungen oder Renderings; erzeugt auch einen zukünftigen Seitenplan.

Nach Bereinigung vom 29.09.2026 sind veraltete Ausgabe-PDFs und Rätselentwürfe
teilweise nur noch in Git vorhanden. Historische Builder nicht blind starten:
benötigte Eingaben zuerst prüfen. Löschliste und Wiederherstellungs-Commit stehen
in `production/cleanup-20260929.json`. Aktuelle Buchbasis ist v08; deutsche v05/v06
bleiben als Quellen für vorhandene Komponenten-Builder erhalten.

Vor neuer Skripterstellung diesen Bestand prüfen. Vorhandene Werkzeuge verwenden
oder gezielt erweitern. Keine neue Skriptkopie allein für andere Seitenzahlen,
Sprachen oder Ausgabeordner anlegen; bei wiederkehrendem Bedarf Parameter ergänzen.
Versionsgebundene Builder dokumentieren historische Produktionsschritte und dürfen
nicht ungeprüft für neue Buchfassungen ausgeführt werden.

## Bestand

| Aufgabe | Werkzeug | Einsatzhinweis |
|---|---|---|
| Asset-Register und Prüfsummen prüfen | `check-production-assets.py` | `--write-overview` aktualisiert `production/STATUS.md` |
| Anfangsseiten einbauen | `assemble-review-v02.py` | Registergestützt; neuer Ausgabeordner erforderlich |
| Innentitel und Pips setzen | `build-frontmatter-review-v01.py` | Versionsgebundener Layout-Builder |
| Impressum setzen | `build-imprint-review-v02.py` | Versionsgebundener Layout-Builder |
| Anatomiekorrekturen einbauen | `replace-anatomy-v03.py`, `replace-anatomy-v04.py` | Bestehende Korrekturquellen und jeweilige Basis erforderlich |
| Kleine Figurenkorrekturen einsetzen | `replace-figures-v05.py` | Begrenzte PDF-Korrekturebenen |
| Korrekturbereiche vergleichen | `check-figures-v05.py` | Vergleich gegen v04 |
| Aufsteller zentrieren | `align-standees-v06.py` | Einzelne Figuren aus vorhandenen Quellen platzieren |
| Girlandenmuster bauen | `build-garland-v01.py` | Vorhandene Figuren und sprachabhängige Texte |
| Freigegebene Girlande einbauen | `integrate-garland-v07.py` | B08 aus geprüftem Muster übernehmen |
| Maskenmuster setzen | `build-mask-sample-v01.py` | Versioniertes Einzelmuster |
| Betroffene Seiten rendern | `render-anatomy-v03.py`, `render-anatomy-v04.py`, `render-figures-v05.py`, `render-standees-v06.py` | Seiten und Versionen derzeit fest eingetragen; vor Wiederverwendung prüfen |
| Umfangreiche historische Prüfung | `render-review-v02.py`, `review-book-v01.py`, `check-review-v01.py` | Nur bei konkretem Anlass, nicht bei jeder Änderung |

## Unfertige Werkzeuge

- `reorder-stories-v08.py`: am 24.09.2026 korrigiert und erfolgreich ausgeführt.
  Verschiebt Inhalts-/Rückseitenpaare und prüft Recto-Parität, Leerseiten sowie
  übernommene Seitenoperatoren. Benötigt einen leeren Ausgabeordner.
- `build-pumpkin-card-v01.py`: experimentelles Muster, keine freigegebene Vorlage.
  Vor erneutem Einsatz Gestaltung, Faltmechanik, Sprachtexte und Schutz vor
  Überschreiben prüfen.
- `build-book-v01.py`: historischer Vollsatz-Builder bleibt gesperrt; siehe
  `production/README.md`.

## Sparsamer Ablauf

1. Passendes Werkzeug und benötigte Eingaben auswählen.
2. Nur notwendige Parameter bzw. betroffene Logik ändern.
3. Lokal ausführen; kurze Status- und Fehlermeldungen zurückgeben.
4. Nur tatsächlich betroffene Seiten rendern und ansehen. Unveränderte, bereits
   geprüfte Inhalte anhand ihrer Quellen und bisherigen Prüfprotokolle übernehmen.
5. Neue Produktionsquellen registrieren und Status dokumentieren.

Vorhandene Ausgaben niemals zur Vorbereitung pauschal löschen oder überschreiben.
Neue Entwürfe erhalten einen neuen Ausgabeordner bzw. eine neue Versionsnummer.

## Coverbanner

`build-front-reference-svg.py`: neue Nutzer-Vorderseite v07 mit editierbarem
gebogenem Untertitel und Siegel-/Inhaltstexten. Bewahrt Quellseitenverhältnis;
Druckformat-Anpassung separat. Keine PDF-Ausgabe.

`build-backcover-reference-svg.py`: Nutzer-Rückseitenentwurf v02 mit bereinigtem
Hintergrund, editierbaren Texten und drei bestehenden Buchillustrationen als
Vorschauen. SVG und Quellenmanifest; keine PDF-Ausgabe.

`build-backcover-svg.py`: deutsche Rückseite mit fünf Charaktervorstellungen,
SVG-Porträtausschnitten aus registrierter Coverquelle und Publisher-Zeichen.
Barcodefläche nur Platzhalter. Versionierte SVG-Ausgabe ohne PDF.

`build-cover-front-svg.py`: deutsche Vorderseite mit registrierten Bildquellen,
Banner und separater Inhaltsaufkleber-Ebene. Versionierter SVG-Entwurf ohne PDF;
vor Wiederholung neue Ausgabeversion setzen. Nutzer übernimmt Sichtprüfung.

`build-cover-banner-svg.py`: deutsche Banner-Komponente mit Geometrie des
bestätigten Innentitels. Prüft registrierte Quelle und Textbreite; erzeugt SVG
und Manifest ohne Rasterbilder/PDFs. Vor neuer Variante Ausgabeversion im Skript
anpassen; vorhandene Ausgabe wird nicht überschrieben. Sichtprüfung übernimmt
der Nutzer.

## Historischer Rätsel-Builder

`build-puzzles-svg.py --output <neuer-Ordner>`: acht SVG-Aufgaben, acht Lösungen, HTML-Übersicht und Manifest. Prüft registrierte Figurenquelle, Labyrinth-Baumstruktur und eindeutiges Sudoku. Aktueller Entwurfsstand v04. Keine PDFs. Neue Dateien anschließend registrieren und Sichtprüfung dokumentieren.
