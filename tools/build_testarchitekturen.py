#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Erzeugt zwei Testarchitekturen (.qea / SQLite) für die EAM-Suite.

Ziel: Die Verbindung ZWISCHEN zwei Architekturen zeigen.
  QA_Taktische-Lagebild-Architektur.qea   ->  liefert  "Lagebilddaten (NATO-Standard)"
  QB_Nationale-Lagebild-Architektur.qea   ->  nutzt     "Lagebilddaten (NATO-Standard)"

Der Betriebsdienst wird in Architektur A als ServiceSpecification geführt und
in Architektur B als Realisation einer Servicefunktion verwendet. Beide Objekte
tragen dieselbe ea_guid (Klammer-GUID-Konvention), damit die Analyse die
Brücke über die Architekturgrenze erkennt.

Aufruf:  python3 tools/build_testarchitekturen.py
"""
import sqlite3
import uuid
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "testdaten"
NS = uuid.UUID("6f1c2a90-0000-4000-8000-000000000000")


def guid(tag: str) -> str:
    """Stabile, lesbare Klammer-GUID je Rolle (gleiche Rolle = gleiche GUID)."""
    return "{" + str(uuid.uuid5(NS, tag)).upper() + "}"


# ------------------------------------------------------------------Konstanten
# Gemeinsame Brücken-Elemente (in BEIDEN Dateien mit identischer GUID)
G_LOESUNG_LAGEBILD = guid("loesung-lagebild")
G_STANDARD_NATO = guid("standard-nato-exchange")

# Architektur A
G_A_PKG_ROOT = guid("A-pkg-root")
G_A_PKG_OPS = guid("A-pkg-ops")
G_A_PKG_SVC = guid("A-pkg-svc")
G_A_PKG_INFO = guid("A-pkg-info")
G_A_NODE = guid("A-node-ops")
G_A_FUNC_ERFASSEN = guid("A-func-erfassen")
G_A_SVC_BETRIEB = guid("A-svc-betrieb")
G_A_SVC_AUSKUNFT = guid("A-svc-auskunft")
G_A_INFO = guid("A-info-lagebild")
G_A_C_EXCHANGE = guid("A-c-exchange")
G_A_C_ACTIVITY = guid("A-c-activity")

# Architektur B
G_B_PKG_ROOT = guid("B-pkg-root")
G_B_PKG_SYS = guid("B-pkg-sys")
G_B_PKG_SVC = guid("B-pkg-svc")
G_B_NODE = guid("B-node-toolbox")
G_B_FUNC_AUSWERTEN = guid("B-func-auswerten")
G_B_FUNC_DARSTELLEN = guid("B-func-darstellen")
G_B_SVC_BETRIEB = guid("B-svc-betrieb-verweis")
G_B_INFO = guid("B-info-lagebild")
G_B_C_EXCHANGE = guid("B-c-exchange")

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
CREATE TABLE t_objectconstraint (ConstraintID INTEGER PRIMARY KEY, Object_ID INTEGER,
    "Constraint" TEXT, "Type" TEXT, "Status" TEXT, "Notes" TEXT);
CREATE TABLE t_connectortag (PropertyID INTEGER PRIMARY KEY, ElementID INTEGER,
    "Property" TEXT, "Value" TEXT, "Notes" TEXT);
CREATE TABLE t_diagramobjects (Instance_ID INTEGER PRIMARY KEY, Diagram_ID INTEGER,
    Object_ID INTEGER, RectTop INTEGER, RectLeft INTEGER, RectRight INTEGER,
    RectBottom INTEGER, ObjectStyle TEXT);
CREATE TABLE t_diagramlinks (Instance_ID INTEGER PRIMARY KEY, DiagramID INTEGER,
    ConnectorID INTEGER, Geometry TEXT, Style TEXT);
"""


