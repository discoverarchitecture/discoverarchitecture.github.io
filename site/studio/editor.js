/* Studio FGA: the board and deck renderer and editor.
   One model drives three things: the editor view, the thumbnails and the exports.
   Positions are millimetres on the sheet (A1 board 594 x 841, deck slide 338.667 x 190.5). */
(function () {
  'use strict';
  const MMPX = 96 / 25.4;               // CSS pixels per millimetre
  const PTMM = 25.4 / 72;               // millimetres per point

  /* ---------------------------------------------------------- text styles (templates/text-styles.json) */
  const FAM = {
    'Inter Tight': "'Inter Tight', Inter, Helvetica, Arial, sans-serif",
    'Inter': 'Inter, Helvetica, Arial, sans-serif',
    'Archivo Narrow': "'Archivo Narrow', 'Arial Narrow', Arial, sans-serif",
    'IBM Plex Sans': "'IBM Plex Sans', Helvetica, Arial, sans-serif",
    'IBM Plex Mono': "'IBM Plex Mono', Menlo, Consolas, monospace"
  };
  const TS = {
    A: { name: 'Swiss Bold', roles: {
      title: { f: 'Inter Tight', w: 800, tr: -0.035 }, lead: { f: 'Inter Tight', w: 500, tr: -0.01 }, leadStrong: { f: 'Inter Tight', w: 700, tr: -0.01 },
      kicker: { f: 'Inter', w: 600, tr: 0.16, up: true }, body: { f: 'Inter', w: 400 }, strong: { f: 'Inter', w: 600 },
      captionTitle: { f: 'Inter', w: 600 }, captionText: { f: 'Inter', w: 400, it: true }, label: { f: 'Inter', w: 500 }, small: { f: 'Inter', w: 500, tr: 0.04 } },
      k: { board: {}, slide: {} } },
    C: { name: 'Drawing Sheet', roles: {
      title: { f: 'Archivo Narrow', w: 700, tr: -0.005, up: true }, lead: { f: 'IBM Plex Sans', w: 500 }, leadStrong: { f: 'IBM Plex Sans', w: 600 },
      kicker: { f: 'IBM Plex Mono', w: 500, tr: 0.06, up: true }, body: { f: 'IBM Plex Sans', w: 400 }, strong: { f: 'IBM Plex Sans', w: 600 },
      captionTitle: { f: 'IBM Plex Mono', w: 500, tr: 0.04, up: true }, captionText: { f: 'IBM Plex Sans', w: 400, it: true },
      label: { f: 'IBM Plex Mono', w: 400, tr: 0.03, up: true }, small: { f: 'IBM Plex Mono', w: 400, up: true } },
      k: { board: { lead: 16 / 17, captionTitle: 7.5 / 8, label: 7.2 / 7.5, small: 7.2 / 7.5 },
           slide: { lead: 13.6 / 15, leadStrong: 13.6 / 15, body: 9.8 / 10, captionTitle: 7.5 / 8.4, label: 7.1 / 7.5, small: 7.1 / 7 } } }
  };
  function runStyle(ts, kind, r) {
    const s = TS[ts], ro = s.roles[r.role] || s.roles.body;
    const size = r.fs * ((s.k[kind] || {})[r.role] || 1);
    return { family: ro.f, css: FAM[ro.f], weight: ro.w, track: ro.tr || 0, upper: !!ro.up, italic: !!ro.it, size, color: r.c || '#1D1D1B' };
  }

  /* ---------------------------------------------------------- helpers */
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const clone = (o) => JSON.parse(JSON.stringify(o));
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  /* a picture's address: a fetched asset (the paid build's pictures, loaded with the job's key) or base + path */
  const srcOf = (P, s) => (window.FGA_ASSETS && window.FGA_ASSETS[s]) || (P.base || '') + s;

  /* where a content's image sits inside a slot */
  function geo(slot, c) {
    const a = c.iw / c.ih, s = slot.w / slot.h;
    let bw, bh;
    if (a > s) { bh = slot.h; bw = slot.h * a; } else { bw = slot.w; bh = slot.w / a; }
    const z = c.view.z, dw = bw * z, dh = bh * z;
    const left = clamp(slot.w / 2 - c.view.cx * dw, slot.w - dw, 0);
    const top = clamp(slot.h / 2 - c.view.cy * dh, slot.h - dh, 0);
    return { ix: slot.x + left, iy: slot.y + top, dw, dh, left, top };
  }
  /* map a point drawn for the content's home slot into the slot it sits in now */
  function mapper(slot, c) {
    const h = c.home;
    const same = Math.abs(h.x - slot.x) < 0.01 && Math.abs(h.y - slot.y) < 0.01 && Math.abs(h.w - slot.w) < 0.01 && Math.abs(h.h - slot.h) < 0.01;
    if (same) return (x, y) => [x, y];
    return (x, y) => {
      const nx = slot.x + (x - h.x) * slot.w / h.w;
      let ny;
      if (y > h.y + h.h) ny = slot.y + slot.h + (y - h.y - h.h);
      else if (y < h.y) ny = slot.y - (h.y - y);
      else ny = slot.y + (y - h.y) * slot.h / h.h;
      return [nx, ny];
    };
  }
  /* every overlay of one slot (labels, scale bars, north), placed for the current crop */
  function overlays(slot, c) {
    const g = geo(slot, c), M = mapper(slot, c), h = c.home;
    const inside = (x, y) => x >= slot.x - 0.01 && x <= slot.x + slot.w + 0.01 && y >= slot.y - 0.01 && y <= slot.y + slot.h + 0.01;
    const labels = [];
    c.labels.forEach((L, i) => {
      if (L.on === false) return;
      const u = (L.dot[0] - h.x) / h.w, v = (L.dot[1] - h.y) / h.h;
      const dot = [g.ix + u * g.dw, g.iy + v * g.dh];
      if (!inside(dot[0], dot[1])) return;
      const md = M(L.dot[0], L.dot[1]);
      let end = M(L.end[0], L.end[1]);
      const b = L.box;
      let bx = M(b.align === 'right' ? b.x + b.w : b.align === 'center' ? b.x + b.w / 2 : b.x, b.y);
      bx = [b.align === 'right' ? bx[0] - b.w : b.align === 'center' ? bx[0] - b.w / 2 : bx[0], bx[1]];
      if (Math.abs(L.end[1] - L.dot[1]) < 0.05) { const dy = dot[1] - md[1]; end = [end[0], end[1] + dy]; bx[1] += dy; }
      else if (Math.abs(L.end[0] - L.dot[0]) < 0.05) { const dx = dot[0] - md[0]; end = [end[0] + dx, end[1]]; bx[0] += dx; }
      labels.push({ i, dot, end, box: { x: bx[0], y: bx[1], w: b.w, h: b.h, align: b.align }, runs: L.runs });
    });
    const f = g.dw / h.w;
    const scales = c.scales.map((S) => {
      const p0 = M(S.x0, S.rects[0].y);
      const maxX = Math.max(...S.rects.map((r) => r.x + r.w));
      let x0 = p0[0];
      const right = x0 + (maxX - S.x0) * f + 4;
      if (right > slot.x + slot.w + 2) x0 -= right - (slot.x + slot.w + 2);
      x0 = Math.max(x0, slot.x);
      const dy = p0[1] - S.rects[0].y;
      const rects = S.rects.map((r) => ({ x: x0 + (r.x - S.x0) * f, y: r.y + dy, w: r.w * f, h: r.h, fill: r.fill }));
      const texts = S.texts.map((t) => {
        const b = t.box, ax = b.align === 'right' ? b.x + b.w : b.align === 'center' ? b.x + b.w / 2 : b.x;
        const isUnit = /^[a-z]+$/i.test((t.runs[0] || {}).t || '');
        const nx = isUnit ? x0 + (maxX - S.x0) * f + (ax - maxX) : x0 + (ax - S.x0) * f;
        return { box: { x: b.align === 'right' ? nx - b.w : b.align === 'center' ? nx - b.w / 2 : nx, y: b.y + dy, w: b.w, h: b.h, align: b.align }, runs: t.runs };
      });
      return { rects, texts, shift: x0 - S.x0, dy };
    });
    const norths = c.norths.map((N) => {
      if (scales.length) return { x: N.x + scales[0].shift, y: N.y + scales[0].dy, ang: N.ang };
      const p = M(N.x, N.y);
      return { x: p[0], y: p[1], ang: N.ang };
    });
    return { g, labels, scales, norths };
  }

  /* ---------------------------------------------------------- project (story-plan derived text) */
  function ideaList(P) { return P.ideas.filter((i) => i.on); }
  function capRuns(P, content) {
    if (!content.cap) return null;
    const cap = clone(content.cap);
    const iid = (P.capIdea || {})[content.id.split('~')[0]];
    const r0 = cap[0] && cap[0].runs[0];
    if (iid && r0 && /^\d\s\s/.test(r0.t)) {
      const pos = ideaList(P).findIndex((i) => i.id === iid);
      r0.t = pos >= 0 ? (pos + 1) + '  ' + r0.t.slice(3) : r0.t.slice(3);
    }
    return cap;
  }
  function derivedTexts(P, page) {
    const on = ideaList(P);
    return page.texts.map((t) => {
      if (page.kind === 'board' && t.name === 'ideas') {
        const head = Object.assign({}, t.paras[0], { runs: [Object.assign({}, t.paras[0].runs[0], { t: ['One idea', 'Two ideas', 'Three ideas'][on.length - 1] || 'Ideas' })] });
        const paras = [head].concat(on.map((idea, i) => ({ lh: 1.55, after: 3.4, align: 'left', runs: [
          { t: (i + 1) + ' ', role: 'strong', fs: 10.5, c: '#C8603A' }, { t: idea.title, role: 'strong', fs: 10.5, c: '#1D1D1B' },
          { t: idea.text, role: 'body', fs: 10.5, c: '#3B3B39' }] })));
        return Object.assign({}, t, { paras, locked: 'ideas' });
      }
      if (page.kind === 'slide' && t.name === 'ideas') {
        if (t.paras.length > 1 && t.paras[0].runs[0].role === 'kicker') {
          const paras = [t.paras[0]].concat(on.map((idea, i) => ({ lh: t.paras[1].lh, after: t.paras[1].after, align: 'left', runs: [
            { t: (i + 1) + '  ', role: 'leadStrong', fs: t.paras[1].runs[0].fs, c: t.paras[1].runs[0].c }, { t: idea.title.replace(/\.$/, ''), role: 'lead', fs: t.paras[1].runs[1].fs, c: t.paras[1].runs[1].c }] })));
          return Object.assign({}, t, { paras, locked: 'ideas' });
        }
        const col = page.ideaCols ? page.ideaCols.indexOf(Math.round(t.x - (t.paras[0].runs[0].role === 'title' ? 8.5 : 0))) : -1;
        const idea = on[col];
        if (col < 0) return t;
        if (!idea) return Object.assign({}, t, { hidden: true });
        const r = t.paras[0].runs[0];
        const txt = r.role === 'title' ? String(col + 1) : r.role === 'leadStrong' ? idea.title.replace(/\.$/, '') : (idea.short || idea.text.trim());
        return Object.assign({}, t, { paras: [Object.assign({}, t.paras[0], { runs: [Object.assign({}, r, { t: txt })] })], locked: 'ideas' });
      }
      if (page.kind === 'slide' && t.name === 'footer' && /^\d+ \/ \d+$/.test(t.paras[0].runs[0].t)) {
        const order = visibleSlides(P), pos = order.findIndex((s) => s.n === page.n);
        return Object.assign({}, t, { paras: [Object.assign({}, t.paras[0], { runs: [Object.assign({}, t.paras[0].runs[0], { t: (pos + 1) + ' / ' + order.length })] })] });
      }
      return t;
    });
  }
  /* an idea's icon on the brief slide hides with its idea */
  function decoOf(P, page) {
    if (!page.ideaCols) return page.deco;
    const n = ideaList(P).length;
    return page.deco.filter((d) => !(d.y >= 140 && page.ideaCols.some((c, i) => i >= n && d.x >= c - 1 && d.x <= c + 20)));
  }
  function visibleSlides(P) { return P.slideOrder.map((n) => P.slides.find((s) => s.n === n)).filter((s) => !P.slideOff.includes(s.n)); }

  function prepare(P) {
    /* idea columns on the brief slide, short deck lines for each idea */
    P.slides.forEach((s) => {
      const nums = s.texts.filter((t) => t.name === 'ideas' && t.paras.length === 1 && t.paras[0].runs[0].role === 'title');
      if (nums.length) s.ideaCols = nums.map((t) => Math.round(t.x - 8.5)).sort((a, b) => a - b);
      s.texts.forEach((t) => {
        if (t.name === 'ideas' && t.paras.length === 1 && t.paras[0].runs[0].role === 'body') {
          const col = (s.ideaCols || []).indexOf(Math.round(t.x));
          if (P.ideas[col] && !P.ideas[col].short) P.ideas[col].short = t.paras[0].runs[0].t;
        }
      });
    });
    return P;
  }

  /* ---------------------------------------------------------- rendering */
  function runsHTML(P, kind, runs, editable) {
    return runs.map((r, j) => {
      const s = runStyle(P.ts, kind, r);
      const st = 'font-family:' + s.css + ';font-weight:' + s.weight + ';font-size:' + s.size.toFixed(2) + 'pt;color:' + s.color +
        (s.track ? ';letter-spacing:' + s.track + 'em' : '') + (s.upper ? ';text-transform:uppercase' : '') + (s.italic ? ';font-style:italic' : '');
      return '<span class="r" data-role="' + r.role + '" data-fs="' + r.fs + '" data-c="' + (r.c || '') + '" style="' + st + '">' + esc(r.t) + '</span>';
    }).join('');
  }
  function parasHTML(P, kind, paras) {
    return paras.map((p) => {
      const mx = Math.max(6, ...p.runs.map((r) => runStyle(P.ts, kind, r).size));
      return '<p style="font-size:' + mx.toFixed(2) + 'pt;line-height:' + p.lh + ';margin:0 0 ' + (p.after || 0) + 'mm 0;text-align:' + (p.align || 'left') + '">' + runsHTML(P, kind, p.runs) + '</p>';
    }).join('');
  }
  const box = (b) => 'left:' + b.x.toFixed(2) + 'mm;top:' + b.y.toFixed(2) + 'mm;width:' + b.w.toFixed(2) + 'mm;' + (b.h ? 'height:' + b.h.toFixed(2) + 'mm;' : '');

  function slotHTML(P, page, slot) {
    const c = page.contents[slot.content], g = geo(slot, c);
    return '<div class="slot" data-slot="' + slot.id + '" style="' + box(slot) + '"><img src="' + srcOf(P, c.src) + '" alt="' + esc(c.alt || '') +
      '" draggable="false" style="left:' + g.left.toFixed(3) + 'mm;top:' + g.top.toFixed(3) + 'mm;width:' + g.dw.toFixed(3) + 'mm;height:' + g.dh.toFixed(3) + 'mm"></div>';
  }
  function overlayHTML(P, page, slot) {
    const c = page.contents[slot.content], o = overlays(slot, c), kind = page.kind;
    let svg = '', html = '';
    o.labels.forEach((L) => {
      svg += '<line x1="' + L.end[0].toFixed(2) + '" y1="' + L.end[1].toFixed(2) + '" x2="' + L.dot[0].toFixed(2) + '" y2="' + L.dot[1].toFixed(2) + '" stroke="#4A4A48" stroke-width="0.17"/>' +
        '<circle cx="' + L.dot[0].toFixed(2) + '" cy="' + L.dot[1].toFixed(2) + '" r="0.65" fill="#4A4A48" stroke="#ffffff" stroke-width="0.25"/>';
      html += '<div class="lab" data-slot="' + slot.id + '" data-label="' + L.i + '" style="' + box(L.box) + 'text-align:' + L.box.align + ';line-height:' + L.box.h.toFixed(2) + 'mm">' + runsHTML(P, kind, L.runs) + '</div>';
    });
    o.scales.forEach((S) => {
      S.rects.forEach((r) => { svg += '<rect x="' + r.x.toFixed(2) + '" y="' + r.y.toFixed(2) + '" width="' + r.w.toFixed(2) + '" height="' + r.h.toFixed(2) + '" fill="' + r.fill + '" stroke="#4A4A48" stroke-width="0.12"/>'; });
      S.texts.forEach((t) => { html += '<div class="lab sc" style="' + box(t.box) + 'text-align:' + t.box.align + ';line-height:' + t.box.h.toFixed(2) + 'mm">' + runsHTML(P, kind, t.runs) + '</div>'; });
    });
    o.norths.forEach((N) => {
      svg += '<g transform="rotate(' + N.ang + ' ' + N.x.toFixed(2) + ' ' + N.y.toFixed(2) + ')"><path d="M' + N.x.toFixed(2) + ' ' + (N.y - 3).toFixed(2) + ' L' + (N.x + 1.3).toFixed(2) + ' ' + (N.y + 1.6).toFixed(2) +
        ' L' + (N.x - 1.3).toFixed(2) + ' ' + (N.y + 1.6).toFixed(2) + ' Z" fill="#4A4A48"/></g>';
      const r = (N.ang * Math.PI) / 180, nx = N.x + 3.9 * Math.sin(r), ny = N.y - 3.9 * Math.cos(r);
      html += '<div class="lab nth" style="left:' + (nx - 3).toFixed(2) + 'mm;top:' + (ny - 1.3).toFixed(2) + 'mm;width:6mm;height:2.6mm;text-align:center;line-height:2.6mm">' +
        runsHTML(P, kind, [{ t: 'N', role: 'small', fs: 6.5, c: '#4A4A48' }]) + '</div>';
    });
    return '<div class="ov" data-ov="' + slot.id + '"><svg viewBox="0 0 ' + page.w + ' ' + page.h + '" style="width:' + page.w + 'mm;height:' + page.h + 'mm" aria-hidden="true">' + svg + '</svg>' + html + '</div>';
  }
  function captionHTML(P, page, slot) {
    if (!slot.cap) return '';
    const c = page.contents[slot.content], cap = capRuns(P, c);
    if (!cap) return '';
    return '<div class="tb cap" data-cap="' + slot.id + '"' + (slot.cap.maxH ? ' data-max="' + slot.cap.maxH + '"' : '') + ' style="' + box(slot.cap) + '">' + parasHTML(P, page.kind, cap) + '</div>';
  }
  function textHTML(P, page, t) {
    if (t.hidden) return '';
    if (t.kind === 'info') {
      const rows = t.rows.map((r, i) => {
        const k = runStyle(P.ts, page.kind, { role: 'kicker', fs: 7.5, c: '#6B6B68' }), v = runStyle(P.ts, page.kind, { role: 'body', fs: 8, c: r.ph ? '#D33A2C' : '#1D1D1B' });
        return '<tr><th style="font-family:' + k.css + ';font-weight:' + k.weight + ';font-size:' + k.size + 'pt;letter-spacing:' + k.track + 'em;color:#6B6B68">' + esc(r.k) +
          '</th><td data-row="' + i + '" style="font-family:' + v.css + ';font-weight:400;font-size:' + v.size + 'pt;color:' + v.color + '">' + esc(r.v) + '</td></tr>';
      }).join('');
      return '<div class="tb info" data-text="' + t.id + '" style="' + box(t) + '"><table>' + rows + '</table></div>';
    }
    const va = { top: 'flex-start', middle: 'center', bottom: 'flex-end' }[t.valign || 'top'];
    return '<div class="tb' + (t.nowrap ? ' nw' : '') + (t.locked ? ' locked' : '') + '" data-text="' + t.id + '"' + (t.h ? ' data-h="1"' : '') + (t.maxH ? ' data-max="' + t.maxH + '"' : '') + ' style="' + box(t) + 'justify-content:' + va + '">' + parasHTML(P, page.kind, t.paras) + '</div>';
  }
  function pageHTML(P, page) {
    let h = '';
    decoOf(P, page).forEach((d) => { h += '<img class="deco" src="' + srcOf(P, d.src) + '" alt="" style="' + box(d) + '">'; });
    page.slots.forEach((s) => { h += slotHTML(P, page, s); });
    if (page.svg) h += '<svg class="static" viewBox="0 0 ' + page.w + ' ' + page.h + '" style="width:' + page.w + 'mm;height:' + page.h + 'mm" aria-hidden="true">' + page.svg + '</svg>';
    page.slots.forEach((s) => { h += overlayHTML(P, page, s) + captionHTML(P, page, s); });
    derivedTexts(P, page).forEach((t) => { h += textHTML(P, page, t); });
    return h;
  }
  function renderInto(el, P, page) {
    el.className = 'sheet ' + page.kind;
    el.style.width = page.w + 'mm';
    el.style.height = page.h + 'mm';
    el.innerHTML = pageHTML(P, page);
    checkOver(el);
    return el;
  }
  function isOver(t) {
    if (t.dataset.h) return t.scrollHeight > t.clientHeight + 2;
    if (t.dataset.max) return t.offsetHeight > (+t.dataset.max) * MMPX + 1;
    return false;
  }
  /* titles shrink to fit their box (at most to 70%), like the layout engine; other text shows a warning instead */
  function fitTitles(t) {
    const spans = [...t.querySelectorAll('.r[data-role="title"]')];
    if (!spans.length || t.classList.contains('editing')) return;
    for (let i = 0; i < 7 && isOver(t); i++) {
      spans.forEach((sp) => { sp.style.fontSize = (parseFloat(sp.style.fontSize) * 0.95).toFixed(2) + 'pt'; const p = sp.parentNode; if (p.style.fontSize) p.style.fontSize = (parseFloat(p.style.fontSize) * 0.95).toFixed(2) + 'pt'; });
    }
  }
  function checkOver(el) { el.querySelectorAll('.tb[data-h], .tb[data-max]').forEach((t) => { fitTitles(t); t.classList.toggle('over', isOver(t)); }); }
  /* a sheet scaled to a width in CSS px (thumbnails, previews) */
  function miniSheet(P, page, widthPx) {
    const wrap = document.createElement('div');
    wrap.className = 'mini';
    const k = widthPx / (page.w * MMPX);
    wrap.style.width = widthPx + 'px';
    wrap.style.height = (page.h * MMPX * k) + 'px';
    const s = document.createElement('div');
    renderInto(s, P, page);
    s.style.transform = 'scale(' + k + ')';
    s.style.transformOrigin = '0 0';
    wrap.appendChild(s);
    return wrap;
  }

  /* ---------------------------------------------------------- the editor */
  function Editor(root, opts) {
    this.root = root;
    this.opts = opts;           // { getP, setP(P, label), onSelect, panel, toast }
    this.sel = null;            // { type: 'slot'|'text'|'cap'|'label'|'info', slot, id, page }
    this.view = 'board';
    this.slideN = null;
    this.zoom = 1;              // view zoom on top of fit
    this.editing = null;
  }
  Editor.prototype.page = function () {
    const P = this.opts.getP();
    if (this.view === 'board') return P.board;
    const vis = visibleSlides(P);
    if (!vis.find((s) => s.n === this.slideN)) this.slideN = vis[0] ? vis[0].n : P.slides[0].n;
    return P.slides.find((s) => s.n === this.slideN);
  };
  Editor.prototype.fitScale = function () {
    const page = this.page(), vp = this.root.querySelector('.viewport');
    const W = vp.clientWidth - 32, Hh = vp.clientHeight - 32;
    const phone = window.matchMedia('(max-width: 899px)').matches;
    const kx = W / (page.w * MMPX), ky = Hh / (page.h * MMPX);
    const fit = page.kind === 'board' && phone ? kx : Math.min(kx, ky);
    return Math.max(0.05, fit) * this.zoom;
  };
  Editor.prototype.render = function () {
    const P = this.opts.getP(), page = this.page();
    const vp = this.root.querySelector('.viewport');
    let holder = vp.querySelector('.holder');
    if (!holder) { holder = document.createElement('div'); holder.className = 'holder'; vp.appendChild(holder); }
    let sheet = holder.querySelector('.sheet');
    if (!sheet) { sheet = document.createElement('div'); holder.appendChild(sheet); }
    renderInto(sheet, P, page);
    sheet.classList.add('editable');
    const k = this.fitScale();
    this.k = k;
    sheet.style.transform = 'scale(' + k + ')';
    sheet.style.transformOrigin = '0 0';
    holder.style.width = (page.w * MMPX * k) + 'px';
    holder.style.height = (page.h * MMPX * k) + 'px';
    this.sheet = sheet;
    this.markSel();
    this.bind();
  };
  Editor.prototype.markSel = function () {
    const s = this.sel;
    this.sheet.querySelectorAll('.is-sel').forEach((e) => e.classList.remove('is-sel'));
    if (!s) return;
    const q = s.type === 'slot' ? '.slot[data-slot="' + s.slot + '"]' : s.type === 'cap' ? '.cap[data-cap="' + s.slot + '"]' :
      s.type === 'label' ? '.lab[data-slot="' + s.slot + '"][data-label="' + s.label + '"]' : '.tb[data-text="' + s.id + '"]';
    const el = this.sheet.querySelector(q);
    if (el) el.classList.add('is-sel');
    else this.sel = null;
  };
  Editor.prototype.select = function (sel) {
    if (this.editing) this.stopEdit();
    this.sel = sel;
    this.markSel();
    this.opts.onSelect(sel);
  };
  Editor.prototype.toMM = function (ev) {
    const r = this.sheet.getBoundingClientRect();
    return [(ev.clientX - r.left) / (MMPX * this.k), (ev.clientY - r.top) / (MMPX * this.k)];
  };
  Editor.prototype.slotAt = function (ev) {
    const page = this.page(), p = this.toMM(ev);
    return page.slots.find((s) => p[0] >= s.x && p[0] <= s.x + s.w && p[1] >= s.y && p[1] <= s.y + s.h);
  };
  Editor.prototype.bind = function () {
    if (this.bound) return;
    this.bound = true;
    const vp = this.root.querySelector('.viewport');
    const self = this;
    let drag = null;
    const pointers = new Map();
    vp.addEventListener('pointerdown', (ev) => {
      const t = ev.target;
      if (self.editing && self.editing.contains(t)) return;
      const slotEl = t.closest('.slot'), tb = t.closest('.tb'), lab = t.closest('.lab[data-label]');
      if (lab) { self.select({ type: 'label', slot: lab.dataset.slot, label: +lab.dataset.label }); return; }
      if (tb) {
        const sel = tb.dataset.cap ? { type: 'cap', slot: tb.dataset.cap } : { type: tb.classList.contains('info') ? 'info' : 'text', id: tb.dataset.text, locked: tb.classList.contains('locked') };
        const same = self.sel && self.sel.type === sel.type && (self.sel.slot || self.sel.id) === (sel.slot || sel.id);
        if (same && !sel.locked) { self.startEdit(tb, ev); return; }
        self.select(sel);
        return;
      }
      if (slotEl) {
        const id = slotEl.dataset.slot;
        pointers.set(ev.pointerId, [ev.clientX, ev.clientY]);
        const page = self.page(), slot = page.slots.find((s) => s.id === id), c = page.contents[slot.content];
        if (self.sel && self.sel.type === 'slot' && self.sel.slot === id) {
          ev.preventDefault();
          vp.setPointerCapture(ev.pointerId);
          drag = { mode: pointers.size > 1 ? 'pinch' : 'pan', id, x0: ev.clientX, y0: ev.clientY, v0: Object.assign({}, c.view), moved: false,
            d0: pointers.size > 1 ? dist(pointers) : 0 };
          if (pointers.size > 1) { drag.mode = 'pinch'; drag.d0 = dist(pointers); drag.v0 = Object.assign({}, c.view); }
        } else {
          self.select({ type: 'slot', slot: id });
          if (ev.pointerType === 'mouse') {
            vp.setPointerCapture(ev.pointerId);
            drag = { mode: 'swap', id, x0: ev.clientX, y0: ev.clientY, moved: false };
          }
        }
        return;
      }
      if (t.closest('.sheet') || t === vp || t.closest('.holder')) self.select(null);
    });
    function dist(m) { const a = [...m.values()]; return Math.hypot(a[0][0] - a[1][0], a[0][1] - a[1][1]); }
    vp.addEventListener('pointermove', (ev) => {
      if (pointers.has(ev.pointerId)) pointers.set(ev.pointerId, [ev.clientX, ev.clientY]);
      if (!drag) return;
      const P = self.opts.getP(), page = self.page(), slot = page.slots.find((s) => s.id === drag.id), c = page.contents[slot.content];
      if (drag.mode === 'swap') {
        if (!drag.moved && Math.hypot(ev.clientX - drag.x0, ev.clientY - drag.y0) < 6) return;
        drag.moved = true;
        let gh = document.getElementById('ghost');
        if (!gh) { gh = document.createElement('img'); gh.id = 'ghost'; gh.src = srcOf(P, c.src); gh.alt = ''; document.body.appendChild(gh); }
        gh.style.left = ev.clientX + 'px'; gh.style.top = ev.clientY + 'px';
        const over = self.slotAt(ev);
        self.sheet.querySelectorAll('.drop').forEach((e) => e.classList.remove('drop'));
        if (over && over.id !== drag.id) self.sheet.querySelector('.slot[data-slot="' + over.id + '"]').classList.add('drop');
        return;
      }
      if (pointers.size > 1 && drag.mode !== 'pinch') { drag.mode = 'pinch'; drag.d0 = dist(pointers); drag.v0 = Object.assign({}, c.view); }
      if (drag.mode === 'pinch') {
        if (pointers.size < 2) return;
        c.view.z = clamp(drag.v0.z * dist(pointers) / drag.d0, 1, 4);
      } else {
        const g = geo(slot, Object.assign({}, c, { view: drag.v0 }));
        const dxmm = (ev.clientX - drag.x0) / (MMPX * self.k), dymm = (ev.clientY - drag.y0) / (MMPX * self.k);
        c.view.cx = clamp(drag.v0.cx - dxmm / g.dw, 0, 1);
        c.view.cy = clamp(drag.v0.cy - dymm / g.dh, 0, 1);
      }
      drag.moved = true;
      self.liveSlot(slot);
    });
    const end = (ev) => {
      pointers.delete(ev.pointerId);
      if (!drag) return;
      const d = drag;
      if (pointers.size > 0 && d.mode === 'pinch') return;
      drag = null;
      const gh = document.getElementById('ghost');
      if (gh) gh.remove();
      self.sheet.querySelectorAll('.drop').forEach((e) => e.classList.remove('drop'));
      if (d.mode === 'swap') {
        if (!d.moved) return;
        const over = self.slotAt(ev);
        if (over && over.id !== d.id) self.swap(d.id, over.id);
        return;
      }
      if (d.moved) self.commit(d.mode === 'pinch' ? 'Zoom picture' : 'Move picture');
    };
    vp.addEventListener('pointerup', end);
    vp.addEventListener('pointercancel', end);
    vp.addEventListener('wheel', (ev) => {
      if (!self.sel || self.sel.type !== 'slot') return;
      const s = self.slotAt(ev);
      if (!s || s.id !== self.sel.slot) return;
      ev.preventDefault();
      const page = self.page(), c = page.contents[s.content];
      c.view.z = clamp(c.view.z * Math.exp(-ev.deltaY * 0.0015), 1, 4);
      self.liveSlot(s);
      clearTimeout(self.wheelT);
      self.wheelT = setTimeout(() => self.commit('Zoom picture'), 400);
    }, { passive: false });
  };
  /* fast update of one slot while dragging */
  Editor.prototype.liveSlot = function (slot) {
    const P = this.opts.getP(), page = this.page(), c = page.contents[slot.content], g = geo(slot, c);
    const img = this.sheet.querySelector('.slot[data-slot="' + slot.id + '"] img');
    Object.assign(img.style, { left: g.left + 'mm', top: g.top + 'mm', width: g.dw + 'mm', height: g.dh + 'mm' });
    const ov = this.sheet.querySelector('.ov[data-ov="' + slot.id + '"]');
    const tmp = document.createElement('div');
    tmp.innerHTML = overlayHTML(P, page, slot);
    ov.replaceWith(tmp.firstChild);
    this.opts.onLive && this.opts.onLive(slot, c);
  };
  Editor.prototype.swap = function (a, b) {
    const page = this.page(), sa = page.slots.find((s) => s.id === a), sb = page.slots.find((s) => s.id === b);
    const t = sa.content; sa.content = sb.content; sb.content = t;
    [sa, sb].forEach((s) => { page.contents[s.content].view = { z: 1, cx: 0.5, cy: 0.5 }; });
    this.sel = { type: 'slot', slot: b };
    this.commit('Swap pictures');
  };
  Editor.prototype.replace = function (slotId, libItem) {
    const P = this.opts.getP(), page = this.page(), slot = page.slots.find((s) => s.id === slotId);
    const c = clone(libItem);
    c.id = libItem.id.split('~')[0] + '~' + Date.now().toString(36);
    c.view = { z: 1, cx: 0.5, cy: 0.5 };
    page.contents[c.id] = c;
    slot.content = c.id;
    this.commit('Replace picture');
  };
  Editor.prototype.commit = function (label) {
    this.opts.setP(this.opts.getP(), label);
    this.render();
    this.opts.onSelect(this.sel);
  };

  /* ---------- text editing */
  Editor.prototype.startEdit = function (tb, ev) {
    if (this.editing === tb) return;
    if (this.editing) this.stopEdit();
    this.editing = tb;
    tb.classList.add('editing');
    if (tb.classList.contains('info')) tb.querySelectorAll('td').forEach((td) => td.setAttribute('contenteditable', 'true'));
    else tb.setAttribute('contenteditable', 'true');
    tb.spellcheck = true;
    const self = this;
    const target = tb.classList.contains('info') ? (ev && ev.target.closest('td')) || tb.querySelector('td') : tb;
    setTimeout(() => {
      target.focus();
      if (ev && document.caretRangeFromPoint) {
        const r = document.caretRangeFromPoint(ev.clientX, ev.clientY);
        if (r) { const s = window.getSelection(); s.removeAllRanges(); s.addRange(r); }
      }
    }, 0);
    this.onKey = (e) => {
      if (e.key === 'Enter') { e.preventDefault(); if (!e.shiftKey) target.blur(); }
      if (e.key === 'Escape') { e.preventDefault(); target.blur(); }
    };
    this.onInput = () => {
      clearTimeout(self.typeT);
      self.typeT = setTimeout(() => self.saveText(false), 700);
      tb.classList.toggle('over', isOver(tb));
      self.opts.onTyping && self.opts.onTyping(tb.classList.contains('over'));
    };
    this.onPaste = (e) => { e.preventDefault(); const t = (e.clipboardData || window.clipboardData).getData('text/plain').replace(/\s*\n\s*/g, ' '); document.execCommand('insertText', false, t); };
    this.onBlur = () => setTimeout(() => { if (self.editing === tb && !tb.contains(document.activeElement)) self.stopEdit(); }, 0);
    tb.addEventListener('keydown', this.onKey);
    tb.addEventListener('input', this.onInput);
    tb.addEventListener('paste', this.onPaste);
    tb.addEventListener('focusout', this.onBlur);
  };
  Editor.prototype.saveText = function (final) {
    const tb = this.editing;
    if (!tb) return false;
    const P = this.opts.getP(), page = this.page();
    let changed = false;
    if (tb.classList.contains('info')) {
      const t = page.texts.find((x) => x.id === tb.dataset.text);
      tb.querySelectorAll('td').forEach((td) => {
        const r = t.rows[+td.dataset.row], v = td.textContent.trim();
        if (r.v !== v) { r.v = v; r.ph = /^\[.*\]$/.test(v); changed = true; }
      });
    } else {
      const old = tb.dataset.cap ? capRuns(P, page.contents[page.slots.find((s) => s.id === tb.dataset.cap).content]) : page.texts.find((x) => x.id === tb.dataset.text).paras;
      const paras = readParas(tb, old);
      if (tb.dataset.cap) {
        const c = page.contents[page.slots.find((s) => s.id === tb.dataset.cap).content];
        const before = JSON.stringify(c.cap);
        const iid = (P.capIdea || {})[c.id.split('~')[0]];
        if (iid && /^\d\s\s/.test((c.cap[0].runs[0] || {}).t || '') && paras[0] && paras[0].runs[0]) paras[0].runs[0].t = '1  ' + paras[0].runs[0].t.replace(/^\d\s\s/, '');
        c.cap = paras;
        changed = before !== JSON.stringify(paras);
      } else {
        const t = page.texts.find((x) => x.id === tb.dataset.text);
        changed = JSON.stringify(t.paras) !== JSON.stringify(paras);
        t.paras = paras;
      }
    }
    if (changed) this.opts.setP(P, 'Edit text', !final);
    return changed;
  };
  Editor.prototype.stopEdit = function () {
    const tb = this.editing;
    if (!tb) return;
    clearTimeout(this.typeT);
    this.saveText(true);
    tb.removeEventListener('keydown', this.onKey);
    tb.removeEventListener('input', this.onInput);
    tb.removeEventListener('paste', this.onPaste);
    tb.removeEventListener('focusout', this.onBlur);
    this.editing = null;
    this.render();
    this.opts.onSelect(this.sel);
  };
  function readParas(tb, old) {
    const ps = [...tb.querySelectorAll('p')];
    return ps.map((p, i) => {
      const o = old[i] || old[old.length - 1];
      const runs = [];
      const walk = (n, role) => {
        n.childNodes.forEach((k) => {
          if (k.nodeType === 3) {
            if (runs.length && runs[runs.length - 1].role === role.role) runs[runs.length - 1].t += k.textContent;
            else runs.push({ t: k.textContent, role: role.role, fs: role.fs, c: role.c });
          } else if (k.nodeType === 1) {
            const sp = k.closest('.r');
            const rr = sp ? { role: sp.dataset.role, fs: +sp.dataset.fs, c: sp.dataset.c } : role;
            if (k.classList && k.classList.contains('r')) runs.push({ t: '', role: rr.role, fs: rr.fs, c: rr.c });
            walk(k, rr);
          }
        });
      };
      const r0 = o.runs[0] || { role: 'body', fs: 10, c: '#1D1D1B' };
      walk(p, { role: r0.role, fs: r0.fs, c: r0.c });
      const clean = runs.filter((r) => r.t !== '');
      return { lh: o.lh, after: o.after, align: o.align, runs: clean.length ? clean : [{ t: '', role: r0.role, fs: r0.fs, c: r0.c }] };
    });
  }

  window.FGA = { srcOf, decoOf, MMPX, PTMM, TS, runStyle, geo, overlays, mapper, renderInto, miniSheet, Editor, visibleSlides, derivedTexts, capRuns, prepare, clone, esc };
})();
