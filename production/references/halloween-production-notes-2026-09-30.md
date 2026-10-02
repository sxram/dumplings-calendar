# Produktionsnotiz: Korrekturen am 29.–30.09.2026

## Nachkorrektur: falsche Entwurfsmasken und Sprechblasen

Die angehobene Fußlinie berührte die vier unteren Witz-Sprechblasen. Diese wurden
in Innenbuch v10 um 26,5 pt von unten verkürzt. Bei Satzänderungen den angrenzenden
Inhalt prüfen, nicht allein das verschobene Element.

Die vorherige Entwurfskorrektur hatte einen einheitlichen weißen Bereich auf alle
Rätsel angewendet. Die Rastertexte liegen jedoch auf jeder Vorlage an anderer
Stelle; einige wurden verfehlt und Bildränder überdeckt. Textsuche allein kann
eingebrannte Rastertexte nicht nachweisen. V10 entfernt zuerst die falschen
Flächen und verwendet pro Seite anhand gezielter Detailrender ermittelte Bereiche.
Auch die Lösungen erhalten die passend umgerechneten Korrekturen. Vor Freigabe
jeden geänderten Ausschnitt auf Schriftreste und unversehrte Bildränder prüfen.

## KDP-Rückmeldung: Fußzeile zu niedrig

Die PDF-Fußzeile hatte eine Grundlinie von 16,5 pt (5,82 mm); Unterlängen
lagen noch tiefer. KDP verlangt ohne Beschnitt mindestens 18 pt (6,35 mm)
unten: https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6 .
Die vorherige technische Prüfung der Seitengröße reichte daher nicht aus.
Neue Grundlinie 36 pt, Trennlinie 49,2 pt; alte Text-/Linienobjekte tatsächlich
entfernt. Neue Ausgabe innen v09, 128 Seiten. Erneute KDP-Prüfung ausstehend.
Vermeidung: sichtbare Glyphengrenzen einschließlich Unterlängen gegen den
Sicherheitsbereich prüfen; nicht nur Grundlinien oder Papiermaße. Überdeckte
Altobjekte können von Prüfwerkzeugen weiterhin erkannt werden und müssen aus
Produktions-PDFs entfernt werden. Alte Vollbuch-Builder nicht ungeprüft erneut
verwenden; vorhandene Quellfußzeilen benötigen ebenfalls diese Bereinigung.

## Nachtrag: Umschlag v09

Nutzer meldet senkrechte Schnitte, fehlenden unteren Schriftzug, Barcode und
verschobene Vorschauen im Umschlag v08. Register und Export verwenden die
ausgewählte Rückseite v05; nicht den vollständigen Rohentwurf. Ein maskierter
Ausschnitt des ursprünglichen Entwurfs liefert nur den unteren Schriftzug.
Im Poppler-Prüfrender von v08 ist die Gestaltung einschließlich Schriftzug
sichtbar; die gemeldeten Schnitte sind dort nicht reproduzierbar. Eine
abweichende Darstellung der PDF-Masken ist daher eine mögliche, nicht bewiesene
Ursache. Eine zusätzliche weiße Barcodefläche wurde im Export tatsächlich
eingefügt, obwohl die entsprechende Ebene der SVG-Vorlage ausgeblendet war.

Korrektur v09: ausgewählte Vorder-/Rückseiten vor der PDF-Montage vollständig
rendern, sodass Masken und verschachtelte Ausschnitte keine getrennten
PDF-Ebenen mehr sind. Kein Beispielbarcode und keine zusätzliche weiße Fläche.
Bei KDP kann der automatisch gesetzte Barcode weiterhin erscheinen; dessen
Platzierung muss in der KDP-Vorschau geprüft werden. Dunkelviolette Seitenflächen
bleiben zur proportionalen Anpassung erhalten. 300-dpi-Rendering erhöht nicht
die native Auflösung der Hintergrundquellen. Nutzerfreigabe bleibt offen.

Vermeidung: die konkrete Exportdatei prüfen, nicht nur die SVG-Vorlage; versteckte
Prüfebenen nicht durch den Export wieder hinzufügen. Gemeldete Darstellungsfehler
als Befund dokumentieren und eine vermutete Ursache nicht als bewiesen ausgeben.

