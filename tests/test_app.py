"""End-to-End-Tests für Architektur Mate.

Playwright steuert einen echten Chromium-Browser (headless) und testet die
gebaute Einzeldatei dist/Architektur_Mate.html gegen die mitgelieferten
Testarchitekturen in tests/fixtures/.

Lokal ausführen:
    python3 src/build_release.py
    pip install -r requirements-dev.txt
    python -m playwright install chromium
    pytest tests/test_app.py -v

Die Tests laufen automatisch bei jedem Push (siehe .github/workflows/ci.yml).
"""
import pathlib
import re

import pytest
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "Architektur_Mate.html"
FIX = ROOT / "tests" / "fixtures"
MASC = FIX / "Musterarchitektur_MASC.qea"
ZWEIT = FIX / "Zweitarchitektur.qea"
URL = DIST.as_uri()

# Bekannte Kennzahlen der Musterarchitektur (MASC)
PKG_COUNT = "226 Pakete"
DIAG_COUNT = "265 Sichten"
EL_COUNT = "1.655 Elemente"
ROOT_EL_COUNT = "1.646 Elemente"  # Paket-Root inkl. Unterpakete


def _load(page, files):
    page.locator("#file").set_input_files([str(f) for f in files])


def _loaded(page, timeout=45000):
    page.wait_for_function(
        "() => typeof PKG !== 'undefined' && Object.keys(PKG).length > 0",
        timeout=timeout,
    )


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture()
def page(browser):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(URL)
    pg.wait_for_timeout(600)
    yield pg
    assert errors == [], f"JS-Fehler aufgetreten: {errors}"
    ctx.close()


# Bei Fehlschlag automatisch Screenshot ablegen (für CI-Artefakt)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        pg = item.funcargs.get("page")
        if pg is not None:
            d = ROOT / "tests" / "_screenshots"
            d.mkdir(exist_ok=True)
            try:
                pg.screenshot(path=str(d / f"{item.name}.png"))
            except Exception:
                pass


def test_startbereich_aufgeraeumt(page):
    """Startbereich: Upload sichtbar, 2 klare Buttons, Kriterien eingeklappt."""
    assert page.locator("#upload").is_visible()
    btns = page.locator(".upbtn")
    assert btns.count() == 2
    texts = [btns.nth(i).inner_text() for i in range(2)]
    assert "Eine Architektur laden" in texts[0]
    assert "verschmelzen" in texts[1]
    details = page.locator(".semwrap-details")
    assert details.count() == 1
    assert details.get_attribute("open") is None  # standardmäßig zu
    assert "v8" in page.locator(".badge-v").inner_text()


def test_laden_einzelmodell(page):
    """MASC lädt, Modellleiste zeigt korrekte Gesamtzahlen, Baum rendert."""
    _load(page, [MASC])
    _loaded(page)
    bar = page.locator("#modellbar").inner_text()
    assert PKG_COUNT in bar
    assert DIAG_COUNT in bar
    assert EL_COUNT in bar
    # MASC enthält zwei Root-Pakete: MASC + TestArchitektur_Verbindungstest
    names = page.evaluate("PKG_ROOTS.map(r => r.name).join('|')")
    assert "MASC" in names and "TestArchitektur_Verbindungstest" in names
    assert page.evaluate("PKG_ROOTS.length") == 2
    assert "MASC" in page.locator("#pkgtree").inner_text()


def test_suche_mit_treffer(page):
    """Sofort-Suche: Treffer-Überschrift mit formatierten Zahlen."""
    _load(page, [MASC])
    _loaded(page)
    page.fill("#globalsearch", "Projekt")
    page.wait_for_selector("#gsres", state="visible", timeout=15000)
    hdr = page.locator(".gs-hdr").inner_text()
    assert "Treffer für" in hdr
    assert re.search(r"[\d.]+ (Sicht|Sichten)", hdr)
    assert "0 Sichten · 0 Pakete · 0 Elemente" not in hdr


