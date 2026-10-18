# Architektur Mate — Kurzanleitung

**Ein Satz:** QEA-Architektur(en) im Browser öffnen, verstehen, ändern — und als **neue** Datei speichern. Ohne Installation, alles bleibt lokal.

---

## In 4 Schritten

### 1 · Öffnen & Laden
`dist/Architektur_Mate.html` herunterladen, per Doppelklick im Browser öffnen. Dann:
- **„📄 Eine Architektur laden"** — eine Datei
- **„🗂️ Mehrere verschmelzen"** — zwei oder mehr zu **einer** Landkarte

Datei(en) aufziehen oder anklicken.

### 2 · (Nur mehrere) Kriterien wählen
Unter **„⚙️ Erweitert"** ankreuzen, wonach gleiche Elemente erkannt werden. **Standard: „Über GUID"** — das ist die empfohlene, stabilste Einstellung. „Über den Namen" und „Über den Alias" sind experimentell. Danach erscheint ein **Prüf-Dialog**: Häkchen einzeln entfernen, wenn etwas eigenständig bleiben soll, dann **„✔ Ausgewählte zusammenlegen"**.

### 3 · Ansehen
- Links: Baum mit **Paketen & Sichten**
- **Suche** oben: sofort über alle Elemente
- Klick auf ein Element: **Steckbrief** (zeigt bei verschmolzenen Elementen, wo sie überall vorkommen)
- Verbindungen über die Dateigrenze sind mit **„Modellgrenze"** markiert

### 4 · Ändern & Speichern
- ✏️ klicken → Feld ändern (wird **vorgemerkt**)
- **„💾 Als neue .qea speichern"** → neue Datei im Download-Ordner

**Wichtig:**
- Das **Original wird nie überschrieben**
- Bei mehreren Dateien bekommt **jede Quelle** ihre eigene neue Datei
- Ergebnis einmal in **Sparx EA** öffnen und prüfen; mit einer **Kopie** arbeiten

---

## Häufige Fragen

**Was bedeutet „verschmelzen"?**
Elemente, die nach den Kriterien als gleich erkannt werden, teilen sich einen Knoten — so werden Verbindungen über die Architekturgrenze sichtbar.

**Nichts zusammenführen?**
Alle Kriterien abwählen oder „Semantik einbeziehen" aus. Die Dateien werden dann nur nebeneinander gestellt.

**Zusammenführung zurücknehmen?**
Im Prüf-Dialog Häkchen entfernen; nach dem Bestätigen: Button **„✕ Auflösen"**.

**Was bedeuten IDs wie `m2_o145`?**
Modell 1 behält Original-IDs, ab Modell 2 kommt ein Präfix (`m2_` = zweite Datei) zur Unterscheidung.

**Wo wird gespeichert?**
In eine **neue** Datei, z. B. `Modell_bearbeitet_20261016-1620.qea`. Das Original bleibt unverändert.

---

*Mehr Details: [README.md](README.md) · Fragen: Issue im Repository*