## Beobachtete Fehler

- Die ersten Bastelseiten hatten eine falsche bzw. uneinheitliche Größe und waren dadurch nicht zuverlässig auf 8,5 × 11 Zoll vorbereitet.
- Die Bastelseiten verwendeten zunächst Arial, während der übrige Satz die Giggle-Dumplings-Schriftwirkung mit Chalkboard für Überschriften nutzt.
- Bei den Bastelseiten fehlten die einheitliche untere Trennlinie und die tatsächliche Buchseitenzahl.
- Kontrollstrecken und Entwurfskennzeichnungen waren in Bastelvorlagen teilweise noch sichtbar.
- Die Rätselseiten und Lösungsseiten enthielten zusätzlich kleine Aufgaben-/Lösungskennzeichnungen im unteren Bereich sowie bei einer Seite noch „Entwurf“.
- Das Kürbis-Klappmaul war als Mechanik und Skizze nicht verständlich genug und wurde deshalb aus der Buchauswahl entfernt.
- Die zunächst erstellte Umschlagmontage benötigte eine technische Korrektur wegen der sehr großen eingebetteten Rückseiten-SVG; die Verarbeitung wurde auf unbegrenzte SVG-Größe umgestellt.

## Vermeidungsregeln

### Ergänzung englische Ausgabe

- Nicht nur extrahierbare PDF-Texte übersetzen: die Rätsel und Lösungen enthalten
  deutsche Rasterbeschriftungen. Lokale Texterkennung liefert ein Koordinateninventar;
  gezielte Kontrolle ergänzt die automatische Suche nach Sprachresten.
- OCR-Rechtecke können benachbarte Sterne, Schwünge oder Figuren berühren. Für solche
  Stellen engere individuelle Flächen verwenden, statt Titelzeilen pauschal abzudecken.
- Native deutsche Texte strukturell entfernen. In pypdf kann ein vorhandener
  ContentStream als leerer Dictionary-Wert „false“ ergeben; deshalb explizit auf
  `is not None` prüfen. Andernfalls bleibt die alte Sprache unter der neuen stehen.
- Nicht komplette BT/ET-Blöcke zum Entfernen einer Fußzeile verwerfen: solche Blöcke
  können zusätzlich Fließtexte enthalten. Die englische Ausgabe setzt Willkommens-
  und Bastelanleitung vollständig neu; Layout und Textvollständigkeit getrennt prüfen.
- US-English konsequent verwenden (Color, colored pencils, center); alte mehrsprachige
  Vorlagen enthielten teilweise „Colour“. Umfang aus dem aktuellen 128-Seiten-Plan
  ableiten, nicht aus dem Parallelprojekt oder der früheren 110-Seiten-Sichtfassung.

- Vor jedem Satz Format, ViewBox, Seitenmaß und Skalierungsfaktor automatisch gegen 8,5 × 11 Zoll prüfen.
- Schriftfamilien zentral festlegen: Chalkboard/Chalkboard SE für sichtbare Giggle-Dumplings-Überschriften, DejaVu Sans für sachliche Anleitungstexte; keine Arial-Reste in neuen Bastelseiten.
- Fußzeile als Satzebene erst nach dem Skalieren setzen: Trennlinie, Buchname und physische Seitenzahl gehören auf Inhaltsvorderseiten; Leerseiten bleiben leer.
- Vor dem Export jede Aufgaben-/Lösungsquelle auf Entwurfsvermerke, doppelte Seitenlabels und alte Kontrollstrecken prüfen. Labels oben dürfen der Orientierung dienen, untere Produktionsvermerke nicht.
- Bastelmechaniken vor Einbau als Papiermodell prüfen; unverständliche Falt- oder Klebelösungen nicht in den Buchsatz übernehmen.
- Große SVG-Dateien mit unbegrenzter SVG-Verarbeitung konvertieren und anschließend Seitenzahl, Mediengröße, Schrift-Einbettung sowie gezielt die geänderten Seiten prüfen.
- Editierbare Quellen, Registereintrag und erzeugten PDF-Stand immer gemeinsam versionieren; ältere Exportstände nicht überschreiben.
