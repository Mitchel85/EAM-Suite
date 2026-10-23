# QC_Weltraumlage-Erweiterung — Auswertung zusammen mit der Musterarchitektur MASC

Diese Architektur ist **kein Ersatz** für die Musterarchitektur, sondern eine Ergänzung.
Sie zeigt, wie die EAM-Suite eine **eigene Architektur mit einer bestehenden Musterarchitektur
verbindet** — ohne die Musterarchitektur zu kopieren oder zu verändern.

Getestet gegen `Musterarchitektur_MASC.qea` (1655 Elemente, 1747 Beziehungen).

---

## 1. Das Prinzip

Die Erweiterung enthält drei Elemente, die **keine eigenen Objekte** sind, sondern
**Referenzen auf die Musterarchitektur**. Sie tragen exakt dieselbe `ea_guid`:

| Element in der Erweiterung | Stereotyp | GUID (aus MASC, unverändert) |
|---|---|---|
| Weltraumstart durchführen | `OperationalActivity` | `{A19AF4C0-1423-40d3-B7F9-4BE7336B441B}` |
| Spacecraft Information Service Bw | `ServiceSpecification` | `{4127A042-10BA-46c9-AB31-86E3C885DD69}` |
| GIS Service Bw | `ServiceSpecification` | `{ABEEB568-CFB0-4643-9251-F746416F249A}` |

Beim Laden im Mehrfachmodus erkennt die Suite diese Elemente als **dasselbe Element** und
führt sie zusammen. Danach trägt ein Element die Beziehungen aus **beiden** Architekturen —
die Brücke steht.

**Warum das funktioniert:** Die GUID ist die Identität eines Modellelements in Sparx EA. Wer
dieselbe GUID verwendet, sagt damit aus: „das ist dasselbe Element, hier nur in einem anderen
Kontext verwendet". Genau dafür ist das Kriterium „Über GUID" gemacht.

---

## 2. Was die Erweiterung selbst enthält

| Element | Stereotyp | Rolle |
|---|---|---|
| Weltraumlagezentrum Boden | `OperationalPerformer` | Bodeneinrichtung, die auswertet und in die Führung einbringt |
| Weltraumlage bewerten | `OperationalActivity` | verdichtet Aufklärungs- und Statusdaten zu einer Weltraumlage |
| Weltraumlage-Auswertedienst | `ServiceSpecification` | stellt die bewertete Weltraumlage als Dienst bereit |
| Auswertesystem Boden | `System` | System, auf dem der Dienst läuft |
| Weltraumlagebericht | `InformationElement` | Ergebnis der Bewertung für die Führung |
| Statusmeldung Raumschiff | `InformationElement` | Eingangsdaten aus dem Raumsegment |

**Beziehungen der Erweiterung (9):**

| Von | Beziehung | Nach | Bedeutung |
|---|---|---|---|
| Weltraumlage bewerten | `ActivitySupportsService` | Weltraumlage-Auswertedienst | Aktivität unterstützt den Dienst |
| Weltraumlage bewerten | `ActivityPerformedByPerformer` | Weltraumlagezentrum Boden | wird ausgeführt von |
| Weltraumlage bewerten | `ServiceDependency` | **GIS Service Bw** | **Brücke 1 → MASC** |
| Weltraumlage bewerten | `ActivityDependency` | **Weltraumstart durchführen** | **Brücke 2 → MASC** |
| Weltraumlage-Auswertedienst | `ServiceExchange` | Weltraumlagebericht | liefert das Ergebnis |
| Weltraumlage-Auswertedienst | `ServiceDependency` | **Spacecraft Information Service Bw** | **Brücke 3 → MASC** |
| Spacecraft Information Service Bw (Ref.) | `ServiceExchange` | Statusmeldung Raumschiff | liefert Statusdaten |
| GIS Service Bw (Ref.) | `ServiceExchange` | Statusmeldung Raumschiff | liefert Geodaten |
| Auswertesystem Boden | `ServiceDeployment` | Weltraumlage-Auswertedienst | betreibt den Dienst |

Die drei Fettdruck-Zeilen sind die Übergänge in die Musterarchitektur.

---

## 3. Ablauf (ca. 2 Minuten)

**Werkzeug:** `https://mitchel85.github.io/EAM-Suite/EAM_Suite.html`

### Schritt 1 — Mehrfachmodus
1. Startbildschirm → **🗂️ „Mehrere verschmelzen"** anklicken.
   *Erst den Knopf, dann die Dateien* — sonst ersetzt die zweite Datei die erste.

### Schritt 2 — Beide Dateien laden
2. **📂 Datei laden** → beide Dateien gemeinsam markieren:
   - `Musterarchitektur_MASC.qea`
   - `QC_Weltraumlage-Erweiterung.qea`
