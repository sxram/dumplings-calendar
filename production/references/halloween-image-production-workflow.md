# Modularer Bildproduktions-Workflow

## Verbindliches Ziel: Usage sparsam einsetzen

Nutzerentscheidung vom 16.09.2026: Bildgenerierung nur für tatsächlich fehlende
Bildinhalte einsetzen. **Kleine wiederverwendbare Teile statt kompletter Bilder**
erzeugen und als separate Ebenen mit einer erhaltenen Grundszene zusammensetzen.
Beispiele: Aufkleber, Publisher Mark, einzelnes Accessoire, Figur, Requisite oder
Untertitelbanner. Ein freigegebenes Teil anschließend über alle passenden Seiten
und DE/EN/ES-Ausgaben wiederverwenden, statt es für jede Ausgabe neu zu erzeugen.

Vor jeder Bildaktion im Arbeitsplan festhalten:

1. Welche vorhandene registrierte Grundszene und welche Komponenten bleiben erhalten?
2. Reicht **Wiederverwenden + Layout/Text** ohne Bildgenerierung?
3. Falls nicht: welches kleinste sinnvolle **Teilbild/Edit + Compositing** fehlt?
4. Nur wenn das nicht ausreicht: **Neu generieren**, mit konkreter Begründung
   (z. B. grundsätzlich andere Szene oder nicht reparierbare Komposition).

Text, Übersetzungen, Umfangszahlen, Sprechblasen, Rahmen sowie Schnitt-/Faltlinien
als kontrollierte Satz-/Vektorebenen halten. Für solche Änderungen keine komplette
Cover-, Comic- oder Innenseitenillustration neu erzeugen. Geltende Werkzeugregeln
für Rasterbearbeitung bleiben verbindlich; diese Regel umgeht sie nicht.

Neue Teilbilder mit geeignetem Hintergrund beziehungsweise echter Transparenz
anlegen; eingebrannte Schachbrettmuster sind keine Transparenz. Vor dem Einsetzen
Umriss, Auflösung, Strichstärke und Perspektive prüfen. Ebenenfolge, Position,
Maßstab, Quellen-IDs und Prüfsummen im jeweiligen Layoutmanifest dokumentieren.
Nicht über bestehende Texte legen; außerhalb beabsichtigter Überdeckungen die
Grundszene erhalten. Erst ein Muster prüfen, dann die Komponente wiederverwenden.

Bei fehlendem Bildkontingent nicht wiederholt erfolglos generieren: innerhalb des
aktiven Auftrags mit Texten, Asset-Pflege, Layoutplanung oder Prüfungen fortfahren.
Das erlaubt keine Wiederaufnahme einer vom Nutzer pausierten Produktion oder
Automation. Seit 18.09.2026 ist lokale Weiterarbeit ausdrücklich beauftragt;
Automationen bleiben aus.

## Ergänzung aus dem Vorgänger vom 16.09.2026

Zuerst `production/assets.json` nach wiederverwendbaren Komponenten durchsuchen.
Herkunft, Prüfsumme und tatsächliche Freigabe prüfen; bestehende Quellen bevorzugen.
Vorhandene Logos, Aufkleber und Titelkomponenten nicht unnötig neu generieren.
Kopierte Vorlagen sind nicht automatisch für Halloween inhaltlich passend.

Logos, Sticker und andere Grafiken niemals über Text platzieren. Getrennte freie
Layoutbereiche vorsehen, vollständige sichtbare Umrisse berücksichtigen und
Überschneidungen im Render prüfen. Freigegebene Hintergrunddekoration nicht für
ein Publisher Mark entfernen. Vor Serienbearbeitung eine Komponente prüfen.

Für Innentitel und Impressum gilt `production/workflows/frontmatter.md`:
vollständige neue Seiten aus getrennten Komponenten, keine Alttext-Überlagerung.
Gestaltungsfreigabe und technische Druckprüfung getrennt im Register halten.

Übernommen und angepasst am 10.09.2026 aus
`/Users/stefan/Documents/dumplings/IMAGE-PRODUCTION-WORKFLOW.md`.
Gilt für 30 Ausmalmotive, Comics, Bilderwitze, Bastelvorlagen und Cover.

## Vor jeder Bildaktion

