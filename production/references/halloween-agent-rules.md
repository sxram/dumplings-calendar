# KDP-Projekt

## Verbindlicher sparsamer Ablauf – Nutzerentscheidung 24.09.2026

- Sichtprüfungen übernimmt grundsätzlich der Nutzer. Keine routinemäßigen
  Bildanalysen, Kontaktbögen oder Vollbuch-Renderings durch den Agenten.
  Eigene Sichtprüfung nur bei einem konkreten technischen Anlass; Grund benennen.
- PDFs erst am Ende erstellen, zuerst ausschließlich Deutsch. EN/ES-Exporte
  erst in einem später ausdrücklich beauftragten Schritt.
- Bis dahin vorhandene Komponenten und editierbare Quelldateien weiterverwenden;
  keine Zwischen-PDFs zur routinemäßigen Übergabe.
- Notwendige automatisierte Struktur-/Dateiprüfungen knapp ausgeben. Nutzerreview
  als offen dokumentieren; keine Sichtfreigabe ohne tatsächliche Prüfung behaupten.
- Diese Entscheidung ersetzt widersprechende frühere Routine-Render-/Reviewregeln.

Dieses Repository enthält den Produktionsworkflow für ein Amazon-KDP-Buch.
Das Projekt ist primär ein Illustrations- und Publishing-Projekt.

## Vor jeder inhaltlichen Änderung lesen

- `01-concept/concept.md`
- `01-concept/style-guide.md`
- `01-concept/motifs.md`
- `01-concept/back-pages.md`
- `PROGRESS.md`

Je nach Arbeitsschritt zusätzlich lesen:
- `production/README.md`, `production/assets.json` und `production/STATUS.md` für
  vorhandene Assets, Versionen, Herkunft und Prüfstatus; vor Neugenerierung prüfen.
- `production/workflows/frontmatter.md` für Innentitel und Impressum.
- `IMAGE-PRODUCTION-WORKFLOW.md` für Bilder, Comics, Bastelvorlagen und Layout.
- `AUTOMATION.md` für Produktion, Prüfstatus und Git-Sicherung.
- `editions/LOCALIZATION-LESSONS.md` für DE/EN/ES.
- `04-cover/cover-text-guidelines.md` für Cover und Innentitel.
- `01-concept/halloween-specials-v01.md` für die noch nicht freigegebene Special-Auswahl.

## Projektstruktur

```text
01-concept/              Konzept, Stil, Motive und Rückseiten
02-characters/           Figuren und Referenzbilder
03-coloring-pages/       Entwürfe, freigegebene und verworfene Seiten
04-cover/                Coverentwürfe und Produktionsdateien
05-kdp/                  Innen-PDF, Gesamtumschlag und Preflight
06-listing/              Titel, Beschreibung, Keywords und Metadaten
tools/                   Wiederholbare Prüf- und Exportwerkzeuge
editions/                Sprachtexte, Editionszuordnung und Lokalisierungsregeln
```

## Arbeitsregeln

- Usage sparsam einsetzen: zuerst vorhandene Assets wiederverwenden, andernfalls
  kleine austauschbare Bildteile erzeugen und als Ebenen zusammensetzen. Keine
  Vollbild-Neugenerierung für Aufkleber, Text, Übersetzung oder Layout. Vor jeder
  Bildaktion Vorgehen und nötigenfalls Grund einer Vollgenerierung dokumentieren;
  Details in `IMAGE-PRODUCTION-WORKFLOW.md`.

- Alle ausgearbeiteten Konzepte, Texte, Drehbücher, Bilddateien und Exporte immer lokal
  in diesem Projektordner speichern. Ergebnisse nicht ausschließlich im Chat belassen.
- Entwürfe klar als Entwürfe kennzeichnen und in den Produktionsstatus aufnehmen.
- Originale und freigegebene Dateien nie ohne ausdrückliche Anweisung überschreiben.
- Neue Bildvarianten zuerst unter `drafts/` speichern und visuell prüfen.
- Freigegebene Seiten nach `03-coloring-pages/approved/` verschieben oder kopieren.
- Produktionsdateien erhalten Versionsnummern; frühere Fassungen bleiben erhalten.
- Jede neue oder neu ausgewählte Produktionsquelle in `production/assets.json`
  mit Herkunft, Prüfsumme, Verwendung und getrenntem Gestaltungs-/Druckstatus führen.
  `tools/check-production-assets.py --write-overview` vor Übergabe ausführen.
  Bestands-Builder erst nach Registeranbindung wieder für neue Buchfassungen nutzen.
- Vor KDP-Upload Innen-PDF und Cover visuell rendern und Maße, Beschnitt, Seitenzahl,
  Farbmodus und Auflösung prüfen.
- Urheberrechtlich geschützte Figuren, Logos, Marken und Verpackungen vermeiden.

## KDP-Arbeitsannahmen

Format, Seitenzahl, Papierfarbe, Beschnitt und Farbprofil werden im Konzept festgelegt
und vor dem Export dokumentiert. Solange diese Werte offen sind, keine Uploaddatei als
final bezeichnen.

Die 30 Ausmalmotive beim Satz genau einmal aufnehmen. Comics, Bilderwitze und
Bastelvorlagen separat zählen. Physische Seitenzahl aus dem Seitenplan berechnen;
aus dem Vorgänger keine Format-, Seitenzahl- oder Freigabewerte übernehmen.
Aktuelle KDP-Vorgaben vor veröffentlichungsrelevanten Berechnungen anhand offizieller
Quellen prüfen. Wiederholbare Werkzeuge bei Bedarf unter `tools/` erstellen; alte
Builder erst nach Prüfung ihrer fest eingebauten Maße, Pfade und Seitenlisten portieren.
