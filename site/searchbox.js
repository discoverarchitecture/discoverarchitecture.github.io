/* The box under the wall's search field (design canvas v37, owner's request 6 Nov 2026).
   As a student types: architects (black-and-white portrait, how many buildings), styles, types, cities and countries
   (with counts), the best buildings (photo, architect, place), and "See all". Empty, it offers searches to try and
   the visitor's own recent ones (kept only in their browser). Arrow keys, Enter and Escape work; on a phone it spans
   the screen under the field. Above the wall, a slim line shows how the search was read ("Museum · Japan", or the
   word a typo was taken for). Matching and ranking: site/search.js. */
(function () {
  'use strict';
  const DA = window.DA, S = window.FGASearch, input = document.getElementById('q');
  if (!DA || !S || !input) return;
  const esc = DA.esc, fold = S.fold;
  window.addEventListener('load', () => setTimeout(S.warm, 1500)); // index the wall once the page has settled
  const TRY = ['Brutalism', 'Tadao Ando', 'Museums in Japan', 'Concrete churches', 'Libraries', 'London', 'Zaha Hadid', '1960s houses'];
  const store = (fn, fallback) => { try { return fn(); } catch (e) { return fallback; } };
  const recent = () => store(() => JSON.parse(localStorage.getItem('recent-searches') || '[]'), []);
  const remember = v => {
    v = v.trim(); if (v.length < 2) return;
    const list = [v].concat(recent().filter(x => fold(x) !== fold(v))).slice(0, 5);
    store(() => localStorage.setItem('recent-searches', JSON.stringify(list)));
  };

  // Portraits by architect name (data/architects.js), and the architects with their own page (data/arch_pages.js).
  const faces = new Map();
  Object.values((window.ARCHITECTS || {}).people || {}).forEach(p => { if (p && p.thumb && p.name) faces.set(fold(p.name), p.thumb); });
  const PAGES = window.ARCH_PAGES || {};

  const box = document.createElement('div');
  box.className = 'qbox'; box.id = 'qbox'; box.hidden = true;
  box.setAttribute('role', 'listbox'); box.setAttribute('aria-label', 'Suggestions');
  document.body.appendChild(box);
  input.setAttribute('role', 'combobox');
  input.setAttribute('aria-autocomplete', 'list');
  input.setAttribute('aria-expanded', 'false');
  input.setAttribute('aria-controls', 'qbox');

  const ARROW = '<svg class="qgo" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  const CLOCK = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/></svg>';
  const GLASS = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6"/><path d="m20 20-4.5-4.5"/></svg>';
  let opts = [], active = -1, n = 0;
  const opt = (html, act, extra) => { const id = 'qo' + (n++); opts.push(id); return `<${extra && extra.href ? `a href="${esc(extra.href)}"` : 'button type="button"'} class="qrow${extra && extra.cls ? ' ' + extra.cls : ''}" role="option" id="${id}" data-act="${esc(act)}">${html}</${extra && extra.href ? 'a' : 'button'}>`; };
  const chip = (label, icon) => { const id = 'qo' + (n++); opts.push(id); return `<button type="button" class="qtry" role="option" id="${id}" data-act="try:${esc(label)}">${icon}${esc(label)}</button>`; };
  const head = t => `<p class="qhead">${t}</p>`;

  function draw() {
    opts = []; n = 0; active = -1;
    const v = input.value.trim();
    let html = '';
    if (!v) {
      const r = recent();
      if (r.length) html += head('Recent') + `<div class="qchips">${r.map(x => chip(x, CLOCK)).join('')}</div>`;
      html += head('Try') + `<div class="qchips">${TRY.map(x => chip(x, GLASS)).join('')}</div>`;
    } else {
      const s = S.suggest(v);
      if (s.fixed.length) html += `<p class="qfix">Showing results for <b>${esc(s.fixed.map(f => f.to).join(' '))}</b></p>`;
      if (s.architects.length) html += head('Architects') + s.architects.map(a => {
        const face = faces.get(fold(a.name)), slug = PAGES[a.name];
        const ini = a.name.split(/\s+/).map(w => w[0]).slice(0, 2).join('');
        return opt(`<span class="qface" data-ini="${esc(ini)}">${face ? `<img src="${esc(face)}" alt="" loading="lazy" onerror="this.replaceWith(this.parentNode.dataset.ini)">` : esc(a.name.split(/\s+/).map(w => w[0]).slice(0, 2).join(''))}</span>` +
          `<span class="qtext"><b>${esc(a.name)}</b><small>${a.n} ${a.n === 1 ? 'building' : 'buildings'}</small></span>${ARROW}`,
          'arch:' + a.name, slug ? { href: 'architects/' + slug + '/' } : null);
      }).join('');
      if (s.topics.length) html += head('Browse') + s.topics.map(t =>
        opt(`<span class="qkind">${esc(t.kind)}</span><span class="qtext"><b>${esc(t.label)}</b><small>${t.n} ${t.n === 1 ? 'building' : 'buildings'}</small></span>${ARROW}`,
          `topic:${t.key}:${t.value}`)).join('');
      if (s.buildings.length) html += head('Buildings') + s.buildings.map(b => {
        const im = b.images && b.images[0];
        const city = (b.place || '').split(',')[0];
        return opt(`<span class="qthumb">${im ? `<img src="${esc(im.thumb)}" alt="" loading="lazy">` : ''}</span>` +
          `<span class="qtext"><b>${esc(b.name)}</b><small>${esc([b.arch && b.arch[0], [city, b.year].filter(Boolean).join(', ')].filter(Boolean).join(' · '))}</small></span>`,
          'open:' + b.id);
      }).join('');
      html += s.total
        ? opt(`<span class="qtext"><b>See all ${s.total.toLocaleString('en')} ${s.total === 1 ? 'building' : 'buildings'}</b></span>${ARROW}`, 'all', { cls: 'qall' })
        : `<p class="qnone">Nothing for “${esc(v)}” yet.</p>` + head('Try') + `<div class="qchips">${TRY.slice(0, 6).map(x => chip(x, GLASS)).join('')}</div>`;
      if (!s.total) countNone(v);
    }
    box.innerHTML = html;
  }
  // A search that finds nothing tells us what students want and the wall lacks: counted once a visit, words only
  // (letters and digits, at most 40), never anything else typed. Privacy page: "What we count".
  const none = new Set();
  let noneTimer;
  function countNone(v) {
    clearTimeout(noneTimer);
    noneTimer = setTimeout(() => {
      const words = v.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40);
      if (words.length < 3 || none.has(words) || input.value.trim() !== v) return;
      none.add(words);
      if (window.fgaEvent) window.fgaEvent('search/none/' + words, 'Search with no results');
    }, 2500);
  }

  function place() {
    const field = input.closest('.search') || input;
    const r = field.getBoundingClientRect();
    const vh = (window.visualViewport && window.visualViewport.height) || window.innerHeight;
    const top = Math.round(r.bottom + 8);
    box.style.top = top + 'px';
    box.style.maxHeight = Math.max(200, vh - top - 12) + 'px';
    if (window.innerWidth <= 640) { box.style.left = '12px'; box.style.right = '12px'; box.style.width = ''; }
    else {
      const w = Math.min(Math.max(r.width, 460), 640), left = Math.min(r.left, window.innerWidth - w - 16);
      box.style.left = Math.max(16, left) + 'px'; box.style.right = ''; box.style.width = w + 'px';
    }
  }
  function open() { draw(); place(); box.hidden = false; input.setAttribute('aria-expanded', 'true'); }
  function close() { box.hidden = true; input.setAttribute('aria-expanded', 'false'); input.removeAttribute('aria-activedescendant'); }
  function setActive(k) {
    if (!opts.length) return;
    active = (k + opts.length) % opts.length;
    opts.forEach((id, j) => document.getElementById(id).classList.toggle('on', j === active));
    const el = document.getElementById(opts[active]);
    input.setAttribute('aria-activedescendant', el.id);
    el.scrollIntoView({ block: 'nearest' });
  }
  const setQuery = v => { input.value = v; input.dispatchEvent(new Event('input', { bubbles: true })); };
  const toTop = () => window.scrollTo({ top: 0, behavior: 'smooth' });

  function act(a, el) {
    const v = input.value.trim();
    if (a.startsWith('try:')) { setQuery(a.slice(4)); remember(a.slice(4)); draw(); return; }
    if (v) remember(v);
    if (a.startsWith('open:')) { close(); DA.open(a.slice(5)); return; }
    if (a.startsWith('arch:')) {
      if (el && el.tagName === 'A') return; // the architect's own page
      close(); setQuery(''); DA.state.filters.arch.add(a.slice(5)); DA.apply(); toTop(); return;
    }
    if (a.startsWith('topic:')) {
      const [, key, ...rest] = a.split(':'), value = rest.join(':');
      close();
      if (key === 'city') { setQuery(value); input.blur(); toTop(); return; }
      setQuery(''); DA.state.filters[key].add(value); DA.apply(); toTop(); return;
    }
    close(); input.blur(); toTop(); // "See all"
  }

  let drawTimer;
  input.addEventListener('focus', open);
  input.addEventListener('input', () => { clearTimeout(drawTimer); drawTimer = setTimeout(() => { if (document.activeElement === input) open(); }, 90); });
  input.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown') { e.preventDefault(); if (box.hidden) open(); setActive(active + 1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(active - 1); }
    else if (e.key === 'Enter') {
      e.preventDefault();
      if (active >= 0) { const el = document.getElementById(opts[active]); el.click(); }
      else act('all');
    } else if (e.key === 'Escape') { if (!box.hidden) { e.stopPropagation(); close(); } }
  });
  box.addEventListener('pointerdown', e => e.preventDefault()); // keep the field focused while choosing
  box.addEventListener('click', e => { const el = e.target.closest('[data-act]'); if (el) act(el.dataset.act, el); });
  input.addEventListener('blur', () => setTimeout(() => { if (document.activeElement !== input) close(); }, 120));
  document.addEventListener('pointerdown', e => { if (!box.hidden && !box.contains(e.target) && e.target !== input) close(); });
  window.addEventListener('resize', () => { if (!box.hidden) place(); });
  window.addEventListener('scroll', () => { if (!box.hidden) place(); }, { passive: true });
  if (window.visualViewport) window.visualViewport.addEventListener('resize', () => { if (!box.hidden) place(); });

  /* ---------- above the wall: how the search was read, and help when nothing is found ---------- */
  const note = document.createElement('div');
  note.className = 'qnote'; note.id = 'qnote'; note.hidden = true;
  const cols = document.getElementById('cols');
  cols.parentNode.insertBefore(note, cols);
  const empty = document.getElementById('empty');
  const emptyTry = document.createElement('span');
  emptyTry.className = 'etry';
  if (empty) empty.appendChild(emptyTry);
  note.addEventListener('click', e => {
    const x = e.target.closest('[data-drop]');
    if (!x) return;
    const drop = fold(x.dataset.drop), left = fold(input.value).split(' ');
    const k = left.join(' ').indexOf(drop);
    setQuery(k < 0 ? input.value : (left.join(' ').slice(0, k) + left.join(' ').slice(k + drop.length)).replace(/\s+/g, ' ').trim());
  });
  emptyTry.addEventListener('click', e => { const x = e.target.closest('[data-try]'); if (x) setQuery(x.dataset.try); });
  document.addEventListener('da:render', () => setTimeout(() => {
    const q = DA.state.q && DA.state.mode === 'buildings' ? DA.state.q : '';
    const r = q ? S.run(q) : null;
    const parts = [];
    if (r && r.chips.length) parts.push(r.chips.map(c => `<span class="qchip"><small>${esc(c.kind)}</small>${esc(c.label)}<button type="button" data-drop="${esc(c.word)}" aria-label="Remove ${esc(c.label)}">×</button></span>`).join(''));
    if (r && r.fixed.length) parts.push(`<span class="qfixed">Showing results for <b>${esc(r.fixed.map(f => f.to).join(' '))}</b></span>`);
    note.innerHTML = parts.join('');
    note.hidden = !parts.length;
    emptyTry.innerHTML = q ? ' Or try ' + TRY.slice(0, 4).map(t => `<button type="button" data-try="${esc(t)}">${esc(t)}</button>`).join(', ') + '.' : '';
  }, 0));
})();