def test_paketansicht_formatierte_kennzahlen(page):
    """Paket-Ansicht: Tausenderpunkte, Singular/Plural, 'Unterpakete'."""
    _load(page, [MASC])
    _loaded(page)
    kpis = page.locator(".kpis").inner_text()
    assert ROOT_EL_COUNT in kpis  # 1.646 statt 1646 (Format-Regression)
    assert "Unterpakete" in kpis
    assert "Unterpakete (" in page.locator(".exp-main").inner_text()


def test_edit_aenderung_vormerken(page):
    """Edit: Modal öffnen, Namen ändern, vormerken → Änderungsliste (1)."""
    _load(page, [MASC])
    _loaded(page)
    oid = page.evaluate(
        "() => Object.keys(OBJS).find(k => OBJS[k].st && !/^proxyconnector$/i.test(OBJS[k].st))"
    )
    page.evaluate("oid => EDIT.elEdit(oid)", oid)
    name = page.locator("#ee-name")
    name.wait_for(state="visible", timeout=10000)
    name.fill(name.input_value() + " (Test)")
    page.locator("#editmodal button", has_text="vormerken").first.click()
    page.evaluate("() => EDIT.openPanel()")
    drawer = page.locator("#editdrawer")
    drawer.wait_for(state="visible", timeout=10000)
    head = page.locator(".edr-head").inner_text()
    assert "(1)" in head
    assert "→" in drawer.inner_text()


def test_mehrfachmodus_keine_doppelten_roots(page):
    """Regression: 2 Architekturen → keine doppelten Root-Pakete im Baum."""
    _load(page, [MASC, ZWEIT])
    page.wait_for_function(
        "() => typeof MODEL_FILES !== 'undefined' && MODEL_FILES.length === 2",
        timeout=45000,
    )
    _loaded(page)
    page.wait_for_function("() => MULTI_MODE === true", timeout=15000)
    roots = page.evaluate("PKG_ROOTS.map(r => r.id)")
    assert len(roots) >= 2
    assert len(set(roots)) == len(roots), f"Doppelte Roots: {roots}"
    names = page.evaluate("PKG_ROOTS.map(r => r.name).join('|')")
    assert "MASC" in names and "Zweitarchitektur" in names


def test_aufloesen_nimmt_fusion_zurueck(page):
    """Regression B1: „✕ Auflösen“ löst die Landkarte auf und zeigt das erste
    Modell wieder als Einzelmodell (statt nur eines Alert-Hinweises)."""
    _load(page, [MASC, ZWEIT])
    page.wait_for_function(
        "() => typeof MODEL_FILES !== 'undefined' && MODEL_FILES.length === 2",
        timeout=45000,
    )
    _loaded(page)
    page.wait_for_function("() => MULTI_MODE === true", timeout=15000)
    assert page.evaluate("() => Object.keys(OBJS).length") > 1655  # Landkarte enthält beide Modelle

    # Eine Vormerkung anlegen, damit auch der Bestätigungsdialog geprüft wird
    oid = page.evaluate(
        "() => Object.keys(OBJS).find(k => OBJS[k].st && !/^proxyconnector$/i.test(OBJS[k].st))"
    )
    page.evaluate("oid => EDIT.elEdit(oid)", oid)
    name = page.locator("#ee-name")
    name.wait_for(state="visible", timeout=10000)
    name.fill(name.input_value() + " (Auflösen-Test)")
    page.locator("#editmodal button", has_text="vormerken").first.click()
    assert page.evaluate("() => EDIT._internal.count()") == 1

    page.on("dialog", lambda d: d.accept())
    page.locator("#mergebar button", has_text="Auflösen").click()
    page.wait_for_function("() => MULTI_MODE === false", timeout=20000)
    page.wait_for_function(
        "() => typeof MODEL_FILES !== 'undefined' && MODEL_FILES.length === 0",
        timeout=20000,
    )

    # Nur noch MASC: 2 Wurzelpakete, Kennzahlen des Einzelmodells
    assert page.evaluate("() => PKG_ROOTS.length") == 2
    assert page.evaluate("() => Object.keys(OBJS).length") == 1655
    assert page.evaluate("() => CONS.length") == 1747
    bar = page.locator("#modellbar").inner_text()
    assert PKG_COUNT in bar
    assert DIAG_COUNT in bar
    assert EL_COUNT in bar
    # Landkarten-Leiste verschwunden, Umschalter zurückgesetzt, Vormerkungen verworfen
    assert page.evaluate(
        "() => getComputedStyle(document.getElementById('mergebar')).display"
    ) == "none"
    assert page.evaluate("() => SINGLE") is True
    assert page.evaluate("() => EDIT._internal.count()") == 0
    assert "Landkarte aufgelöst" in page.locator("#mttoast").inner_text()