3. Oben erscheint:
   ```
   M1  Musterarchitektur_MASC        226 Pakete · 265 Sichten · 1655 Elemente · 1747 Beziehungen
   M2  QC_Weltraumlage-Erweiterung     4 Pakete ·   1 Sichten ·   13 Elemente ·    9 Beziehungen
   ```

### Schritt 3 — Brücken prüfen und bestätigen
4. Die Suite meldet: **„3 Element(e) wurden über die Dateigrenzen hinweg erkannt (Kriterien: Über GUID)"**.
5. Auf **👁 „3 Zusammenführungen prüfen"** klicken. Erwartete Paare:
   - `Weltraumstart durchführen` → `Weltraumstart durchführen`
   - `Spacecraft Information Service Bw` → `Spacecraft Information Service Bw`
   - `GIS Service Bw` → `GIS Service Bw`
6. Bestätigen.

### Schritt 4 — Pfad über beide Architekturen
7. Reiter **🔗 Verbindungen** öffnen.
8. **Start:** `Weltraumlage bewerten` (Erweiterung, `OperationalActivity`)
9. **Ziel:** `Aufklärungselement Weltraum` (MASC, `OperationalPerformer`)
10. **🔎 Verbindung suchen**

**Erwartetes Ergebnis (real gemessen):**
```
✔ Verbindung gefunden: 4 Hops · 5 Elemente · 4 Beziehungen · 0,4 ms

Weltraumlage bewerten                [QC]    OperationalActivity
  ActivitySupportsService „unterstützt"
Weltraumlage-Auswertedienst          [QC]    ServiceSpecification
  ServiceDependency „nutzt"
Spacecraft Information Service Bw    [MASC]  ServiceSpecification   ← Übergang
  ServiceDependency „nutzt Sensordaten"
Bemanntes Aufklärungselement Weltraum [MASC] OperationalPerformer
  PropertySetGeneralisation
Aufklärungselement Weltraum          [MASC]  OperationalPerformer
```
Die Kette beginnt in der eigenen Architektur, wechselt nach zwei Schritten in die
Musterarchitektur und endet dort. Genau das ist der Nachweis der Verbindung über die
Architekturgrenze.

### Schritt 5 — Gegenprobe
11. **✕ „Auflösen"** klicken (Zusammenführung zurücknehmen).
12. Dieselbe Suche erneut starten.
13. Ergebnis: **„Keine Verbindung gefunden"** — die Elemente sind wieder getrennt.
    Damit ist belegt, dass die Verbindung tatsächlich aus der GUID-Zusammenführung entsteht
    und nicht aus Zufallstreffern.

---

## 4. Weitere Auswertungen mit MASC

| Frage | Vorgehen | Erwartung |
|---|---|---|
| Welche MASC-Services nutzt die Erweiterung? | Graph → Nachbarschaft von `Weltraumlage-Auswertedienst` | `Spacecraft Information Service Bw`, `GIS Service Bw` |
| Wie hängt der Dienst im MASC-Kontext? | Pfad `Weltraumlage-Auswertedienst` → `Information Management Services` | Weg über `ServiceClassification` |
| Wo steht die Aktivität im MASC-Bild? | Pfad `Weltraumlage bewerten` → `Weltraumstart durchführen` | direkte `ActivityDependency` (Brücke 2) |
| Vollständiges Bild | Reiter 🕸️ Graph | MASC-Netz mit angehängter QC-Teilarchitektur |
| Export | 📊 Excel | Gesamtmodell mit Herkunftsspalte (M1/M2) |

---

## 5. Technische Hinweise

- Beide Dateien sind Sparx-EA-kompatibel (SQLite, `.qea`).
- Die Erweiterung ist klein (~41 KB) und lädt in Sekunden; MASC bringt ~12 MB mit.
- Die verwendeten GUIDs stammen unverändert aus `Musterarchitektur_MASC.qea` — es sind
  **keine** neu erzeugten Werte. Wer die Musterarchitektur ändert, muss die GUIDs dort
  entnehmen (Abfrage: `SELECT ea_guid FROM t_object WHERE Name='…'`).
- Die Datei enthält keine personenbezogenen Daten.
- Nachladbar über `tools/build_erweiterung_weltraumlage.py`.
- Hinweis der Suite: In der Erweiterung fehlt die Tabelle `t_diagramlinks`; die Suite meldet
  das als Hinweis, die Auswertung läuft vollständig. Für eine produktive Nutzung in Sparx EA
  ergänzt Sparx Systems diese Tabelle beim ersten Öffnen und Speichern selbst.
