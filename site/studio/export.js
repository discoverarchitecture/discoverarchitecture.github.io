/* Studio FGA: exports. PDF and JPG are high-resolution pictures of the edited sheets
   (made in the browser with html2canvas + jsPDF); the PowerPoint is built from the model with
   PptxGenJS, so every word stays an editable text box. */
(function () {
  'use strict';
  const LIBS = {
    html2canvas: 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js',
    jspdf: 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js',
    pptx: 'https://cdn.jsdelivr.net/npm/pptxgenjs@3.12.0/dist/pptxgen.bundle.js'
  };
  const loaded = {};
  function lib(name) {
    if (!loaded[name]) loaded[name] = new Promise((res, rej) => {
      const s = document.createElement('script');
      s.src = LIBS[name]; s.onload = res; s.onerror = () => rej(new Error('Could not load the ' + name + ' library. Check the internet connection.'));
      document.head.appendChild(s);
    });
    return loaded[name];
  }
  const F = () => window.FGA;
  const inch = (mm) => mm / 25.4;
  const hex = (c) => (c || '#1D1D1B').replace('#', '').toUpperCase();

  /* ---------- saving: the artifact's downloads capability, else a normal browser download */
  async function save(filename, blob) {
    let dl = null;
    try { dl = window.claude && window.claude.use ? await window.claude.use('downloads') : null; } catch (e) { dl = null; }
    if (dl) {
      try { await dl.save({ filename, data: blob }); return 'saved'; }
      catch (e) { if (e && e.code === 'declined') return 'declined'; if (e && e.code !== 'unavailable' && e.code !== 'not_granted') throw new Error(e.message || e.code); }
    }
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = filename;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
    return 'saved';
  }
  async function fileBlob(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error('Could not read ' + url);
    return r.blob();
  }
  function needsServer() {
    if (location.protocol === 'file:') throw new Error('Downloads need the hosted link or a local server: run  python3 -m http.server  in the prototype/app folder, then open http://localhost:8000');
  }

  /* ---------- pictures of sheets */
  async function settle(el) {
    await document.fonts.ready;
    await Promise.all([...el.querySelectorAll('img')].map((im) => im.complete && im.naturalWidth ? null : new Promise((r) => { im.onload = im.onerror = r; })));
  }
  async function shoot(P, page, scale) {
    await lib('html2canvas');
    const host = document.createElement('div');
    host.className = 'shoot-host';
    const sheet = document.createElement('div');
    F().renderInto(sheet, P, page);
    sheet.classList.add('export');
    host.appendChild(sheet);
    document.body.appendChild(host);
    try {
      await settle(sheet);
      return await window.html2canvas(sheet, { scale, backgroundColor: '#ffffff', useCORS: true, logging: false });
    } finally { host.remove(); }
  }
  async function boardPDF(P, onStep) {
    needsServer();
    onStep('Drawing the A1 board');
    const c = await shoot(P, P.board, 1.6);
    await lib('jspdf');
    const pdf = new window.jspdf.jsPDF({ unit: 'mm', format: [594, 841], orientation: 'portrait', compress: true });
    pdf.addImage(c.toDataURL('image/jpeg', 0.9), 'JPEG', 0, 0, 594, 841);
    return save(fileName(P, 'board-A1.pdf'), pdf.output('blob'));
  }
  async function boardJPG(P, onStep) {
    needsServer();
    onStep('Drawing the A1 board');
    const c = await shoot(P, P.board, 1.6);
    const blob = await new Promise((r) => c.toBlob(r, 'image/jpeg', 0.9));
    return save(fileName(P, 'board-A1.jpg'), blob);
  }
  async function deckPDF(P, onStep) {
    needsServer();
    await lib('jspdf');
    const vis = F().visibleSlides(P);
    const pdf = new window.jspdf.jsPDF({ unit: 'mm', format: [338.667, 190.5], orientation: 'landscape', compress: true });
    for (let i = 0; i < vis.length; i++) {
      onStep('Slide ' + (i + 1) + ' of ' + vis.length);
      const c = await shoot(P, vis[i], 2);
      if (i) pdf.addPage([338.667, 190.5], 'landscape');
      pdf.addImage(c.toDataURL('image/jpeg', 0.9), 'JPEG', 0, 0, 338.667, 190.5);
    }
    return save(fileName(P, 'jury-deck.pdf'), pdf.output('blob'));
  }

  /* ---------- PowerPoint */
  const imgCache = {};
  function loadImg(src) {
    if (!imgCache[src]) imgCache[src] = new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = () => rej(new Error('Could not read ' + src)); im.src = src; });
    return imgCache[src];
  }
  async function cropData(P, slot, c) {
    const im = await loadImg(F().srcOf(P, c.src)), g = F().geo(slot, c);
    const sx = (-g.left / g.dw) * im.naturalWidth, sy = (-g.top / g.dh) * im.naturalHeight;
    const sw = (slot.w / g.dw) * im.naturalWidth, sh = (slot.h / g.dh) * im.naturalHeight;
    const k = Math.min(1, 2600 / sw);
    const cv = document.createElement('canvas');
    cv.width = Math.round(sw * k); cv.height = Math.round(sh * k);
    cv.getContext('2d').drawImage(im, sx, sy, sw, sh, 0, 0, cv.width, cv.height);
    return cv.toDataURL('image/jpeg', 0.88);
  }
  async function plainData(src) {
    const im = await loadImg(src), cv = document.createElement('canvas');
    cv.width = im.naturalWidth; cv.height = im.naturalHeight;
    cv.getContext('2d').drawImage(im, 0, 0);
    return cv.toDataURL('image/png');
  }
  function textRuns(P, kind, paras) {
    const out = [];
    paras.forEach((p, pi) => {
      p.runs.forEach((r, ri) => {
        const s = F().runStyle(P.ts, kind, r);
        out.push({ text: s.upper ? r.t.toUpperCase() : r.t, options: {
          fontFace: s.family, fontSize: Math.round(s.size * 10) / 10, bold: s.weight >= 600, italic: s.italic, color: hex(s.color),
          charSpacing: s.track ? Math.round(s.track * s.size * 100) / 100 : undefined, align: p.align || 'left', lineSpacingMultiple: p.lh,
          paraSpaceAfter: p.after ? Math.round((p.after / 25.4) * 72 * 10) / 10 : undefined, breakLine: ri === p.runs.length - 1 && pi < paras.length - 1 } });
      });
    });
    return out;
  }
  function addText(P, kind, slide, b, paras, valign, nowrap) {
    const title = paras.some((p) => p.runs.some((r) => r.role === 'title'));
    slide.addText(textRuns(P, kind, paras), { x: inch(b.x), y: inch(b.y), w: inch(b.w), h: inch(b.h || 10), valign: valign || 'top', margin: 0, wrap: !nowrap, fit: title ? 'shrink' : 'none', isTextBox: true });
  }
  function addLine(pptx, slide, x1, y1, x2, y2, color, wpt) {
    slide.addShape(pptx.ShapeType.line, { x: inch(Math.min(x1, x2)), y: inch(Math.min(y1, y2)), w: inch(Math.max(0.01, Math.abs(x2 - x1))), h: inch(Math.max(0.0, Math.abs(y2 - y1))),
      flipH: (x2 < x1) !== (y2 < y1) && Math.abs(y2 - y1) > 0.01 && Math.abs(x2 - x1) > 0.01, line: { color: hex(color), width: wpt } });
  }
  async function deckPPTX(P, onStep) {
    needsServer();
    await lib('pptx');
    const pptx = new window.PptxGenJS();
    pptx.defineLayout({ name: 'FGA16x9', width: inch(338.667), height: inch(190.5) });
    pptx.layout = 'FGA16x9';
    pptx.title = P.name + ' jury deck';
    const vis = F().visibleSlides(P);
    for (let i = 0; i < vis.length; i++) {
      const page = vis[i];
      onStep('Slide ' + (i + 1) + ' of ' + vis.length);
      const s = pptx.addSlide();
      s.background = { color: 'FFFFFF' };
      for (const d of F().decoOf(P, page)) s.addImage({ data: await plainData(F().srcOf(P, d.src)), x: inch(d.x), y: inch(d.y), w: inch(d.w), h: inch(d.h) });
      for (const slot of page.slots) {
        const c = page.contents[slot.content];
        s.addImage({ data: await cropData(P, slot, c), x: inch(slot.x), y: inch(slot.y), w: inch(slot.w), h: inch(slot.h), altText: c.alt || '' });
      }
      for (const slot of page.slots) {
        const c = page.contents[slot.content], o = F().overlays(slot, c);
        o.labels.forEach((L) => {
          addLine(pptx, s, L.end[0], L.end[1], L.dot[0], L.dot[1], '#4A4A48', 0.5);
          s.addShape(pptx.ShapeType.ellipse, { x: inch(L.dot[0] - 0.65), y: inch(L.dot[1] - 0.65), w: inch(1.3), h: inch(1.3), fill: { color: '4A4A48' }, line: { color: 'FFFFFF', width: 0.5 } });
          addText(P, page.kind, s, L.box, [{ lh: 1, after: 0, align: L.box.align, runs: L.runs }], 'middle', true);
        });
        o.scales.forEach((S) => {
          S.rects.forEach((r) => s.addShape(pptx.ShapeType.rect, { x: inch(r.x), y: inch(r.y), w: inch(r.w), h: inch(r.h), fill: { color: hex(r.fill) }, line: { color: '4A4A48', width: 0.3 } }));
          S.texts.forEach((t) => addText(P, page.kind, s, t.box, [{ lh: 1, after: 0, align: t.box.align, runs: t.runs }], 'middle', true));
        });
        o.norths.forEach((N) => {
          s.addShape(pptx.ShapeType.triangle, { x: inch(N.x - 1.3), y: inch(N.y - 3), w: inch(2.6), h: inch(4.6), fill: { color: '4A4A48' }, line: { type: 'none' }, rotate: N.ang });
          const r = (N.ang * Math.PI) / 180;
          s.addText('N', { x: inch(N.x + 3.9 * Math.sin(r) - 2), y: inch(N.y - 3.9 * Math.cos(r) - 1.3), w: inch(4), h: inch(2.6), fontFace: F().runStyle(P.ts, 'slide', { role: 'small', fs: 6.5 }).family, bold: true, fontSize: 6.5, color: '4A4A48', align: 'center', valign: 'middle', margin: 0 });
        });
        const cap = F().capRuns(P, c);
        if (slot.cap && cap) addText(P, page.kind, s, slot.cap, cap, 'top', false);
      }
      F().derivedTexts(P, page).forEach((t) => { if (!t.hidden && t.paras) addText(P, page.kind, s, t, t.paras, t.valign, t.nowrap); });
    }
    onStep('Packing the PowerPoint file');
    const blob = await pptx.write({ outputType: 'blob' });
    return save(fileName(P, 'jury-deck.pptx'), blob);
  }
  function fileName(P, tail) { return (P.slug || 'studio-fga') + '-' + tail.replace(/^/, '') .replace('board-A1', 'board-A1-' + P.ts.toLowerCase()).replace('jury-deck', 'jury-deck-' + P.ts.toLowerCase()); }
  async function original(P, key, name) {
    needsServer();
    return save(name, await fileBlob(F().srcOf(P, P.files[key])));
  }
  window.FGAExport = { boardPDF, boardJPG, deckPDF, deckPPTX, original };
})();
