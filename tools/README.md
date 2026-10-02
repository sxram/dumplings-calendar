# Kalenderwerkzeuge

Übernommen am 02.10.2026 aus `../kdp-dumplings-halloween/tools/`.

Aktiv:
- `check-production-assets.py`: an Kalenderordner und Etsy/Gelato angepasst; prüft SHA-256, Quellen, Auswahl und unregistrierte Dateien. `--write-overview` erzeugt `production/STATUS.md`.
- `ocr-image-text.swift`: unverändert übernommen; lokale macOS-Vision-Texterkennung mit Positionen. Nur bei eingebrannten Beschriftungen und konkretem Bedarf einsetzen; OCR ist keine Sichtfreigabe.
- `register-assets.py --add-new`: ergänzt ausschließlich neue Assets; vorhandene Prüfsummen und Status bleiben unverändert.
- `build-calendar-puzzles.py --output production/puzzles/<neue-Version>`: zwölf deterministische SVG-Rätsel und gemeinsame Zeichnungsdaten; ersetzt die alten Rätselobjekte strukturell im unteren Arbeitsmaster. Keine Bildgenerierung. Quelllayout und registrierte PDF-Prüfsumme müssen passen.
- `check-calendar-master.py production/puzzles/<Version>`: prüft zwölf Monate, echte Wochentage 2027, Seitengrößen, Titel, Aufgaben und unveränderte übrige Texte.
- `assemble-calendar-master.py --lower <registrierte-untere-PDF> --output <neue-PDF>`: ersetzt ausschließlich die zwölf unteren Monatsseiten der registrierten 26-Seiten-Basis. Die übrigen 14 Seiten bleiben erhalten; Quell- und Seitenprüfsummen werden geprüft.

`reference-halloween/` enthält alle Python-/Swift-Skripte und die ursprüngliche Werkzeugübersicht als nachvollziehbare Referenz. Keines dieser historischen Skripte wurde ausgeführt. Insbesondere KDP-Assembler, Cleanup-Skripte, Cover-Exporte und versionsgebundene Reparaturen nicht direkt starten. Der Rätsel-Builder zeigt nutzbare Prinzipien (exakte Duplikate, gemeinsame Lösungsgeometrie, deterministische Konstruktion), enthält aber Halloween-Aufgaben, deutsche Texte und Buchmaße.

`production/tool-import-manifest.json` dokumentiert Originalpfade und Prüfsummen. Wiederkehrende Abläufe parametrisieren; keine neue Skriptkopie allein für einen anderen Ausgabeordner. Bestandsdateien nie zur Vorbereitung löschen.
