/* Studio FGA: turns what the server sends into the one model editor.js draws, edits and exports.

   fromLayout(board, deck, key)  the paid build's layout.json files (format "fga-layout" v1, measured from the
                                 engine's own board and deck) -> the editor's model. Pictures become slots you can
                                 crop and swap; labels, scale bars and north arrows ride on their picture; captions
                                 follow their picture; everything else stays where the engine put it.
   fromPlan(edit, plan, card, dims)  the free preview's story plan -> a first sketch of the board and deck, drawn
                                 from the student's own drawings (the preview makes no pictures and no layout).

   Positions are millimetres from the sheet's top-left, type in points, as in editor.js. */
(function () {
  'use strict';
  const PT = 25.4 / 72;
  const r2 = (v) => Math.round(v * 100) / 100;

  /* ---------------------------------------------------------- layout.json -> model */
  function role(pr, r) {
    const w = r.weight || 400;
    if (pr === 'Title') return 'title';
    if (pr === 'Lead') return w >= 600 ? 'leadStrong' : 'lead';
    if (pr === 'Kicker') return 'kicker';
    if (pr === 'Caption title') return 'captionTitle';
    if (pr === 'Caption') return r.italic ? 'captionText' : 'body';
    if (pr === 'Label') return 'label';
    if (pr === 'Footer') return 'small';
    return w >= 600 ? 'strong' : 'body';
  }
  const runsOf = (p) => p.runs.map((r) => ({ t: String(r.t || '').replace(/\t/g, ' '), role: role(p.role, r), fs: r.size || 10, c: r.color || '#1D1D1B' }));
  function parasOf(it) {
    return it.paras.map((p, i) => {
      const nx = it.paras[i + 1], mx = Math.max(1, ...p.runs.map((r) => r.size || 10));
      return { lh: r2((p.lead || mx * 1.2) / mx) || 1.2, after: nx ? r2((nx.before || 0) * PT) : 0, align: p.align || 'left', runs: runsOf(p) };
    });
  }
  /* The engine measured each frame from its first baseline; CSS puts the baseline half a leading plus about
     0.36 em below the box top (Inter's metrics), so the box moves up by the difference. */
  function cssTop(it) {
    const p = it.paras[0] || { runs: [] }, s = Math.max(1, ...p.runs.map((r) => r.size || 10)), lead = p.lead || s * 1.2;
    return it.y + (it.fb || 0) - (lead / 2 + 0.363 * s) * PT;
  }
  function oneLineBox(it) {   // labels and scale-bar numbers: the editor centres one line in the box height
    const p = it.paras[0] || { runs: [] }, s = Math.max(1, ...p.runs.map((r) => r.size || 7)) * PT;
    return { x: r2(it.x), y: r2(it.y + (it.fb || it.h * 0.65) - (it.h / 2 + 0.363 * s)), w: r2(it.w), h: r2(it.h), align: (p.align || 'left') };
  }
  const isNorthText = (it) => it.k === 'text' && it.paras.some((p) => p.style === 'North');
  const bbox = (pts) => { const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]); return { x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) }; };
  const inRect = (x, y, r, pad) => x >= r.x - pad && x <= r.x + r.w + pad && y >= r.y - pad && y <= r.y + r.h + pad;
  function distToBox(x, y, b) { const dx = Math.max(b.x - x, 0, x - (b.x + b.w)), dy = Math.max(b.y - y, 0, y - (b.y + b.h)); return Math.hypot(dx, dy); }
  function svgOf(it) {
    const st = ' fill="' + (it.fill || 'none') + '" stroke="' + (it.stroke || 'none') + '" stroke-width="' + r2(it.wmm || 0) + '"';
    if (it.k === 'oval') return '<ellipse cx="' + r2(it.cx) + '" cy="' + r2(it.cy) + '" rx="' + r2(it.rx) + '" ry="' + r2(it.ry) + '"' + st + '/>';
    return '<path d="M' + it.pts.map((p) => r2(p[0]) + ' ' + r2(p[1])).join(' L') + (it.closed ? ' Z' : '') + '"' + st + '/>';
  }

  function page(lp, kind, folder, nPage) {
    const pre = kind === 'board' ? 'b' : 's' + nPage;
    const pg = { kind, n: kind === 'board' ? undefined : nPage, w: lp.w, h: lp.h, slots: [], contents: {}, texts: [], deco: [], svg: '' };
    const items = lp.items.slice(), used = new Set();
    /* pictures: icons and colour bands are decoration; the rest are slots */
    items.forEach((it, i) => {
      if (it.k !== 'img') return;
      used.add(i);
      const src = folder + it.src;
      if (/(^|\/)(icon|band)-[^/]*\.png$/i.test(it.src) || (it.w < 14 && it.h < 14)) { pg.deco.push({ src, x: it.x, y: it.y, w: it.w, h: it.h }); return; }
      const id = pre + '-p' + pg.slots.length, px = it.px || [it.w * 10, it.h * 10];
      pg.slots.push({ id, x: it.x, y: it.y, w: it.w, h: it.h, cap: null, content: id });
      pg.contents[id] = { id, src, iw: px[0], ih: px[1], alt: it.alt || it.name || '', home: { x: it.x, y: it.y, w: it.w, h: it.h }, view: { z: 1, cx: 0.5, cy: 0.5 },
        cap: null, labels: [], scales: [], norths: [] };
    });
    const slotAt = (x, y, below) => pg.slots.find((s) => x >= s.x - 0.5 && x <= s.x + s.w + 0.5 && y >= s.y - 0.5 && y <= s.y + s.h + (below || 0.5));
    /* labels: a dot on the drawing, a straight leader, and the words at its other end */
    const dots = items.map((it, i) => [it, i]).filter(([it]) => it.k === 'oval' && it.rx < 2 && it.ry < 2);
    const labelTexts = items.map((it, i) => [it, i]).filter(([it]) => it.k === 'text' && /^(lab|label)$/.test(it.name) && !isNorthText(it));
    items.forEach((ld, li) => {
      if (used.has(li) || ld.k !== 'path' || ld.closed || !ld.pts || ld.pts.length !== 2) return;
      const ends = ld.pts;
      let hit = null;
      dots.forEach(([d, di]) => { if (used.has(di)) return; ends.forEach((e, ei) => { if (!hit && Math.abs(e[0] - d.cx) < 0.06 && Math.abs(e[1] - d.cy) < 0.06) hit = { d, di, ei }; }); });
      if (!hit) return;
      const dot = [hit.d.cx, hit.d.cy], end = ends[1 - hit.ei];
      const slot = slotAt(dot[0], dot[1]);
      if (!slot) return;
      let best = null, bd = 6;
      labelTexts.forEach(([t, ti]) => { if (used.has(ti)) return; const dd = distToBox(end[0], end[1], t); if (dd < bd) { bd = dd; best = [t, ti]; } });
      if (!best) return;
      used.add(li); used.add(hit.di); used.add(best[1]);
      pg.contents[slot.content].labels.push({ dot, end: [end[0], end[1]], box: oneLineBox(best[0]), runs: runsOf(best[0].paras[0]).map((r) => Object.assign(r, { role: 'label' })), on: true });
    });
    /* scale bars: a group of thin rectangles plus their numbers */
    const groups = {};
    items.forEach((it, i) => { if (!used.has(i) && it.k === 'path' && it.closed && it.grp && it.pts.length === 4) { const b = bbox(it.pts); if (b.h < 3 && b.w > 0.5) (groups[it.grp] = groups[it.grp] || []).push([it, i, b]); } });
    Object.values(groups).forEach((g) => {
      if (g.length < 2) return;
      const minX = Math.min(...g.map((x) => x[2].x)), maxX = Math.max(...g.map((x) => x[2].x + x[2].w)), y0 = g[0][2].y;
      const slot = slotAt((minX + maxX) / 2, y0, 14);
      if (!slot) return;
      const texts = [];
      items.forEach((t, ti) => {
        if (used.has(ti) || t.k !== 'text' || !/^(sct|scale)$/.test(t.name)) return;
        const cx = t.x + t.w / 2, cy = t.y + t.h / 2;
        if (cx >= minX - 8 && cx <= maxX + 8 && Math.abs(cy - y0) < 6) { used.add(ti); texts.push({ box: oneLineBox(t), runs: runsOf(t.paras[0]).map((r) => Object.assign(r, { role: 'small' })) }); }
      });
      g.forEach(([, i]) => used.add(i));
      pg.contents[slot.content].scales.push({ x0: minX, rects: g.map(([it, , b]) => ({ x: b.x, y: b.y, w: b.w, h: b.h, fill: it.fill || '#4A4A48' })), texts });
    });
    /* north arrows: a small closed shape with an "N" beside it */
    items.forEach((it, i) => {
      if (used.has(i) || it.k !== 'path' || !it.closed || !it.pts || it.pts.length < 3 || it.pts.length > 4) return;
      const b = bbox(it.pts);
      if (b.w > 8 || b.h > 8 || !(it.name === 'north' || it.name === 'path')) return;
      const cx = it.pts.reduce((a, p) => a + p[0], 0) / it.pts.length, cy = it.pts.reduce((a, p) => a + p[1], 0) / it.pts.length;
      const nIdx = items.findIndex((t, ti) => !used.has(ti) && (t.name === 'northt' || isNorthText(t)) && distToBox(cx, cy, t) < 8);
      if (nIdx < 0 && it.name !== 'north') return;
      const slot = slotAt(cx, cy, 14);
      if (!slot) return;
      const tip = it.pts.reduce((a, p) => (Math.hypot(p[0] - cx, p[1] - cy) > Math.hypot(a[0] - cx, a[1] - cy) ? p : a), it.pts[0]);
      const ang = Math.round(Math.atan2(tip[0] - cx, -(tip[1] - cy)) * 180 / Math.PI);
      used.add(i); if (nIdx >= 0) used.add(nIdx);
      pg.contents[slot.content].norths.push({ x: r2(cx), y: r2(cy), ang });
    });
    /* captions sit on or just under their picture */
    items.forEach((it, i) => {
      if (used.has(i) || it.k !== 'text' || it.name !== 'caption') return;
      let best = null, bd = 9;
      pg.slots.forEach((s) => {
        if (s.cap) return;
        const ov = Math.min(it.x + it.w, s.x + s.w) - Math.max(it.x, s.x);
        if (ov < Math.min(it.w, s.w) * 0.5) return;
        const d = it.y >= s.y && it.y <= s.y + s.h ? 0.5 : it.y - (s.y + s.h);
        if (d >= -0.5 && d < bd) { bd = d; best = s; }
      });
      if (!best) return;
      used.add(i);
      const y = cssTop(it);
      best.cap = { x: r2(it.x), y: r2(y), w: r2(it.w + 0.6), h: null, maxH: r2(it.h + (it.y - y) + 2) };
      pg.contents[best.content].cap = parasOf(it);
    });
    /* everything else: text frames where the engine set them, shapes drawn as they are */
    items.forEach((it, i) => {
      if (used.has(i)) return;
      if (it.k === 'text') {
        if (it.m) return;   // a rotated one-off (rare): left to the original files
        const name = it.name === 'ideas' ? 'idea' : it.name;   // the build already wrote the ideas: no re-deriving here
        if (kind === 'board' && it.name === 'info') {
          const rows = it.paras.map((p) => {
            const k = p.runs[0] || { t: '' }, rest = p.runs.slice(1);
            const v = rest.map((r) => r.t).join('').replace(/\t/g, ' ').trim();
            return { k: k.t.trim(), v, ph: rest.some((r) => r.cs === 'Placeholder') || /^\[.*\]$/.test(v) };
          });
          pg.texts.push({ id: pre + '-t' + i, name: 'info', kind: 'info', x: it.x, y: it.y, w: it.w, h: null, rows, maxH: r2(it.h + 4) });
          return;
        }
        const y = cssTop(it);
        pg.texts.push({ id: pre + '-t' + i, name, x: r2(it.x), y: r2(y), w: r2(it.w + (it.nowrap ? 1 : 0.6)), h: null, valign: 'top', nowrap: !!it.nowrap,
          maxH: r2(it.h + (it.y - y) + 2), paras: parasOf(it) });
      } else if (it.k === 'path' || it.k === 'oval') pg.svg += svgOf(it);
    });
    return pg;
  }

  function fromLayout(board, deck, key) {
    if (!board || board.format !== 'fga-layout' || !board.pages) throw new Error('The board layout could not be read.');
    const fonts = JSON.stringify(board).slice(0, 200000);
    const P = { v: 'L1', built: key || '', real: true, base: '', ts: /Archivo Narrow|IBM Plex/.test(fonts) ? 'C' : 'A',
      name: board.title || 'Your project', ideas: [], altIdeas: [], capIdea: {}, raw: [], found: [], files: {} };
    P.short = P.name;
    P.slug = slug(P.name);
    P.board = page(Object.assign({ w: board.page.w, h: board.page.h }, board.pages[0]), 'board', 'board/', 0);
    P.board.w = board.page.w; P.board.h = board.page.h;
    P.slides = (deck && deck.pages ? deck.pages : []).map((lp, i) => { const pg = page(lp, 'slide', 'deck/', i + 1); pg.w = deck.page.w; pg.h = deck.page.h; return pg; });
    P.slideOrder = P.slides.map((s) => s.n);
    P.slideOff = [];
    return P;
  }
  const slug = (s) => String(s || 'studio-fga').toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 40) || 'studio-fga';

  /* ---------------------------------------------------------- the preview's plan -> a first sketch */
  const T = (id, name, x, y, w, maxH, paras, extra) => Object.assign({ id, name, x, y, w, h: null, valign: 'top', maxH, paras }, extra || {});
  const run = (t, role, fs, c) => ({ t: String(t || ''), role, fs, c: c || '#1D1D1B' });
  const KICK = '#6B6B68', ACC = '#C8603A';
  /* which drawings suit which slide, by the role the plan gave the slide and the use it gave each drawing */
  const SUITS = { brief: ['hero', 'render', 'concept'], intent: ['hero', 'render'], context: ['site'], setting: ['site'], site: ['site'], process: ['process', 'concept'],
    concept: ['concept', 'process'], idea: ['concept', 'process'], models: ['model'], model: ['model'], plan: ['plan'], section: ['section'], elevation: ['elevation', 'section'],
    axonometric: ['render', 'model'], structure: ['section', 'model'], diagram: ['concept', 'section', 'plan'], views: ['render', 'hero'], render: ['render', 'hero'],
    detail: ['detail'], precedent: ['reference'], closing: ['render', 'hero'] };

  function fromPlan(edit, plan, card, dims) {
    plan = plan || {}; card = card || {};
    const pics = (edit.pictures || []).filter((p) => p.on !== false && p.thumb);
    const heroPic = pics.find((p) => p.id === edit.hero) || pics[0];
    const others = pics.filter((p) => p !== heroPic).slice(0, 15);
    const title = card.project_title || plan.project_name || 'Your project';
    const capOf = (p) => { const c = p.caption || {}; return [{ lh: 1.3, after: 0, align: 'left', runs: [run(c.title || p.label || '', 'captionTitle', 8)] }].concat(c.line || c.short ? [{ lh: 1.3, after: 0, align: 'left', runs: [run(c.line || c.short, 'captionText', 8, KICK)] }] : []); };
    const content = (p, id, home) => { const d = dims[p.thumb] || [4, 3]; return { id, src: p.thumb, iw: d[0], ih: d[1], alt: p.label || '', home, view: { z: 1, cx: 0.5, cy: 0.5 }, cap: capOf(p), labels: [], scales: [], norths: [] }; };
    /* board: the hero across two columns, the concept, story and ideas beside it, then the rest in rows */
    const B = { kind: 'board', w: 594, h: 841, slots: [], contents: {}, texts: [], deco: [], svg: '' };
    const addSlot = (pg, p, id, x, y, w, h, capBelow) => {
      const home = { x, y, w, h };
      pg.slots.push({ id, x, y, w, h, cap: capBelow ? { x, y: y + h + 2, w, h: null, maxH: 14 } : null, content: id });
      pg.contents[id] = content(p, id, home);
    };
    if (heroPic) addSlot(B, heroPic, 'b-hero', 20, 64, 366.67, 176, true);
    const rows = Math.max(1, Math.ceil(others.length / 3)), top0 = 262, bottom = 818, gap = 9;
    const rowH = (bottom - top0 - gap * (rows - 1)) / rows;
    for (let r = 0; r < rows; r++) {
      const inRow = others.slice(r * 3, r * 3 + 3), k = inRow.length;
      inRow.forEach((p, j) => { const w = (554 - 8 * (k - 1)) / k; addSlot(B, p, 'b-p' + (r * 3 + j), 20 + j * (w + 8), top0 + r * (rowH + gap), w, rowH - 17, true); });
    }
    const rowsInfo = [[card.unbranded ? null : (card.pro ? 'Architect' : 'Student'), card.name], ['Project', title], ['Location', card.project_location], ['Program', card.program]]
      .filter((r) => r[0] && r[1]).map(([k, v]) => ({ k, v, ph: false }));
    B.texts.push(T('b-title', 'title', 20, 18.5, 413.5, 43.5, [{ lh: 1, after: 3.2, align: 'left', runs: [run(title, 'title', 60)] }, { lh: 1.32, after: 0, align: 'left', runs: [run(edit.subtitle || plan.subtitle, 'lead', 17)] }]));
    B.texts.push({ id: 'b-info', name: 'info', kind: 'info', x: 441.5, y: 21, w: 132.5, h: null, rows: rowsInfo, maxH: 41 });
    B.texts.push(T('b-concept', 'concept', 394.67, 63, 179.33, 50, [{ lh: 1, after: 2.6, align: 'left', runs: [run('Concept', 'kicker', 8, KICK)] }, { lh: 1.32, after: 0, align: 'left', runs: [run(edit.concept || plan.concept, 'lead', 12)] }]));
    B.texts.push(T('b-story', 'story', 394.67, 116, 179.33, 58, [{ lh: 1, after: 2.6, align: 'left', runs: [run('The story', 'kicker', 8, KICK)] }, { lh: 1.5, after: 0, align: 'left', runs: [run(edit.story || plan.story, 'body', 9, '#3B3B39')] }]));
    B.texts.push(T('b-ideas', 'ideas', 394.67, 178, 179.33, 80, [{ lh: 1, after: 2.6, align: 'left', runs: [run('Ideas', 'kicker', 8, KICK)] }]));
    /* deck: a cover, then one slide per slide in the plan */
    const W = 338.667, H = 190.5, slides = [];
    const cover = { kind: 'slide', n: 0, w: W, h: H, slots: [], contents: {}, deco: [], svg: '', texts: [
      T('s0-title', 'title', 223.78, 11, 98.89, 70, [{ lh: 1, after: 0, align: 'left', runs: [run(title, 'title', 34)] }]),
      T('s0-lead', 'lead', 223.78, 120, 98.89, 48, [{ lh: 1.32, after: 0, align: 'left', runs: [run(edit.subtitle || plan.subtitle, 'lead', 13)] }])] };
    if (heroPic) addSlot(cover, heroPic, 's0-hero', 16, 12, 202.78, 155.5, false);
    slides.push(cover);
    const used = new Set(heroPic ? [heroPic.id] : []);
    const pickFor = (role) => {
      const want = SUITS[String(role || '').toLowerCase()] || [];
      return pics.find((p) => !used.has(p.id) && want.includes(p.use)) || pics.find((p) => !used.has(p.id)) || heroPic;
    };
    const nAll = (edit.slides || []).length + 1;
    (edit.slides || []).forEach((sd) => {
      const n = sd.n, pg = { kind: 'slide', n, w: W, h: H, slots: [], contents: {}, deco: [], svg: '', texts: [
        T('s' + n + '-sec', 'section', 16, 12, 306.67, 6, [{ lh: 1, after: 0, align: 'left', runs: [run(String(n).padStart(2, '0') + '   ', 'kicker', 7.8, ACC), run(String(sd.label || '').toUpperCase(), 'kicker', 7.8, KICK)] }]),
        T('s' + n + '-head', 'headline', 16, 17, 306.67, 14, [{ lh: 1, after: 0, align: 'left', runs: [run(sd.title, 'title', 28)] }]),
        T('s' + n + '-lead', 'lead', 16, 32, 254.72, 12, [{ lh: 1.32, after: 0, align: 'left', runs: [run(sd.lead, 'lead', 13)] }]),
        T('s' + n + '-foot', 'footer', 262.67, 181.9, 60, 5, [{ lh: 1, after: 0, align: 'right', runs: [run('1 / ' + nAll, 'small', 7, '#A3A3A0')] }])] };
      const p = pickFor(sd.role);
      if (p) { used.add(p.id); addSlot(pg, p, 's' + n + '-pic', 16, 48, 306.67, 128, false); }
      slides.push(pg);
    });
    const ideas = (edit.ideas || []).map((i) => ({ id: i.id, title: /[.!?]$/.test(i.title || '') ? i.title : (i.title || '') + '.', text: ' ' + (i.text || ''), short: i.text, proof: i.proof, on: i.on !== false }));
    return { v: 'V1', real: true, preview: true, base: '', ts: (plan.text_style === 'C' ? 'C' : 'A'), name: title, short: title, slug: slug(title),
      board: B, slides, ideas, altIdeas: [], capIdea: {}, raw: [], found: [], files: {},
      slideOrder: [0].concat(edit.slideOrder || (edit.slides || []).map((s) => s.n)), slideOff: (edit.slideOff || []).slice(),
      slideMeta: (edit.slides || []).reduce((m, s) => { m[s.n] = s; return m; }, {}) };
  }

  /* when the status has no "edit" yet (an older server): the same shape, made from the plan itself */
  function editFromPlan(plan) {
    plan = plan || {};
    const pics = (plan.panels || []).map((p) => ({ id: p.panel, label: p.title || (p.caption || {}).title, kind: p.kind, file: p.file, use: p.use, on: p.use !== 'drop', protected: false, caption: p.caption || {}, thumb: p.thumb }));
    const hero = plan.hero || ((plan.panels || []).find((p) => p.use === 'hero') || {}).panel;
    return { ideas: (plan.ideas || []).map((it, k) => ({ id: 'i' + (k + 1), title: it.tagline, text: it.line, proof: it.proof, on: true })), altIdeas: [], hero, pictures: pics,
      slides: (plan.slides || []).map((s, k) => Object.assign({}, s, { n: k + 1, required: false })), slideOrder: (plan.slides || []).map((s, k) => k + 1), slideOff: [],
      subtitle: plan.subtitle, concept: plan.concept, story: plan.story };
  }

  window.FGALayout = { fromLayout, fromPlan, editFromPlan, slug };
})();
