# Deployment des ADMBw QEA Editors (SharePoint / Bw-Netz)

Zwei Dateien stehen zur Verfügung (identischer Inhalt, bis auf den Kopf):

* `ADMBw_QEA_Editor.html` — reine HTML-Variante
* `ADMBw_QEA_Editor.aspx` — SharePoint-/IIS-Variante

## 1. Lokale Nutzung (empfohlen für Einzelplatz)

1. Datei `dist/ADMBw_QEA_Editor.html` speichern.
2. Per **Doppelklick** öffnen (aktueller Edge/Chrome/Firefox).
3. QEA-Datei auf die Seite ziehen — Auswertung startet automatisch.
   *Hinweis: Es werden keinerlei Daten übertragen; alles rechnet im Browser.*

## 2. SharePoint-Dokumentbibliothek

1. Zielbibliothek öffnen (z. B. „Dokumente" der Projekt- oder Referatsseite).
2. **`ADMBw_QEA_Editor.aspx`** hochladen (für die Bibliotheksansicht; die ASPX rendert ohne Server-Code).
3. Datei anklicken → sie wird direkt im Browser ausgeführt bzw. kann in einem neuen Tab geöffnet werden.
4. Für die **HTML-Variante**: `ADMBw_QEA_Editor.html` ebenfalls hochladen; je nach Farm-Konfiguration wird sie zum Download angeboten oder direkt angezeigt.

### Technische Vorgaben (bereits eingehalten)

* Die ASPX-Datei beginnt **direkt mit `<!DOCTYPE html>`**.
  **Es wird keine `<%@ Page Language=… %>`-Direktive vorangestellt** (die Farm-Parser lehnen die Direktive ab).
* Datei ist **UTF-8 mit BOM** gespeichert + `<meta charset>` und `<meta http-equiv="Content-Type">` als Absicherungen (verhindert Mojibake bei Umlauten).
* Die Datei enthält **keine `<%`-Sequenzen** (kein Server-Code).
* Keine externen Abhängigkeiten zur Laufzeit (kein CDN, keine Webfonts) — funktioniert auch in gesperrten Netzen vollständig offline.
* Die Datei ist **~1,3 MB** groß: Sie enthält eine eingebettete SQLite-Engine (sql.js, WebAssembly) für den lokalen Schreibpfad.

### Voraussetzungen

* Aktueller **Edge, Chrome oder Firefox** — **WebAssembly** muss aktiv sein (Standard; per Richtlinie abschaltbar).
  Wird WebAssembly blockiert, erscheint beim Speichern die Meldung „SQLite-Engine konnte nicht geladen werden".

### Arbeitsweise und Sicherheit

* Änderungen werden **vorgemerkt** und erst über „💾 Als neue .qea speichern" als **neue Datei** geschrieben (Download).
* Die geöffnete **Originaldatei wird nie verändert**.
* Es findet **keine Datenübertragung** statt.

### Empfohlener Ablauf beim Ersttest

1. **Kopie** des Modells verwenden (nicht das Referenzmodell direkt).
2. Eine kleine Änderung vormerken und speichern.
3. Die erzeugte `.qea` in Sparx EA öffnen und prüfen.
4. Erst danach mit echten Änderungen arbeiten.

### Prüfliste nach dem Upload

1. Seite öffnen → Header „ADMBw QEA Editor" mit Versions-Badge sichtbar?
2. Umlaute korrekt (z. B. „Sichten", „Prüfung")? Falls nicht → BOM/Zeichendekodierung prüfen.
3. QEA-Datei laden → Kennzahlenzeile („x Pakete · y Sichten …") erscheint?
4. Test-Export: eine Sicht öffnen → „📊 Sicht als Excel (.xlsx)" → Datei öffnet in Excel.
5. Test-Speichern: kleine Änderung vormerken → „💾 Als neue .qea speichern" → neue Datei im Download-Ordner; Ansicht aktualisiert sich.

## 3. Fehlersuche

| Symptom | Ursache / Abhilfe |
|---|---|
| Mojibake („Ã¤", „Ã¶") | BOM verloren (Datei wurde z. B. über einen Editor ohne BOM neu gespeichert) → Original aus diesem Repo verwenden |
| „Seite kann nicht angezeigt werden" beim ASPX-Aufruf | Bibliothek erlaubt kein Ausführen von ASPX → HTML-Variante nutzen oder Datei in einen Ordner mit Ausführungsrechten legen (Admin) |
| „SQLite-Engine konnte nicht geladen werden" | Browser blockiert WebAssembly (selten, z. B. per Richtlinie) → Richtlinie prüfen; Analyse bleibt nutzbar |
| Kein Download beim Speichern | Pop-up-/Download-Blocker für die Seite erlauben |
| Leere Seite im IE-Altbestand | Tool setzt ES5 voraus, benötigt aber aktuellen Browser (Chromium/Firefox); IE11 wird nicht unterstützt |
| Erzeugte Datei öffnet in EA nicht | **Bitte melden** (Issue im Repository) — mit EA-Version, Modellgröße und kurzer Beschreibung der Änderungen |

---

*Stand: 16.10.2026 · ADMBw QEA Editor v5.0 (Edit-Edition) — Testversion*
