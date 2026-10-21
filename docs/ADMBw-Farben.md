# ADMBw/NAFv4-Farben im QEA Analyzer

Die Knoten- und Elementfarben des Tools folgen der offiziellen Farbgebung des **NATO Architecture Framework v4** und deren Umsetzung im **Architekturdatenmodell der Bundeswehr (ADMBw)**. Dieses Dokument belegt die verwendeten Farbwerte anhand der primären Quellen.

## Verwendete Palette (ADMBw-Umsetzung)

Umgesetzt in Sparx Systems Enterprise Architect.

| Architekturbereich | Schichtfarbe (Rand/Header) | Elementfüllung (hell) | Verwendung im Tool |
|---|---|---|---|
| **Konzepte & Fähigkeiten** | `#C8D300` | `#F6FF5D` | «Capability», «ActualEnterprisePhase», Enterprise-Phase-Elemente |
| **Dienste (Services)** | `#CE8ABB` | `#E7C7DE` | «ServiceSpecification», «Service» |
| **Logik & Prozesse** | `#66B2E4` | `#B2D8F1` | Knoten, «OperationalActivity», Information, Rollen |
| **Systeme & Ressourcen / Organisation** | `#EF7D00` | `#FFCA90` | «ResourcePerformer», «ResourceArtifact», Ausrüstung, Organisationen |
| **Anforderungen & Normen** | `#C9C9C9` | `#EDEDED` | «Requirement», «ResourceConstraint», Concerns |
| **Weitere / generische Elemente** | `#DADADA` | `#F2F2F2` | generische abstrakte Elemente (NAFv4.1) |

## Quellenlage (öffentlich belegt)

1. **NATO Architecture Framework v4.1**, Kap. 3, Abschnitt 2.4.3, Abb. 18 „Domain Colour Scheme":
   Jede Architekturdomäne hat *zwei* Farben — eine Header-Farbe aus der NAF-Grid-Palette und eine hellere Elementfarbe für Viewpoint-Ausschnitte. Generische (abstrakte) Elemente sind hellgrau (`#DADADA`).

2. **Bundeswehr: „Grundlagen Methode Architektur nach NAFv4" v1.1 (16.12.2025)**, Abb. 36 (S. 58) — explizite Legende:
   Concepts `#C9D301` · Logical `#66B2E4` · Service `#CE8ABC` · Resources `#EF7D00` · Requirements `#CBCBCB` · Foundation `#FFD618`.
   Ebenda Abb. 35: Aufgabenträger/Information = Logical (blau), Ausrüstung/Organisation = Resources (orange).

3. **Bundeswehr: „Dokumentation Verwendung des ADMBw im Sparx EA" v2.0 (21.05.2024)** — Umsetzung in Sparx EA:
   Grid (Abb. 35, S. 42): Concepts `#C8D300`/`#F6FF5D` · Service `#CE8ABB`/`#E7C7DE` · Logical `#66B2E4`/`#B2D8F1` · Physical `#EF7D00`/`#FFCA90` · Requirement `#C9C9C9`/`#EDEDED`.
   Element-Beispiele: «Capability» `#C8D300` (S. 43) · «ServiceSpecification» `#CE8ABB` (S. 51) · «OperationalActivity»/Knoten `#66B2E4` (S. 65) · «ResourcePerformer»/Organisation `#EF7D00` (S. 50/72/75).

## Umsetzung im Tool

* **Graphen & Pfad-Graph:** Knoten = Elementfüllung + Rand in Schichtfarbe (entspricht der Darstellung der Elemente in den Original-Schaubildern).
* **EA-Diagramm-Nachbildung:** Boxen mit heller Füllung, farbigem Stereotyp-Band und farbigem Rand.
* **PNG-/Excel-Exporte:** übernehmen dieselbe Codierung.
* Die Farbzuordnung erfolgt automatisch anhand des Stereotyps (`archCategory()`/`CAT_META` in `src/part2_app_core.js`).

> Hinweis: Die Farben sind eine **Visualisierungshilfe** und ersetzen keine methodische Prüfung der Modellinhalte.
