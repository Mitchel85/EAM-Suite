#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Erzeugt QC_Weltraumlage-Erweiterung.qea — eine Erweiterungsarchitektur, die
zusammen mit der Musterarchitektur MASC (Musterarchitektur_MASC.qea) ausgewertet
wird.

Brücke: Die drei Modellelemente aus MASC werden mit ihren ECHTEN ea_guids
referenziert (kein Nachbau, keine Kopie):

  Spacecraft Information Service Bw   {4127A042-10BA-46c9-AB31-86E3C885DD69}  ServiceSpecification
  GIS Service Bw                      {ABEEB568-CFB0-4643-9251-F746416F249A}  ServiceSpecification
  Weltraumstart durchführen           {A19AF4C0-1423-40d3-B7F9-4BE7336B441B}  OperationalActivity

Dadurch entsteht beim Laden beider Dateien im Mehrfach-Modus eine durchgehende
Beziehungskette von der Auswertungs-Architektur über die beiden MASC-Services
bis in die operationelle Aktivität der Musterarchitektur.

Aufruf:  python3 tools/build_erweiterung_weltraumlage.py
"""
import sqlite3
import uuid
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "testdaten"
NS = uuid.UUID("7d3e6f10-0000-4000-8000-000000000000")

# --- echte GUIDs aus Musterarchitektur_MASC.qea (unverändert übernommen) -----
G_MASC_SPACECRAFT_SVC = "{4127A042-10BA-46c9-AB31-86E3C885DD69}"
G_MASC_GIS_SVC = "{ABEEB568-CFB0-4643-9251-F746416F249A}"
G_MASC_WELTRAUMSTART = "{A19AF4C0-1423-40d3-B7F9-4BE7336B441B}"


def g(tag: str) -> str:
    return "{" + str(uuid.uuid5(NS, tag)).upper() + "}"


SCHEMA = {
    "t_package": """
        CREATE TABLE t_package (
            Package_ID INTEGER PRIMARY KEY, Name TEXT, Parent_ID INTEGER,
            CreatedDate TEXT, ModifiedDate TEXT, Notes TEXT, ea_guid TEXT,
            XMLPath TEXT, IsControlled INTEGER, LastLoadDate TEXT,
            LastSaveDate TEXT, Version TEXT, Protected INTEGER, PkgOwner TEXT,
            UMLVersion TEXT, UseDTD INTEGER, LogXML INTEGER, CodePath TEXT,
            Namespace TEXT, TPos INTEGER, PackageFlags TEXT, BatchSave INTEGER,
            BatchLoad INTEGER)""",
    "t_object": """
        CREATE TABLE t_object (
            Object_ID INTEGER PRIMARY KEY, Object_Type TEXT, Name TEXT,
            Author TEXT, Note TEXT, Package_ID INTEGER, Stereotype TEXT,
            Status TEXT, Scope TEXT, Alias TEXT, Classifier INTEGER,
            ea_guid TEXT, ParentID INTEGER, TPos INTEGER)""",
    "t_connector": """
        CREATE TABLE t_connector (
            Connector_ID INTEGER PRIMARY KEY, Name TEXT, Direction TEXT,
            Notes TEXT, Connector_Type TEXT, Stereotype TEXT,
            Start_Object_ID INTEGER, End_Object_ID INTEGER,
            SourceRole TEXT, DestRole TEXT, ea_guid TEXT)""",
    "t_xref": """
        CREATE TABLE t_xref (
            XrefID INTEGER PRIMARY KEY, Name TEXT, Type TEXT, Visibility TEXT,
            "Namespace" TEXT, "Requirement" TEXT, "Constraint" TEXT, "Behavior" TEXT,
            "Partition" TEXT, "Description" TEXT, "Client" TEXT, "Supplier" TEXT,
            "Link" TEXT)""",
    "t_diagram": """
        CREATE TABLE t_diagram (
            Diagram_ID INTEGER PRIMARY KEY, Name TEXT, Type TEXT, Package_ID INTEGER,
            ea_guid TEXT)""",
}

BODY_TAIL = """
CREATE TABLE t_attribute (ID INTEGER PRIMARY KEY, Object_ID INTEGER, Name TEXT, Type TEXT,
    Stereotype TEXT, ea_guid TEXT);
