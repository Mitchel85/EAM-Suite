# ADMBw QEA Editor

**Sparx-EA-Architekturen im Browser bearbeiten — 100 % lokal, ohne KI, ohne Installation, ohne Server.**

Einzeldatei-Tool (HTML & ASPX) für Architekturmodelle im SQLite-Format (`.qea` / `.eapx` / `.qeax`):
Elemente, Pakete, Sichten, Beziehungen und Tagged Values **ändern**, Elemente & Beziehungen **anlegen** und **entfernen** — geschrieben wird in eine **neue `.qea`-Datei**, das Original bleibt unangetastet.

> **Testphase — Feedback willkommen.** Dies ist eine **Edit-Edition zum Mit-Testen**. Bitte mit einer **Kopie** des Modells arbeiten und die erzeugte Datei vor der Weiterverwendung einmal in Sparx EA öffnen und prüfen. Rückmeldungen (auch Fehlerfälle) sind ausdrücklich erwünscht.

![Bearbeiten-Buttons im Steckbrief](docs/img/vorschau_edit_steckbrief.png)

---

## Was das Tool kann

### Bearbeiten
| Objekt | Änderbar |
|---|---|
| **Element** | Name, Stereotype, Alias, Status, Beschreibung/Notiz |
| **Paket** | Name, Beschreibung (wird in `t_package` **und** der gespiegelten `t_object`-Zeile gepflegt) |
| **Sicht / Diagramm** | Name, Beschreibung |
| **Beziehung** | Name, Stereotype (inkl. `t_xref`-Eintrag und «…»-Label), Richtung, Beschreibung |
| **Tagged Values** | ändern, ergänzen, entfernen |

### Anlegen & Entfernen
* **Neu:** Elemente in einem Paket (beliebiger Objekttyp), Beziehungen zwischen zwei Elementen (mit Zielsuche über Name/Alias/Stereotype).
* **Löschen:** einzelne Elemente mit vollständiger **Kaskade** (Beziehungen, Sicht-Platzierungen, Tags, Diagramm-Links, Attribut-/xref-Einträge) und einzelne Beziehungen.

### Prinzip: Vormerken statt Sofort-Schreiben
Alle Änderungen landen in einer **Änderungsliste** (mit Alt→Neu-Gegenüberstellung, einzeln entfernbar) und werden erst über **„💾 Als neue .qea speichern"** geschrieben — in eine **neue Datei**. Änderungsprotokoll als CSV exportierbar.

