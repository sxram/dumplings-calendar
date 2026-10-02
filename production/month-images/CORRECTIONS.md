# Bildkorrekturen — 02.10.2026

Built-in Imagegen verwendet; kein CLI-/API-Fallback. Die Ausgangsbilder wurden verlustfrei aus dem nachgereichten Master extrahiert. Dezember blieb unverändert.

| Monat | Gespeicherter Korrekturentwurf | Änderung | Prompt |
|---|---|---|---|
| Februar | [02-winter-clock-v03.png](drafts/february-v01/02-winter-clock-v03.png) | Mochi mit rosa Wintermantel und Schal; Uhr visuell auf 20:51 korrigiert | [Erster Edit](drafts/february-v01/prompt.txt), [Minutenzeiger](drafts/february-v01/clock-followup-prompt.txt), [Stundenzeiger](drafts/february-v01/hour-followup-prompt.txt) |
| April | [04-no-pompon-tail-v01.png](drafts/april-v01/04-no-pompon-tail-v01.png) | Sunny: falscher Pompon-Schwanz links am Rücken entfernt | [Prompt](drafts/april-v01/prompt.txt) |
| Juni | [06-no-pompon-tail-v01.png](drafts/june-v01/06-no-pompon-tail-v01.png) | Mochi: falscher Pompon-Schwanz neben der unteren linken Körperkontur entfernt, Decke rekonstruiert | [Prompt](drafts/june-v01/prompt.txt) |

Fünf gezielte Bildedit-Aufrufe insgesamt: Februar erforderte nach der Kleidung zwei eng begrenzte Zeigerkorrekturen. April und Juni jeweils ein Aufruf. Alle Ergebnisse lokal gespeichert; frühere Februarvarianten erhalten, aber nicht ausgewählt.

## Prüfstatus

- Neue Bilder: 1492 × 1054 Pixel, RGB. Keine Auflösung durch bloße dpi-Metadaten behauptet.
- Februar: Winterkleidung, Gesicht, Brief und Kranz gezielt visuell geprüft; Uhr vergrößert geprüft, letzte Variante zeigt plausibel 8:51/20:51. Dies ist eine visuelle Prüfung der Rasterzeichnung, kein mathematischer Nachweis exakter Zeigerwinkel.
- April/Juni: Fehlteil entfernt; Körper, Hände und benachbarte Objekte visuell erhalten, Hintergrundrekonstruktion scharf. Keine Pixelidentität außerhalb des Edits behauptet, da das Bildwerkzeug die gesamte Rasterdatei neu ausgibt.
- Im Gesamtmaster v07 sind die Pixel der drei ausgewählten Varianten exakt eingebettet; diese technische Gleichheit wurde automatisiert geprüft.
- Gestaltungsfreigabe durch den Nutzer und produktbezogene Gelato-Druckprüfung weiterhin offen.