CREATE TABLE t_operation (OperationID INTEGER PRIMARY KEY, Object_ID INTEGER, Name TEXT,
    Type TEXT, Stereotype TEXT, ea_guid TEXT);
CREATE TABLE t_objectproperties (PropertyID INTEGER PRIMARY KEY, Object_ID INTEGER,
    "Property" TEXT, "Value" TEXT, "Notes" TEXT);
CREATE TABLE t_diagramobjects (Instance_ID INTEGER PRIMARY KEY, Diagram_ID INTEGER,
    Object_ID INTEGER, RectTop INTEGER, RectLeft INTEGER, RectRight INTEGER,
    RectBottom INTEGER, ObjectStyle TEXT);
"""


class Arch:
    def __init__(self, path: Path):
        if path.exists():
            path.unlink()
        self.con = sqlite3.connect(path)
        self.con.executescript(";\n".join(v.strip().rstrip(";") for v in SCHEMA.values())
                               + ";" + BODY_TAIL)
        self.oid, self.cid, self.xid = 100, 200, 500

    def pkg(self, pid, name, parent, note=""):
        self.con.execute("INSERT INTO t_package (Package_ID, Name, Parent_ID, Notes, ea_guid, TPos,"
                         " PackageFlags) VALUES (?,?,?,?,?,?,?)",
                         (pid, name, parent, note, g(f"pkg-{pid}"), pid, "VICON=3;"))
        self.con.execute("INSERT INTO t_object (Object_ID, Object_Type, Name, Package_ID, ea_guid, TPos)"
                         " VALUES (?,?,?,?,?,?)", (pid, "Package", name, pid, g(f"pkg-{pid}"), pid))

    def el(self, name, stereotype, package_id, guid_value, note="", otype="Class"):
        self.oid += 1
        oid = self.oid
        self.con.execute("INSERT INTO t_object (Object_ID, Object_Type, Name, Package_ID, Stereotype,"
                         " Note, ea_guid, TPos) VALUES (?,?,?,?,?,?,?,?)",
                         (oid, otype, name, package_id, stereotype, note, guid_value, self.oid))
        if stereotype:
            self.con.execute("INSERT INTO t_xref (XrefID, Type, Description, Client) VALUES (?,?,?,?)",
                             (self._x(), "element property",
                              f"@STEREO;Name={stereotype};FQName=NAFv4::{stereotype};@ENDSTEREO;",
                              guid_value))
        return oid

    def con_(self, stereotype, src, dst, name="", ctype="Dependency"):
        self.cid += 1
        cid = self.cid
        cg = g(f"conn-{cid}")
        self.con.execute("INSERT INTO t_connector (Connector_ID, Name, Connector_Type, Stereotype,"
                         " Start_Object_ID, End_Object_ID, ea_guid) VALUES (?,?,?,?,?,?,?)",
                         (cid, name, ctype, stereotype, src, dst, cg))
        if stereotype:
            self.con.execute("INSERT INTO t_xref (XrefID, Type, Description, Client) VALUES (?,?,?,?)",
                             (self._x(), "connector property",
                              f"@STEREO;Name={stereotype};FQName=NAFv4::{stereotype};@ENDSTEREO;", cg))
        return cid

    def _x(self):
        self.xid += 1
        return self.xid


def build():
    a = Arch(OUT / "QC_Weltraumlage-Erweiterung.qea")

    a.pkg(1, "QC Weltraumlage-Erweiterung", 0,
          "Auswertungsarchitektur: ergänzt die Musterarchitektur MASC um eine "
          "Bodenauswertung und verweist auf drei Elemente der Musterarchitektur.")

    a.pkg(2, "Operationelle Architektur", 1, "Wer nutzt die Weltraumlage?")
    a.pkg(3, "Servicearchitektur", 1, "Welche Dienste werden bereitgestellt bzw. genutzt?")
    a.pkg(4, "Systemarchitektur", 1, "Womit wird ausgewertet?")

    # --- eigene Elemente -----------------------------------------------------
    performer = a.el("Weltraumlagezentrum Boden", "OperationalPerformer", 2,
                     g("qc-performer"),
                     "Bodeneinrichtung, die Weltraumlage und Aufklärungsdaten auswertet "
                     "und in die Führung einbringt.")
    activity = a.el("Weltraumlage bewerten", "OperationalActivity", 2,
                    g("qc-activity"),
                    "Operationelle Aktivität: Aufklärungs- und Statusdaten zu einer "
                    "belastbaren Weltraumlage verdichten.")
    service = a.el("Weltraumlage-Auswertedienst", "ServiceSpecification", 3,
                   g("qc-service"),
                   "Stellt die bewertete Weltraumlage als Dienst bereit.")
    system = a.el("Auswertesystem Boden", "System", 4,
                  g("qc-system"),
                  "System, auf dem der Auswertedienst betrieben wird.")
    info_lage = a.el("Weltraumlagebericht", "InformationElement", 3,
                     g("qc-info-lage"),
                     "Informationsobjekt: bewertete Weltraumlage als Bericht an die Führung.")
    info_status = a.el("Statusmeldung Raumschiff", "InformationElement", 3,
                       g("qc-info-status"),
                       "Informationsobjekt: Statusmeldungen des Raumschiffs, die in die "
                       "Lagebewertung eingehen.")

    # --- Referenzen auf die Musterarchitektur MASC --------------------------
    ref_weltraumstart = a.el("Weltraumstart durchführen", "OperationalActivity", 2,
                             G_MASC_WELTRAUMSTART,
                             "Referenz auf die operationelle Aktivität „Weltraumstart "
                             "durchführen“ aus der Musterarchitektur MASC (identische ea_guid).")
    ref_sci = a.el("Spacecraft Information Service Bw", "ServiceSpecification", 3,
                   G_MASC_SPACECRAFT_SVC,
                   "Referenz auf den Spacecraft Information Service Bw aus der "
                   "Musterarchitektur MASC (identische ea_guid).")
    ref_gis = a.el("GIS Service Bw", "ServiceSpecification", 3,
                   G_MASC_GIS_SVC,
                   "Referenz auf den GIS Service Bw aus der Musterarchitektur MASC "
                   "(identische ea_guid).")

    # --- Beziehungen innerhalb der Erweiterung ------------------------------
    a.con_("ActivitySupportsService", activity, service, "unterstützt")
    a.con_("ActivityPerformedByPerformer", activity, performer, "wird ausgeführt von")
    a.con_("ServiceExchange", service, info_lage, "liefert")
    a.con_("ServiceExchange", ref_sci, info_status, "liefert")
    # Der eigene Dienst konsumiert den MASC-Service (Brücke 1)
    a.con_("ServiceDependency", service, ref_sci, "nutzt")
    # Die eigene Aktivität nutzt den MASC-Service (Brücke 2)
    a.con_("ServiceDependency", activity, ref_gis, "nutzt")
    # Die eigene Aktivität steht in Bezug zum MASC-Weltraumstart (Brücke 3)
    a.con_("ActivityDependency", activity, ref_weltraumstart, "folgt auf")
    # Systembezug
    a.con_("ServiceDeployment", system, service, "betreibt")
    a.con_("ServiceExchange", ref_gis, info_status, "liefert")

    a.con.execute("INSERT INTO t_diagram (Diagram_ID, Name, Type, Package_ID, ea_guid)"
                  " VALUES (1, 'QC Übersicht', 'Logical', 1, ?)", (g("qc-diag"),))
    a.con.commit()
    a.con.close()
    return OUT / "QC_Weltraumlage-Erweiterung.qea"


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    p = build()
    print(f"{p.name}: {p.stat().st_size:,} Bytes")
    print("\nBrücken zu MASC (echte GUIDs, unverändert):")
    print("  Spacecraft Information Service Bw ", G_MASC_SPACECRAFT_SVC)
    print("  GIS Service Bw                    ", G_MASC_GIS_SVC)
    print("  Weltraumstart durchführen         ", G_MASC_WELTRAUMSTART)