Im Arbeitsplan festhalten: `Neu generieren`, `Teilbild/Edit` oder `Layout/Text`.
Prüfen, ob neue visuelle Inhalte nötig sind oder vorhandene Quellen genügen.
Für eine Übersetzung keine ganze Szene neu generieren. Text, Rahmen, Sprechblasen,
Schnittlinien und Aufkleber separat gestalten und im Layout zusammensetzen.
Für Änderungen an bestehenden Rasterbildern das verfügbare Bildbearbeitungswerkzeug
und dessen geltende Anweisungen verwenden. Die modulare Planung ist keine Erlaubnis,
Werkzeugvorgaben zu umgehen. Reine Satz- und Vektorebenen können lokal gebaut werden.

## Ablage pro Motiv oder Komponente

- `base.png`: erhaltene Ausgangsszene.
- `layers/characters/`, `layers/objects/`: wiederverwendbare Figuren und Requisiten.
- `layers/text/`: sprachabhängige Texte und Sprechblasen.
- `layers/badges/`, `layers/frame/`: Coverhinweise und technisch gesetzte Rahmen.
- `masks/`: dokumentierte Bearbeitungsbereiche, sofern verwendet.
- `composites/`: versionierte Zusammensetzungen.
- `manifest.json`: Quellen, Prüfsummen, Versionen, Ebenenfolge, Koordinaten und Status.

Diese Unterstruktur bei Bedarf im jeweiligen Produktionsordner anlegen. Originale
und freigegebene Varianten erhalten; keine abweichende Datei still überschreiben.
Prompts, Ergebnisse und Prüfnotizen immer lokal speichern.

## Ablauf

1. Konzept, Stil, Motivplan und vorhandene Versionen lesen.
2. Szene oder Panel mit Figuren, Handlung, Text und Ebenen beschreiben.
3. Zunächst ein repräsentatives Muster erarbeiten und prüfen; eine bereits beauftragte
   Serie innerhalb des vereinbarten Stils weiterführen. Inhaltliche Fragen bündeln.
4. Neue Bilder als Entwurf speichern. Keine Storyboard-Miniaturen als fertige
   Druckquellen behandeln; einzelne Druckmotive ausreichend groß erstellen.
5. Gesamtansicht, Detailansichten und tatsächliche Druckgröße prüfen.
6. Geprüfte Komponenten mit separat gesetzten Sprach- und Layoutebenen kombinieren.
7. Manifest und Produktionsstatus aktualisieren. Inhaltsfreigabe und technische
   Druckprüfung getrennt dokumentieren.

## Prüfungen für Bilder und Comics

- Feste Accessoires und Figurenzuordnung über alle Panels erhalten.
- Hände, Augen, Kopffalten, Mützenkonturen und wichtige Requisiten vergrößert prüfen.
- Keine unbeabsichtigten Konturlücken, abgeschnittenen Figuren oder zusätzlichen Glieder.
- Schwarze Linien auf Weiß, keine grauen Füllungen oder großen schwarzen Malflächen.
- Rahmen erst im Satz setzen; Position am Bildbereich messen und im Render prüfen.
- Comic-Leserichtung, Sprechblasen-Zuordnung, Requisiten und Anschluss zwischen Panels prüfen.
- Eine Pointe muss aus der Bildhandlung verständlich werden; letzte Panels nicht mit Text überfüllen.
- Quellauflösung und effektive Auflösung am Druckmaß dokumentieren. Hochskalieren
  erzeugt keine neuen Details; 300-dpi-Metadaten allein belegen keine Druckqualität.
- Vor Umwandlung RGB prüfen: ungleiche RGB-Kanäle bedeuten Farbpixel. Gleiche Kanäle
  können Grau enthalten. Finale monochrome Bildraster separat auf ausschließlich
  Schwarz und Weiß prüfen; danach Konturen erneut ansehen.
- Bei gezielten Edits Original und Ergebnis vergleichen; außerhalb des geplanten
  Bereichs nach Möglichkeit Pixelvergleich ergänzen. Keine automatische Konturerkennung
  als Ersatz für Sichtprüfung ausgeben.

## Bastelvorlagen

Schnitt-, Falt- und Klebelinien als kontrollierte Layoutelemente setzen. Vor finaler
Illustration den Mechanismus als Papiermodell testen. Originalgröße, Maskenpassform,
Aufstellerstand und Laschenfunktion prüfen und als tatsächlich getestet oder offen
dokumentieren. Rückseiten der Ausschneideblätter frei halten; Abstand zur Bindung
berücksichtigen. Bastelflächen erhalten keinen störenden Ausmalrahmen.

## Vollständige Neugenerierung

Sinnvoll bei einer neuen Szene oder wenn Perspektive, Komposition oder vorhandene
Quellqualität eine brauchbare Weiterbearbeitung verhindern. Bei Übersetzungen,
Seitenzahlen und Coverhinweisen vorhandene Bildbasis weiterverwenden.