def test_mobile_390_kein_horizontaler_overflow(browser):
    """Regression B2: Explorer und Referenz-Grid erzeugen bei 390 px Viewport
    keinen horizontalen Seiten-Scroll (Baum/Tabellen scrollen intern)."""
    ctx = browser.new_context(viewport={"width": 390, "height": 844})
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(URL)
    pg.wait_for_timeout(600)
    _load(pg, [MASC])
    pg.wait_for_function(
        "() => typeof PKG !== 'undefined' && Object.keys(PKG).length > 0",
        timeout=45000,
    )
    pg.wait_for_timeout(500)

    sw_explorer = pg.evaluate("() => document.documentElement.scrollWidth")
    assert sw_explorer <= 390, f"Explorer: horizontaler Overflow (scrollWidth={sw_explorer})"
    panel_box = pg.locator(".exp-tree-panel").bounding_box()
    assert panel_box is not None
    assert panel_box["x"] >= -0.5, f"Baum-Panel ragt links heraus: {panel_box}"
    assert panel_box["x"] + panel_box["width"] <= 390.5, f"Baum-Panel zu breit: {panel_box}"
    # Controls im Baumkopf sichtbar (＋ Alle / －)
    assert pg.locator(".tree-hdr button", has_text="Alle").is_visible()

    pg.evaluate("() => showView('grid')")
    pg.wait_for_timeout(500)
    sw_grid = pg.evaluate("() => document.documentElement.scrollWidth")
    assert sw_grid <= 390, f"Referenz-Grid: horizontaler Overflow (scrollWidth={sw_grid})"

    assert errors == [], f"JS-Fehler mobil: {errors}"
    ctx.close()


def test_dunkelmodus(browser):
    """Design: hell ist Standard (auch bei System-Dark), Dunkel nur per Button."""
    ctx = browser.new_context(
        viewport={"width": 1440, "height": 900}, color_scheme="dark"
    )
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(URL)
    pg.wait_for_timeout(800)

    # 1) Systemeinstellung 'dark' darf NICHT automatisch dunkel schalten
    body_bg = pg.evaluate("getComputedStyle(document.body).backgroundColor")
    assert body_bg == "rgb(241, 245, 249)", f"Standard muss hell sein: {body_bg}"
    assert pg.evaluate("document.documentElement.getAttribute('data-theme')") is None

    # 2) Button oben rechts schaltet dunkel
    btn = pg.locator("#themeBtn")
    assert btn.count() == 1, "Genau ein Design-Umschalter erwartet"
    assert btn.inner_text().strip() == "\U0001F319 Dunkles Design"
    btn.click()
    pg.wait_for_timeout(300)
    assert pg.evaluate("document.documentElement.getAttribute('data-theme')") == "dark"
    body_bg = pg.evaluate("getComputedStyle(document.body).backgroundColor")
    assert body_bg == "rgb(13, 22, 34)", f"Unerwarteter Hintergrund: {body_bg}"
    card_bg = pg.evaluate(
        "getComputedStyle(document.querySelector('.drop')).backgroundColor"
    )
    assert card_bg == "rgb(22, 34, 47)", f"Unerwartete Karte: {card_bg}"
    assert btn.inner_text().startswith("\u2600"), "Button muss zurück auf hell zeigen"

    # 3) Zurückschalten -> wieder hell
    btn.click()
    pg.wait_for_timeout(300)
    body_bg = pg.evaluate("getComputedStyle(document.body).backgroundColor")
    assert body_bg == "rgb(241, 245, 249)", f"Zurück auf hell erwartet: {body_bg}"
    assert errors == [], f"JS-Fehler im Designwechsel: {errors}"
    ctx.close()

