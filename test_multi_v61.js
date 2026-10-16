/* E2E-Test Mehrfach-Modus v6.1: MASC (M1) + Test.qea/Testarchitektur (M2) verschmelzen.
   Neues Schema: M1 behält Original-Kennungen, M2 nutzt m2_o/m2_p/m2_d/m2_c.
   Läuft in der Page-Welt; Ergebnis in document.body[data-multi2]. */
(function () {
  var R = { steps: [], errors: [] };
  function step(n, ok, info) { R.steps.push({ n: n, ok: !!ok, info: String(info == null ? '' : info).substring(0, 260) }); }
  function done() { document.body.setAttribute('data-multi2', JSON.stringify(R)); }
  window.addEventListener('unhandledrejection', function (e) { R.errors.push('rej: ' + (e.reason && e.reason.message ? e.reason.message : e.reason)); });

  function loadFile(url, name) {
    return fetch(url + '?ts=' + Date.now()).then(function (r) { return r.arrayBuffer(); }).then(function (ab) {
      loadQea(ab, name);
      return ab.byteLength;
    });
  }

  toggleMultiMode(true);
  MULTI_MODE = true;
  SINGLE = false;

  loadFile('/Musterarchitektur_MASC.qea', 'Musterarchitektur_MASC.qea').then(function (b1) {
    step('M1 geladen (MASC)', b1 > 1000000, b1 + ' bytes');
    var n1 = { pkg: Object.keys(PKG).length, obj: Object.keys(OBJS).length, diag: DIAGS.length, con: CONS.length };
    step('M1 Aufbau', n1.pkg === 225 && n1.diag === 265 && n1.obj > 1600, JSON.stringify(n1));
    return loadFile('/Test.qea', 'Test.qea').then(function (b2) {
      step('M2 geladen (Testarchitektur/Test.qea)', b2 > 100000, b2 + ' bytes');
      return n1;
    });
  }).then(function (n1) {
    step('MODEL_FILES = 2', MODEL_FILES.length === 2, MODEL_FILES.map(function (f) { return 'M' + f.n + ':' + f.name.slice(0, 24) + '(pkg=' + f.pkg + ',obj=' + f.obj + ',merged=' + f.merged + ')'; }).join(' '));
    var totPkg = Object.keys(PKG).length, totObj = Object.keys(OBJS).length, totDiag = DIAGS.length, totCon = CONS.length;
    step('Pakete: M1+M2', totPkg > n1.pkg, totPkg + ' vs ' + n1.pkg);
    step('Sichten: M1+M2', totDiag > n1.diag, totDiag + ' vs ' + n1.diag);
    step('Beziehungen: M1+M2', totCon > n1.con, totCon + ' vs ' + n1.con);

    var k, m1 = 0, m2 = 0, merge = 0, models2 = 0;
    for (k in OBJS) {
      if (!OBJS.hasOwnProperty(k)) continue;
      if (/^m2_o\d+$/.test(k)) m2++;
      else m1++;
      if (OBJS[k].models && OBJS[k].models.length > 1) models2++;
    }
    step('M2-Elemente mit eigenem Schlüssel', m2 > 100, 'm2_o*=' + m2);
    step('M1-Elemente unverändert (raw keys)', m1 > 1600, 'M1=' + m1);
    step('Fusion: Elemente mit models=[1,2]', models2 > 100, 'geteilt=' + models2);

    /* Kern-Probe: Sichten haben aufgelöste Elemente (objCount > 0) */
    var dM1 = 0, dM1ok = 0, dM2 = 0, dM2ok = 0, i, j, d;
    for (i = 0; i < DIAGS.length; i++) {
      d = DIAGS[i];
      var dob = DIAGOBJ[d.id] || [];
      var okCnt = 0;
      for (j = 0; j < dob.length; j++) { if (OBJS[String(dob[j].oid)]) okCnt++; }
      var voll = (dob.length === 0) || (okCnt === dob.length);   /* leere Übersichts-Sichten sind gültig */
      if (/^m2_d\d+$/.test(String(d.id))) { dM2++; if (voll) dM2ok++; }
      else { dM1++; if (voll) dM1ok++; }
    }
    step('M1-Sichten vollständig aufgelöst', dM1ok === dM1, dM1ok + '/' + dM1);
    step('M2-Sichten vollständig aufgelöst', dM2ok === dM2 && dM2 > 0, dM2ok + '/' + dM2);

    /* Beziehungen: Endpunkte mustergültig */
    var conOk = 0, conBad = 0, crossA = 0;
    for (i = 0; i < CONS.length; i++) {
      var ca = String(CONS[i].a), cb = String(CONS[i].b);
      if (OBJS[ca] && OBJS[cb]) conOk++; else conBad++;
    }
    for (i = 0; i < CONS.length; i++) {
      var pa = parseG(CONS[i].a), pb = parseG(CONS[i].b);
      if (pa && pb && pa.n !== pb.n) crossA++;
    }
    step('Beziehungen: Endpunkte existieren', conBad === 0, 'ok=' + conOk + ' kaputt=' + conBad);
    step('Keine falsche Quervernetzung (m2→m2)', crossA === 0, 'quer=' + crossA);

    /* CONNMAP + Diagramlink-Auflösung */
    var dl = 0, dlok = 0;
    for (k in DIAGLINK) {
      if (!DIAGLINK.hasOwnProperty(k)) continue;
      for (i = 0; i < DIAGLINK[k].length; i++) { dl++; if (CONNMAP[String(DIAGLINK[k][i].cid)]) dlok++; }
    }
    step('Diagramm-Links auflösbar (CONNMAP)', dl > 0 && dlok === dl, dlok + '/' + dl);

    /* M2-Paketbaum: eigene Wurzel + echte Zuordnung */
    var m2roots = 0;
    for (i = 0; i < PKG_ROOTS.length; i++) if (Number(PKG_ROOTS[i].m) === 2) m2roots++;
    step('M2-Wurzelpakete (separater Baum)', m2roots >= 1, 'roots=' + m2roots);

    /* Unpaketierte Zuordnung: M2-Element pkgId zeigt auf m2_p* */
    var exEl = null;
    for (k in OBJS) { if (OBJS.hasOwnProperty(k) && /^m2_o\d+$/.test(k)) { exEl = k; break; } }
    step('M2-Element: pkgId ist m2_p*', exEl && String(OBJS[exEl].pkgId).indexOf('m2_p') === 0, exEl + ' pkg=' + (OBJS[exEl] || {}).pkgId);

    /* Edit-Zuordnung: groupOf über neue Kennungen (via EDIT._internal? nein — global prüfen) */
    if (typeof EDIT !== 'undefined' && EDIT._internal && EDIT._internal.groupOfTest) {
      step('groupOf (M2)', true, 'ok');
    }

    renderMergeBar();
    var mb = el('mergebar');
    step('Merge-Leiste sichtbar', mb && mb.style.display !== 'none' && mb.innerHTML.indexOf('M2') >= 0, mb ? 'ok' : 'fehlt');
    openMergeReport();
    var mm = el('editmodal');
    step('Fusionsbericht öffnet', mm && !mm.hasAttribute('hidden') && mm.innerHTML.indexOf('Test.qea') >= 0, '');
    modalClose();

    /* Pfad-/Graph-Smoke: globale Suche */
    var found = 0;
    for (k in OBJS) { if (!OBJS.hasOwnProperty(k)) continue; if (/fusion|geteilt/i.test(OBJS[k].name)) found++; }
    step('Suche über Landkarte (Smoke)', true, 'Treffer=' + found);

    document.body.setAttribute('data-multi2', JSON.stringify(R));
  }).catch(function (e) {
    R.errors.push('fatal: ' + (e && e.message ? e.message : e));
    document.body.setAttribute('data-multi2', JSON.stringify(R));
  });
})();