### Analyse inklusive
Die vollständige Analyse-Funktionalität des [ADMBw QEA Analyzers](https://github.com/Mitchel85/admbw-qea-analyzer) ist enthalten: Paket- & Sichten-Explorer, globale Sofort-Suche, interaktiver Graph (ADMBw/NAFv4-Farben), Verbindungs-/Pfadanalyse mit Architektur-Diagnose sowie 1-Klick-Export jeder Sicht als **PNG** oder **Excel (.xlsx)**.

![Element-Editor](docs/img/vorschau_edit_editor.png)
![Änderungsliste](docs/img/vorschau_edit_aenderungen.png)
![Gespeichert](docs/img/vorschau_edit_gespeichert.png)

---

## Schnellstart

1. `dist/ADMBw_QEA_Editor.html` herunterladen (oder *Raw → Datei speichern*).
2. Per Doppelklick im Browser öffnen (aktueller Edge/Chrome/Firefox).
3. `.qea`-Datei per Drag & Drop laden.
4. Änderungen vornehmen (✏️-Buttons im Steckbrief, in Tabellen und an Paketen/Sichten).
5. **„✏️ Bearbeiten"** oben rechts öffnet die Änderungsliste → **„💾 Als neue .qea speichern"**.
6. Die neue Datei erscheint im Download-Ordner; die Ansicht springt automatisch auf den gespeicherten Stand.

> **Erster Test:** mit einer **Kopie** arbeiten und das Ergebnis in Sparx EA prüfen.

## Deployment (SharePoint / Bw-Netz)

| Datei | Verwendung |
|---|---|
| `dist/ADMBw_QEA_Editor.html` | Lokale Nutzung (Doppelklick) oder SharePoint-Dokumentbibliothek |
| `dist/ADMBw_QEA_Editor.aspx` | SharePoint-/IIS-Bibliothek (beginnt direkt mit `<!DOCTYPE html>`) |

**Wichtig:** Die ASPX-Datei beginnt **direkt mit `<!DOCTYPE html>`** — es wird **keine** `<%@ Page … %>`-Direktive vorangestellt. Beide Dateien sind **UTF-8 mit BOM** und enthalten keine `<%`-Sequenzen. Details: [docs/SharePoint-Deployment.md](docs/SharePoint-Deployment.md)

## Technischer Aufbau

Eine einzige HTML-Datei (~1,29 MB), modular aus Bausteinen gebaut:

```
src/part1_head_body.html   Struktur & Design (CSS, Reiter, Ansichten, Edit-UI)
src/part2_app_core.js      Modell-Aufbau, Suche, Exporte (PNG/XLSX/CSV)
src/part3_app_graph.js     Diagramme, Steckbriefe, interaktiver Graph
src/part4_path.js          Verbindungs-/Pfadanalyse (BFS, Alternativpfade, Diagnose)
src/part5_edit.js          Edit-Modus: Änderungsliste, Editoren, SQLite-Schreibpfad
vendor/sql-wasm.js/.wasm   sql.js (MIT) — eingebettete SQLite-Engine für den Schreibpfad
src/build_release.py       Assembler: baut HTML + ASPX, bettet WASM ein (node --check)
```

```bash
python3 src/build_release.py   # Pfade im Skript ggf. anpassen
```

### Wie das Schreiben funktioniert
Die `.qea`-Datei ist eine SQLite-Datenbank. Zum Schreiben wird eine **echte SQLite-Engine** (sql.js, als WebAssembly eingebettet) im Browser gestartet — die Datei bleibt damit strukturell eine valide EA-Datenbank. Vor jedem Export laufen `PRAGMA integrity_check` und ein Selbsttest mit dem eingebauten Reader.

Dabei werden die EA-Konventionen berücksichtigt: getrennte AUTOINCREMENT-Sequenzen je Tabelle, Paket-Spiegelung über `ea_guid`, entity-kodierte Notizen (`&#252;`, CRLF), `t_xref`-Stereotype-Einträge (inkl. `FQName`), «…»-Labels auf Diagrammen sowie die vollständigen Lösch-Kaskaden.

### Sicherheit
* Das Modell verlässt den Rechner **nicht** — keine Netzverbindung, kein CDN, keine Telemetrie.
* Die geöffnete Originaldatei wird **nie** überschrieben.
* Es wird ausschließlich die vom Nutzer geladene Datei gelesen und eine neue Datei erzeugt.

## Getestet mit

Musterarchitektur **MASC** (12,4 MB; 225 Pakete, 265 Sichten, 1.652 Elemente, 1.746 Beziehungen):
* 10 Änderungsarten (Umbenennen, Stereotype, Notizen, Tags, Anlegen, Löschen inkl. Kaskaden) — alle Struktur- und Integritätsprüfungen grün
* Speichern inkl. Integritätsprüfung und Export: **~3 Sekunden**
* Die vollständige Analysefunktionalität wurde regressionsgetestet.

Testmodell: `https://github.com/Mitchel85/eam-qea-tool` → `Demo-Output/Musterarchitektur_MASC.qea`

## Mitmachen / Feedback

Dieses Repository ist **bewusst als Testversion** veröffentlicht. Interessant sind besonders:
* Modelle, bei denen etwas **nicht** wie erwartet funktioniert (Lösch-Kaskaden, Sonder-Stereotype, große Dateien)
* Rückmeldungen aus der **Praxis mit Sparx EA** (öffnet EA die erzeugte Datei sauber?)
* Hinweise zu EA-Konventionen, die noch nicht berücksichtigt sind

Am einfachsten per **Issue** hier im Repository — gerne mit kurzer Beschreibung, EA-Version und ggf. anonymisiertem Beispielfall.

## Verwandte Projekte

| Repository | Zweck |
|---|---|
| [admbw-qea-analyzer](https://github.com/Mitchel85/admbw-qea-analyzer) | Analyse-Version (nur lesen, ~300 KB) |
| [eam-qea-tool](https://github.com/Mitchel85/eam-qea-tool) | Natürlichsprachliche Abfragen an QEA-Modelle |
| [admbw-extractor](https://github.com/Mitchel85/admbw-extractor) | ADMBw-Viewpoints aus Prosa ableiten |
| [sparx-ea-scripts](https://github.com/Mitchel85/sparx-ea-scripts) | JavaScript-Automatisierung in Sparx EA |

---

*Autor: Michael Estel · *
*Enthält [sql.js](https://github.com/sql-js/sql.js) (MIT-Lizenz) — siehe `vendor/LICENSE-sql.js`.*