def test_helle_flaechen(browser):
    """Helles Design: Dropzone, Suchfeld, Baumfilter und Sichten dürfen keine dunklen Flächen haben."""
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    pg = ctx.new_page()
    pg.goto(URL)
    pg.wait_for_timeout(600)

    def avg(selector):
        rgb = pg.evaluate(
            "sel => { const el = document.querySelector(sel); if (!el) return null;"
            " const c = getComputedStyle(el).backgroundColor.match(/[\\d.]+/g);"
            " return c ? c.slice(0, 3).map(Number) : null; }", selector)
        assert rgb is not None, f"Kein Hintergrund ermittelbar: {selector}"
        return sum(rgb) / 3

    assert avg(".drop") > 200, "Dropzone ist zu dunkel"
    assert avg("#globalsearch") > 200, "Suchfeld ist zu dunkel"
    assert avg("#treefilter") > 200, "Baumfilter ist zu dunkel"

    # Nicht-Chrome-Flächen im geladenen Modell prüfen (Button-/Header-Blau ist gewollt)
    pg.set_input_files("#file", str(ZWEIT))
    pg.wait_for_timeout(4000)
    pg.locator("button:has-text('Sicht öffnen')").first.click()
    pg.wait_for_timeout(2500)
    dunkel = pg.evaluate(
        "() => { const out = [];"
        "document.querySelectorAll('.svgwrap, .diagbox, .exp-tree-panel, .dcard, table.data, "
        ".tree-filter, .search-input-wrap input, .dtree, .dbar').forEach(el => {"
        " const c = getComputedStyle(el).backgroundColor.match(/[\\d.]+/g);"
        " if (c && c.length >= 3 && c.slice(0,3).map(Number).reduce((a,b)=>a+b,0)/3 < 110) "
        " out.push((el.className||el.tagName) + ': ' + getComputedStyle(el).backgroundColor); });"
        "return out; }")
    assert dunkel == [], f"Dunkle Flächen im hellen Design: {dunkel}"
    ctx.close()

def test_erweitert_oeffnet_keinen_explorer(browser):
    """"Erweitert"-Bereich und Kriterien dürfen den Startbildschirm nicht verlassen."""
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(URL)
    pg.wait_for_timeout(600)

    def zustand():
        return pg.evaluate(
            "() => ({exp: !!document.querySelector('.exp-tree-panel')?.offsetParent,"
            " ws: !!document.getElementById('workspace')?.offsetParent,"
            " up: !!document.getElementById('upload')?.offsetParent})")

    pg.locator(".semwrap-details summary").click()
    pg.wait_for_timeout(300)
    assert zustand() == {"exp": False, "ws": False, "up": True}, "Erweitert öffnet die Arbeitsansicht"

    # Kriterien bleiben nach dem Öffnen bedienbar (nicht ausgegraut)
    assert pg.locator("#semmatch-guid").is_enabled()
    assert pg.locator("#semmatch-name").is_enabled()
    assert pg.locator("#semmatch-alias").is_enabled()

    pg.locator("#semmatch-guid").click()
    pg.wait_for_timeout(300)
    assert zustand()["exp"] is False, "Kriterienwechsel öffnet den Explorer"
    assert pg.locator("#semmatch-guid").is_enabled(), "GUID-Kästchen wurde gesperrt"

    pg.locator("#semmatch-guid").click()
    pg.wait_for_timeout(200)
    assert pg.locator("#semmatch-guid").is_checked()
    assert errors == [], f"JS-Fehler: {errors}"
    ctx.close()
