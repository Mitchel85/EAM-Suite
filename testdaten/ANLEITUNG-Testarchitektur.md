# Testarchitektur für die EAM-Suite — Verbindung über zwei Architekturen hinweg

Zwei kleine Architekturdateien (Sparx EA, `.qea`) und eine Anleitung, mit der sich die
Kernfunktion der Suite zeigt: **zwei getrennte Architekturen laden, über eine gemeinsame
GUID zusammenführen und quer über beide Modelle eine Verbindung nachweisen.**

Laufzeit: ca. 3 Minuten. Keine Installation, keine KI, keine Cloud.

---

## 1. Dateien

| Datei | Inhalt | Elemente | Beziehungen |
|---|---|---|---|
| `QA_Taktische-Lagebildarchitektur.qea` | Taktische Architektur: System, Aktivität, zwei Dienste, zwei Informationsobjekte | 10 | 4 |
| `QB_Nationale-Lagebildarchitektur.qea` | Nationale Architektur: System, zwei Aktivitäten, Dienst-Referenz, Daten-Referenz | 8 | 5 |

**Gemeinsame Elemente** (identische `ea_guid` in beiden Dateien — das ist der Brückenschlag):

| Element | Stereotyp | Rolle |
|---|---|---|
| Betriebsdienst Lagebild | `ServiceSpecification` | wird von A geliefert und in B genutzt |
| Lagebilddaten (NATO-Standard) | `InformationElement` | Datenaustausch zwischen beiden Architekturen |

Zusätzlich sind reale NAFv4-Beziehungstypen gesetzt: `ActivitySupportsService` und
`ServiceExchange`. Alle Stereotype sind nach der EA-Konvention zusätzlich in `t_xref`
eingetragen (`@STEREO;Name=…;FQName=NAFv4::…;@ENDSTEREO;`), sodass die Dateien in Sparx EA
korrekt geöffnet werden.

---

## 2. Anleitung — Verbindung über zwei Architekturen

**Werkzeug:** Architektur Mate — EAM-Suite
`https://mitchel85.github.io/EAM-Suite/EAM_Suite.html`

### Schritt 1 — Mehrfachmodus vorbereiten
1. Seite öffnen.
2. Auf dem Startbildschirm **🗂️ „Mehrere verschmelzen"** anklicken.
   *Wichtig:* Erst den Knopf drücken, dann die Dateien wählen. Werden die Dateien einzeln
   nachgeladen, ersetzt die zweite die erste.

### Schritt 2 — Beide Architekturen laden
3. **📂 Datei laden** anklicken und **beide** `.qea`-Dateien gemeinsam markieren
   (Strg-Klick bzw. Umschalt-Klick) und öffnen.
4. Oben erscheint: *„🗂️ 2 Architekturen geladen"* — M1 (QA) und M2 (QB) mit ihren Kennzahlen.

### Schritt 3 — Zusammenführung prüfen
5. In der Leiste steht *„2 Element(e) wurden über die Dateigrenzen hinweg erkannt
   (Kriterien: Über GUID)"*.
6. Auf **👁 „2 Zusammenführungen prüfen"** klicken. Erwartetes Ergebnis:
   - `Betriebsdienst Lagebild` → `Betriebsdienst Lagebild`
   - `Lagebilddaten (NATO-Standard)` → `Lagebilddaten (NATO-Standard)`
7. Bestätigen. Die beiden Elemente existieren jetzt **einmal** im Gesamtmodell und tragen
   beide Beziehungen aus A und B — das ist die Brücke.
8. Optional **🔍 Fusionsbericht** öffnen: dokumentiert, was zusammengelegt wurde.

### Schritt 4 — Verbindung über beide Architekturen nachweisen
9. Reiter **🔗 Verbindungen** wählen (Pfadanalyse).
10. **Start-Element:** `Lage erfassen` (QA, `OperationalActivity`)
11. **Ziel-Element:** `Lagebild auswerten` (QB, `ResourceActivity`)
12. **🔎 Verbindung suchen**.

**Erwartetes Ergebnis:**
```
✔ Verbindung gefunden: 2 Hops · 3 Elemente · 2 Beziehungen
Lage erfassen            [QA]  OperationalActivity
   ActivitySupportsService „unterstützt"
Betriebsdienst Lagebild  [QA]  ServiceSpecification
   ActivitySupportsService „nutzt"      ← Brücke nach QB
Lagebild auswerten       [QB]  ResourceActivity
```
Entscheidend: Schritt 1 und 2 liegen in **QA**, Schritt 3 in **QB**. Ohne die
GUID-Zusammenführung wäre die Kette unterbrochen.

### Schritt 5 — Gegenprobe (beweist, dass die Brücke wirkt)
13. **✕ „Auflösen"** in der Mehrfach-Leiste klicken (Zusammenführung zurücknehmen).
14. Dieselbe Suche erneut ausführen.
15. Ergebnis: *„Keine Verbindung … gefunden"* mit der Architektur-Diagnose
   („zwei getrennte Zusammenhangskomponenten"). Das zeigt den Unterschied zwischen
   **nur geladen** und **wirklich zusammengeführt**.

---

## 3. Weitere Funktionen, die sich mit den Dateien zeigen lassen

| Funktion | Vorgehen | Erwartung |
|---|---|---|
| **GUID als Standardkriterium** | Startbildschirm → ⚙️ Erweitert | „Über GUID" ist vorbelegt; Name und Alias sind zuschaltbar (experimentell) |
| **Paketstruktur** | Reiter 🧭 Erkunden | QA und QB als getrennte Wurzelpakete, je 3–4 Unterpakete |
| **Stereoetypen** | Element-Steckbrief öffnen | `ServiceSpecification`, `InformationElement`, `OperationalActivity` etc. |
| **Sichten** | Reiter 🖼️ Sichten | „QA Übersicht" und „QB Übersicht" |
| **Graph** | Reiter 🕸️ Graph | beide Modelle als ein Netz, inkl. Brückenknoten |
| **Referenz-Grid** | Reiter 📐 Referenz-Grid | zeigt, welche NAFv4-Sichten die Dateien abdecken |
| **Export** | Excel / PNG / CSV / PDF | Ausgabe des Gesamtmodells inkl. Herkunft (M1/M2) |

---

## 4. Technische Hinweise

- Format: SQLite (`.qea`), direkt von Sparx EA lesbar.
- Beide Dateien sind bewusst klein (~52 KB) — sie lassen sich in Sekunden laden und
  eignen sich zum Vorführen ohne Wartezeit.
- Die GUIDs sind stabil erzeugt (`uuid5`), der Aufbau ist reproduzierbar über
  `tools/build_testarchitekturen.py`.
- Die Dateien enthalten keine personenbezogenen Daten.
- Wer die Brücke testen will, ohne sie zu bestätigen: schon im Zustand „nicht
  zusammengeführt" zeigt der Pfad die Diagnose „zwei getrennte Komponenten" — genau das
  erwartet man ohne GUID-Match.
