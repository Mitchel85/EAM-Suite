/* Kombinierter E2E-Test v7:
   A) Einzelmodus-Regression (MASC): Aufbau, Sichten, Rendering-Smoke
   B) Mehrfach-Modus: MASC (M1) + Test.qea (M2) verschmelzen
   C) Edit + Save: je eine Änderung in M1 und M2, getrennt speichern, beide Ausgaben prüfen
   Ergebnis: document.body[data-v7] */
(function () {
  var R = { A: [], B: [], C: [], errors: [] };
  function st(list, n, ok, info) { list.push({ n: n, ok: !!ok, info: String(info == null ? '' : info).substring(0, 240) }); }
  function fin() { document.body.setAttribute('data-v7', JSON.stringify(R)); }
  window.addEventListener('unhandledrejection', function (e) { R.errors.push('rej: ' + (e.reason && e.reason.message ? e.reason.message : e.reason)); });

  function loadFile(url, name) {
    return fetch(url + '?ts=' + Date.now()).then(function (r) { return r.arrayBuffer(); }).then(function (ab) {
      loadQea(ab, name);
      return ab.byteLength;
    });
  }

  /* ---------- A) Einzelmodus ---------- */
  var k, i, j;
  loadFile('/Musterarchitektur_MASC.qea', 'Musterarchitektur_MASC.qea').then(function (b1) {
    st(R.A, 'Load MASC', b1 > 1000000, b1 + 'B');
    st(R.A, 'Kennzahlen 225/265/1652/1746', Object.keys(PKG).length === 225 && DIAGS.length === 265 && Object.keys(OBJS).length === 1652 && CONS.length === 1746,
      Object.keys(PKG).length + '/' + DIAGS.length + '/' + Object.keys(OBJS).length + '/' + CONS.length);
    var rawKeys = true, prefixed = 0;
    for (k in OBJS) { if (!OBJS.hasOwnProperty(k)) continue; if (/^m\d+_o/.test(k)) rawKeys = false; if (OBJS[k].name && OBJS[k].name.indexOf('<<M') === 0) prefixed++; }
    st(R.A, 'Einzelmodus: keine Modell-Kennungen/Präfixe', rawKeys && prefixed === 0, 'rawOK=' + rawKeys + ' präfixe=' + prefixed);
    var dOk = 0, dBad = 0;
    for (i = 0; i < DIAGS.length; i++) {
      var dob = DIAGOBJ[DIAGS[i].id] || [], ok = 0;
      for (j = 0; j < dob.length; j++) { if (OBJS[String(dob[j].oid)]) ok++; }
      if (dob.length === 0 || ok === dob.length) dOk++; else dBad++;
    }
    st(R.A, 'Sichten vollständig aufgelöst', dBad === 0, dOk + '/' + DIAGS.length);
    var dl = 0, dlok = 0;
    for (k in DIAGLINK) { if (!DIAGLINK.hasOwnProperty(k)) continue; for (i = 0; i < DIAGLINK[k].length; i++) { dl++; if (CONNMAP[String(DIAGLINK[k][i].cid)]) dlok++; } }
    st(R.A, 'Diagramm-Links (CONNMAP)', dl > 0 && dlok === dl, dlok + '/' + dl);
    try { renderPkgTree(); computeStats(); renderDiagsCatalog(); openPackage(PKG_ROOTS[0].id, true); st(R.A, 'Rendering-Smoke (Explorer/Sichten/Stats)', true, ''); }
    catch (e) { st(R.A, 'Rendering-Smoke', false, e.message); }

    /* ---------- B) Mehrfach-Modus ---------- */
    toggleMultiMode(true);
    SINGLE = false;
    st(R.B, 'M1 registriert', MODEL_N === 1 && MODEL_FILES.length === 1 && MODEL_FILES[0].obj > 1600, 'N=' + MODEL_N + ' obj=' + (MODEL_FILES[0] || {}).obj);
    return loadFile('/Test.qea', 'Test.qea');
  }).then(function (b2) {
    st(R.B, 'Load Testarchitektur (M2)', b2 > 100000, b2 + 'B');
    st(R.B, 'Kennzahlen 374/342/2167', Object.keys(PKG).length === 374 && DIAGS.length === 342 && CONS.length === 2167,
      Object.keys(PKG).length + '/' + DIAGS.length + '/' + CONS.length);
    var m2 = 0, shared = 0;
    for (k in OBJS) { if (!OBJS.hasOwnProperty(k)) continue; if (/^m2_o\d+$/.test(k)) m2++; if (OBJS[k].models && OBJS[k].models.length > 1) shared++; }
    st(R.B, 'M2-Elemente + Fusionen', m2 === 279 && shared >= 200, 'm2=' + m2 + ' geteilt=' + shared);
    st(R.B, 'Fusionszähler (MODEL_FILES)', MODEL_FILES[1].merged === 288, 'merged=' + MODEL_FILES[1].merged);
    var dOk2 = 0, dBad2 = 0;
    for (i = 0; i < DIAGS.length; i++) {
      var dob2 = DIAGOBJ[DIAGS[i].id] || [], ok2 = 0;
      for (j = 0; j < dob2.length; j++) { if (OBJS[String(dob2[j].oid)]) ok2++; }
      if (dob2.length === 0 || ok2 === dob2.length) dOk2++; else dBad2++;
    }
    st(R.B, 'Alle Sichten aufgelöst (inkl. leer)', dBad2 === 0, dOk2 + '/' + DIAGS.length);
    var conBad = 0, cross = 0;
    for (i = 0; i < CONS.length; i++) {
      if (!OBJS[String(CONS[i].a)] || !OBJS[String(CONS[i].b)]) conBad++;
      var pa = parseG(CONS[i].a), pb = parseG(CONS[i].b);
      if (pa && pb && pa.n !== pb.n) cross++;
    }
    st(R.B, 'Beziehungen: Endpunkte + keine Quervernetzung', conBad === 0 && cross === 0, 'kaputt=' + conBad + ' quer=' + cross);

    /* ---------- C) Edit + Save (je Datei eine Änderung) ---------- */
    var m1id = null;
    for (k in OBJS) { if (!OBJS.hasOwnProperty(k)) continue; if (!/^m2_/.test(k) && OBJS[k].type === 'Class' && OBJS[k].name) { m1id = k; break; } }
    st(R.C, 'M1-Testelement gefunden', !!m1id, m1id + ' = ' + (OBJS[m1id] || {}).name);
    window.__v7files = [];
    window.__editSink = function (out, fname) { window.__v7files.push({ fname: fname, bytes: out }); };

    var tests = [];
    if (m1id) tests.push({ id: m1id, neu: 'V7-M1-TESTALIAS' });
    /* ein nicht fusioniertes M2-Element */
    var m2id = null;
    for (k in OBJS) { if (OBJS.hasOwnProperty(k) && /^m2_o\d+$/.test(k)) { m2id = k; break; } }
    st(R.C, 'M2-Testelement gefunden', !!m2id, m2id + ' = ' + (OBJS[m2id] || {}).name);
    if (m2id) tests.push({ id: m2id, neu: 'V7-M2-TESTALIAS' });

    tests.forEach(function (t) {
      EDIT.elEdit(t.id);
      var inp = el('ee-name');
      if (inp) { inp.value = t.neu; }
      EDIT.formOk();
    });
    var cnt = EDIT._internal.count();
    var pend = EDIT._internal.list();
    st(R.C, 'Vormerkungen mit korrekter Quelldatei', cnt >= 2 && pend[0].srcNo === 1 && pend[1].srcNo === 2,
      'count=' + cnt + ' srcNos=' + pend.map(function (c) { return c.srcNo; }).join(','));

    try { EDIT.save(); st(R.C, 'Speichern gestartet', true, ''); }
    catch (e) { st(R.C, 'Speichern gestartet', false, e.message); }

    /* Warten und Ausgaben prüfen */
    setTimeout(function () {
      var files = window.__v7files || [];
      st(R.C, 'Zwei Ausgabedateien erzeugt', files.length === 2, files.map(function (f) { return f.fname + '(' + f.bytes.length + 'B)'; }).join(' | '));
      var check = { m1: false, m2: false, m1ok: false, m2ok: false };
      for (i = 0; i < files.length; i++) {
        try {
          var db2 = qeaOpen(files[i].bytes.slice().buffer);
          var rows = db2.rows('t_object'), hit = false, rr;
          for (j = 0; j < rows.length; j++) { rr = qcol(rows[j], 'Name'); if (String(rr) === 'V7-M1-TESTALIAS') check.m1 = true; if (String(rr) === 'V7-M2-TESTALIAS') check.m2 = true; }
          if (files[i].fname.indexOf('Musterarchitektur') >= 0) check.m1ok = check.m1;
          if (files[i].fname.indexOf('Test') >= 0) check.m2ok = check.m2;
        } catch (e9) { R.errors.push('qeaOpen(' + files[i].fname + '): ' + e9.message); }
      }
      st(R.C, 'M1-Datei enthält M1-Änderung', check.m1, 'gefunden=' + check.m1);
      st(R.C, 'M2-Datei enthält M2-Änderung', check.m2, 'gefunden=' + check.m2);
      fin();
    }, 75000);
  }).catch(function (e) {
    R.errors.push('fatal: ' + (e && e.message ? e.message : e));
    fin();
  });
})();