class Arch:
    def __init__(self, path: Path, name: str):
        if path.exists():
            path.unlink()
        self.path = path
        self.name = name
        self.con = sqlite3.connect(path)
        self.con.executescript(";\n".join(v.strip().rstrip(";") for v in SCHEMA.values()) + ";" + BODY_TAIL)
        self.obj_id = 100
        self.con_id = 200
        self.xref_id = 500
        self.diag_id = 1

    # ---------------------------------------------------------------- Helfer
    def pkg(self, pid, name, parent, note=""):
        self.con.execute(
            "INSERT INTO t_package (Package_ID, Name, Parent_ID, Notes, ea_guid, TPos, PackageFlags)"
            " VALUES (?,?,?,?,?,?,?)", (pid, name, parent, note, guid(f"pkg-{self.name}-{pid}"), pid, "VICON=3;"))
        # EA-Konvention: Paket existiert zusätzlich als Element in t_object
        self.con.execute(
            "INSERT INTO t_object (Object_ID, Object_Type, Name, Package_ID, ea_guid, TPos)"
            " VALUES (?,?,?,?,?,?)", (pid, "Package", name, pid, guid(f"pkg-{self.name}-{pid}"), pid))

    def el(self, otype, name, stereotype, package_id, node_guid, note="", alias=""):
        self.obj_id += 1
        oid = self.obj_id
        self.con.execute(
            "INSERT INTO t_object (Object_ID, Object_Type, Name, Package_ID, Stereotype, Note, Alias, ea_guid, TPos)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            (oid, otype, name, package_id, stereotype, note, alias, node_guid, self.obj_id))
        if stereotype:
            self.con.execute(
                "INSERT INTO t_xref (XrefID, Type, Description, Client) VALUES (?,?,?,?)",
                (self._xid(), "element property",
                 f"@STEREO;Name={stereotype};FQName=NAFv4::{stereotype};@ENDSTEREO;", node_guid))
        return oid

    def con_(self, ctype, stereotype, src, dst, name="", g=None):
        self.con_id += 1
        cid = self.con_id
        self.con.execute(
            "INSERT INTO t_connector (Connector_ID, Name, Connector_Type, Stereotype,"
            " Start_Object_ID, End_Object_ID, ea_guid) VALUES (?,?,?,?,?,?,?)",
            (cid, name, ctype, stereotype, src, dst, g or guid(f"conn-{self.name}-{cid}")))
        if stereotype:
            self.con.execute(
                "INSERT INTO t_xref (XrefID, Type, Description, Client) VALUES (?,?,?,?)",
                (self._xid(), "connector property",
                 f"@STEREO;Name={stereotype};FQName=NAFv4::{stereotype};@ENDSTEREO;",
                 g or guid(f"conn-{self.name}-{cid}")))
        return cid

    def _xid(self):
        self.xref_id += 1
        return self.xref_id

    def close(self):
        self.con.commit()
        self.con.close()


# ============================================================== ARCHITEKTUR A
def build_a():
    a = Arch(OUT / "QA_Taktische-Lagebildarchitektur.qea", "QA")
    a.pkg(1, "QA Taktische Lagebildarchitektur", 0,
          "Testarchitektur A – liefert die Lagebilddaten für die nationale Darstellung.")
    a.pkg(2, "Operationelle Architektur", 1, "Wer erzeugt die Lagebilddaten?")
    a.pkg(3, "Servicearchitektur", 1, "Welcher Dienst stellt die Daten bereit?")
    a.pkg(4, "Informationsmodell", 1, "Welche Daten fließen?")

    node = a.el("Class", "Taktisches Führungssystem A", "OperationalPerformer", 2, G_A_NODE,
                "System, das die taktische Lage erfasst.")
    func = a.el("Class", "Lage erfassen", "OperationalActivity", 2, G_A_FUNC_ERFASSEN,
                "Operationelle Aktivität: Sensorsichtungen und Meldungen zusammenführen.")
    svc = a.el("Class", "Betriebsdienst Lagebild", "ServiceSpecification", 3, G_A_SVC_BETRIEB,
               "Liefert Lagebilddaten im NATO-Austauschformat.", "Lagebilddienst")
    svc2 = a.el("Class", "Auskunftsdienst Verbindungsdaten", "ServiceSpecification", 3, G_A_SVC_AUSKUNFT,
                "Zweiter Dienst derselben Architektur (Vergleich im Tool).")
    info = a.el("Class", "Lagebilddaten (NATO-Standard)", "InformationElement", 4, G_A_INFO,
                "Informationsobjekt: standardisierter Lagebilddatensatz, Brücke zu Architektur B.")
    a.el("Class", "Auskunftsdaten Verbindungslage", "InformationElement", 4,
         guid("A-info-verbindung"), "Zweites Informationsobjekt.")

    a.con_("Realisation", "ActivitySupportsService", func, svc, "unterstützt")
    a.con_("Realisation", "ServiceExchange", svc, info, "liefert", G_A_C_EXCHANGE)
    a.con_("Dependency", None, node, func, "fährt aus")
    a.con_("Dependency", None, svc2, info, "nutzt")

    a.con.execute("INSERT INTO t_diagram (Diagram_ID, Name, Type, Package_ID, ea_guid)"
                  " VALUES (1, 'QA Übersicht', 'Logical', 1, ?)", (guid("A-diag-1"),))
    a.close()
    return a.path


# ============================================================== ARCHITEKTUR B
def build_b():
    b = Arch(OUT / "QB_Nationale-Lagebildarchitektur.qea", "QB")
    b.pkg(1, "QB Nationale Lagebildarchitektur", 0,
          "Testarchitektur B – nutzt die Lagebilddaten aus Architektur A.")
    b.pkg(2, "Systemarchitektur", 1, "Womit werden die Daten ausgewertet?")
    b.pkg(3, "Servicearchitektur", 1, "Welcher Dienst nutzt die Daten?")

    node = b.el("Class", "Lagebild-Toolbox national", "ResourcePerformer", 2, G_B_NODE,
                "System zur Auswertung und Darstellung der nationalen Lage.")
    f1 = b.el("Class", "Lagebild auswerten", "ResourceActivity", 2, G_B_FUNC_AUSWERTEN,
              "Ressourcenaktivität: Meldungen zu einem Lagebild verdichten.")
    f2 = b.el("Class", "Lagebild darstellen", "ResourceActivity", 2, G_B_FUNC_DARSTELLEN,
              "Ressourcenaktivität: Lagebild auf der Karte ausgeben.")

    # Verweis auf das Element aus Architektur A – gleiche GUID wie in Datei A
    svc = b.el("Class", "Betriebsdienst Lagebild", "ServiceSpecification", 3, G_A_SVC_BETRIEB,
               "Referenz auf den Betriebsdienst aus Architektur A (gleiche GUID).")
    info = b.el("Class", "Lagebilddaten (NATO-Standard)", "InformationElement", 3, G_A_INFO,
                "Referenz auf das Informationsobjekt aus Architektur A (gleiche GUID).")

    b.con_("Realisation", "ActivitySupportsService", f1, svc, "nutzt")
    b.con_("Realisation", "ServiceExchange", svc, info, "verarbeitet", G_B_C_EXCHANGE)
    b.con_("Dependency", None, node, f1, "fährt aus")
    b.con_("Dependency", None, f2, node, "läuft auf")
    b.con_("Dependency", None, f1, f2, "geht über in")

    b.con.execute("INSERT INTO t_diagram (Diagram_ID, Name, Type, Package_ID, ea_guid)"
                  " VALUES (1, 'QB Übersicht', 'Logical', 1, ?)", (guid("B-diag-1"),))
    b.close()
    return b.path


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    pa = build_a()
    pb = build_b()
    for p in (pa, pb):
        size = p.stat().st_size
        print(f"{p.name:45s} {size:>8,d} Bytes")
    print(f"\nBrücken-GUID (identisch in beiden Dateien): {G_LOESUNG_LAGEBILD}")
