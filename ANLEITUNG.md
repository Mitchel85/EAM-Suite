# Architektur Mate — Kurzanleitung (Ihr Architekturgehilfe)

**Ein Satz:** QEA-Architektur(en) im Browser öffnen, verstehen, ändern — und als **neue** Datei speichern. Ohne Installation, alles bleibt lokal.

---

## In 5 Minuten

### 1 · Öffnen
`dist/Architektur_Mate.html` herunterladen, per Doppelklick im Browser öffnen (Edge / Chrome / Firefox).

### 2 · Laden
- **Eine Datei:** Button **„📄 Eine Architektur laden"**
- **Mehrere Dateien:** Button **„🗂️ Mehrere Architekturen verschmelzen"**

Datei(en) auf die Fläche ziehen oder anklicken.

### 3 · (Bei mehreren Dateien) Kriterien wählen
Ankreuzen, wonach gleiche Elemente erkannt werden:

| ☑ | Kriterium | Bedeutung |
|---|---|---|
| ☑ | **Über GUID** | gleiche Kennung (URI/UUID) — **empfohlen** |
| ☐ | **Über den Namen** | gleiche Bezeichnung — *experimentell* |
| ☐ | **Über den Alias** | gleicher Alternativname — *experimentell* |

Kästchen einzeln an/aus — beliebig kombinieren. **Standard ist nur „Über GUID".** ⚠️ **Achtung:** Je mehr Kriterien Sie ankreuzen, desto **instabiler** wird die Anwendung und desto höher ist die Wahrscheinlichkeit, dass sie **abstürzt**. Die anderen beiden Kriterien gelten als **experimentell**. Danach erscheint ein **Prüf-Dialog**: jede Überschneidung einzeln sichtbar, Häkchen rausnehmen, wenn etwas eigenständig bleiben soll. Dann **„✔ Ausgewählte zusammenlegen"**.

### 4 · Ansehen
- Links: Baum mit **Paketen & Sichten**
- **Suche** oben: sofort über alle Elemente
- Klick auf ein Element: **Steckbrief** — zeigt bei verschmolzenen Elementen, in welchen Architekturen sie vorkommen, mit **Sprung-Button**
- **Beziehungen**: Verbindungen über die Dateigrenze sind mit **„Modellgrenze"** markiert

### 5 · Ändern & Speichern
- ✏️ klicken → Feld ändern → speichern (Änderungen werden nur **vorgemerkt**)
- **„✏️ Bearbeiten"** zeigt die Änderungsliste (einzeln entfernbar)
- **„💾 Als neue .qea speichern"** → neue Datei im Download-Ordner

**Wichtig:**
- Das **Original wird nie überschrieben**
- Bei mehreren Dateien bekommt **jede Quelldatei** ihre eigene neue Datei
- Ergebnis einmal in **Sparx EA** öffnen und prüfen
- Am besten immer mit einer **Kopie** arbeiten

---

## Häufige Fragen

**Was bedeutet „verschmelzen"?**
Elemente, die nach den gewählten Kriterien als gleich erkannt werden, teilen sich einen Knoten. Dadurch sieht man Verbindungen, die über die Architekturgrenze hinweggehen.

**Was, wenn ich nichts zusammenführen will?**
Alles abwählen oder das Kontrollkästchen „Semantik einbeziehen" aus. Die Dateien werden dann nur nebeneinander gestellt.

**Kann ich eine Zusammenführung zurücknehmen?**
Ja — im Prüf-Dialog einzelne Häkchen entfernen. Nach dem Bestätigen: Button **„✕ Auflösen"** in der Leiste.

**Warum sehe ich IDs wie `m2_o145`?**
Modell 1 behält die Original-IDs. Ab Modell 2 bekommen Elemente einen Präfix (`m2_` = zweite Datei), damit nichts verwechselt wird.

**Wo wird gespeichert?**
In eine **neue** Datei, z. B. `Modell_bearbeitet_20261016-1620.qea`. Das Original bleibt unverändert.

---

*Mehr Details: [README.md](README.md) · Fragen & Probleme: Issue im Repository*
