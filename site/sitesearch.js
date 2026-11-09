/* The search box on every page outside the wall: building, architect, hub, guide, A-Z and policy pages (the slim
   bar's field, #tq). The same box as the wall's (design canvas v37, approved 6 Nov 2026): the first time the field is
   used it loads data/search_index.js (one short row per building, made by build_pages.py) and search.js, then offers
   architects, styles, types, cities, buildings and searches to try. Every row is a link: a building opens its own
   page, an architect their page, a style, type, city or idea its hub page (else the wall's search for it), and Enter or
   "See all" the wall's search, as the field did before. Searches that find nothing are counted (search/none/...). */
(function () {
  'use strict';
  const me = document.currentScript;
  const ROOT = me ? me.src.replace(/sitesearch\.js.*$/, '') : '/';
  const input = document.getElementById('tq');
  if (!input) return;
  const form = input.form;
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const TRY = ['Brutalism', 'Tadao Ando', 'Museums in Japan', 'Concrete churches', 'Libraries', 'London', 'Zaha Hadid', '1960s houses'];
  const store = (fn, fallback) => { try { return fn(); } catch (e) { return fallback; } };
  const recent = () => store(() => JSON.parse(localStorage.getItem('recent-searches') || '[]'), []);
  const remember = v => {
    v = v.trim(); if (v.length < 2) return;
    const f = x => x.toLowerCase();
    store(() => localStorage.setItem('recent-searches', JSON.stringify([v].concat(recent().filter(x => f(x) !== f(v))).slice(0, 5))));
  };
  const add = (tag, attrs) => new Promise((res, rej) => { const el = document.createElement(tag); Object.assign(el, attrs); el.onload = res; el.onerror = rej; document.head.appendChild(el); });

  let X = null, loading = null;
  function load() {
    if (loading) return loading;
    add('link', { rel: 'stylesheet', href: ROOT + 'search.css' }).catch(() => {});
    loading = add('script', { src: ROOT + 'data/search_index.js' }).then(() => {
      X = window.SEARCH_INDEX;
      const W = X.w, FIX = { UK: 'GB', 'Hong Kong': 'HK' };
      window.WORLD = window.WORLD || { names: X.countries };
      window.SEARCH_ALL = X.b.map(r => {
        const c = (r[3] || '').split(', ').pop(), arch = r[2] ? r[2].split('|') : [];
        const thumb = typeof r[11] === 'number' ? `images/${r[0]}/thumbs/${r[11]}.webp` : r[11] === 'd' ? `images/${r[0]}/drawing.svg` : r[11];
        return { id: r[0], name: r[1], arch, by: arch.join(', '), place: r[3], year: r[4] || String(r[5] || ''), y: r[5], type: W[r[6]],
          movement: W[r[7]], region: W[r[8]], concepts: r[9].map(k => W[k]), n: r[10], country: FIX[c] || c, thumb };
      });
      return add('script', { src: ROOT + 'search.js' });
    });
    return loading;
  }
  const S = () => window.FGASearch;
  const url = p => /^https?:/.test(p) ? p : ROOT + p;
  const wallSearch = v => ROOT + '?q=' + encodeURIComponent(v);

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
  const row = (html, href, cls) => { const id = 'qo' + (n++); opts.push(id); return `<a class="qrow${cls ? ' ' + cls : ''}" role="option" id="${id}" href="${esc(href)}">${html}</a>`; };
  const chip = (label, icon) => { const id = 'qo' + (n++); opts.push(id); return `<button type="button" class="qtry" role="option" id="${id}" data-try="${esc(label)}">${icon}${esc(label)}</button>`; };
  const head = t => `<p class="qhead">${t}</p>`;
  const count = k => `${k} ${k === 1 ? 'building' : 'buildings'}`;

  let none = new Set();
  function draw() {
    opts = []; n = 0; active = -1;
    const v = input.value.trim();
    let html = '';
    if (!v || !S()) {
      const r = recent();
      if (r.length) html += head('Recent') + `<div class="qchips">${r.map(x => chip(x, CLOCK)).join('')}</div>`;
      html += head('Try') + `<div class="qchips">${TRY.map(x => chip(x, GLASS)).join('')}</div>`;
      box.innerHTML = html;
      return;
    }
    const s = S().suggest(v);
    if (s.fixed.length) html += `<p class="qfix">Showing results for <b>${esc(s.fixed.map(f => f.to).join(' '))}</b></p>`;
    if (s.architects.length) html += head('Architects') + s.architects.map(a => {
      const face = X.faces[a.name], slug = X.pages[a.name];
      const ini = a.name.split(/\s+/).map(w => w[0]).slice(0, 2).join('');
      return row(`<span class="qface" data-ini="${esc(ini)}">${face ? `<img src="${esc(face)}" alt="" loading="lazy" onerror="this.replaceWith(this.parentNode.dataset.ini)">` : esc(ini)}</span>` +
        `<span class="qtext"><b>${esc(a.name)}</b><small>${count(a.n)}</small></span>${ARROW}`,
        slug ? ROOT + 'architects/' + slug + '/' : wallSearch(a.name));
    }).join('');
    if (s.topics.length) html += head('Browse') + s.topics.map(t => {
      const hub = X.hubs[t.key + ':' + t.value];
      return row(`<span class="qkind">${esc(t.kind)}</span><span class="qtext"><b>${esc(t.label)}</b><small>${count(t.n)}</small></span>${ARROW}`,
        hub ? ROOT + hub : wallSearch(t.label));
    }).join('');
    if (s.buildings.length) html += head('Buildings') + s.buildings.map(b => {
      const city = (b.place || '').split(',')[0];
      return row(`<span class="qthumb">${b.thumb ? `<img src="${esc(url(b.thumb))}" alt="" loading="lazy">` : ''}</span>` +
        `<span class="qtext"><b>${esc(b.name)}</b><small>${esc([b.arch[0], [city, b.year].filter(Boolean).join(', ')].filter(Boolean).join(' · '))}</small></span>`,
        ROOT + 'buildings/' + b.id + '/');
    }).join('');
    if (s.total) html += row(`<span class="qtext"><b>See all ${s.total.toLocaleString('en')} ${s.total === 1 ? 'building' : 'buildings'}</b></span>${ARROW}`, wallSearch(v), 'qall');
    else {
      html += `<p class="qnone">Nothing for “${esc(v)}” yet.</p>` + head('Try') + `<div class="qchips">${TRY.slice(0, 6).map(x => chip(x, GLASS)).join('')}</div>`;
      countNone(v);
    }
    box.innerHTML = html;
  }
  // A search that finds nothing tells us what students want and the wall lacks: counted once a visit, words only.
  let noneTimer;
  function countNone(v) {
    clearTimeout(noneTimer);
    noneTimer = setTimeout(() => {
      const words = v.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40);
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

  input.addEventListener('focus', () => { open(); load().then(() => { if (document.activeElement === input) open(); }).catch(() => {}); });
  let drawTimer;
  input.addEventListener('input', () => { clearTimeout(drawTimer); drawTimer = setTimeout(() => { if (document.activeElement === input) open(); }, 90); });
  input.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown') { e.preventDefault(); if (box.hidden) open(); setActive(active + 1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(active - 1); }
    else if (e.key === 'Enter' && active >= 0) { e.preventDefault(); document.getElementById(opts[active]).click(); }
    else if (e.key === 'Escape') close();
  });
  if (form) form.addEventListener('submit', () => remember(input.value)); // Enter: the wall's search, as before
  box.addEventListener('pointerdown', e => e.preventDefault()); // keep the field focused while choosing; links still open
  box.addEventListener('click', e => {
    const t = e.target.closest('[data-try]');
    if (t) { input.value = t.dataset.try; remember(t.dataset.try); input.focus(); open(); return; }
    if (e.target.closest('a')) remember(input.value);
  });
  input.addEventListener('blur', () => setTimeout(() => { if (document.activeElement !== input) close(); }, 150));
  window.addEventListener('resize', () => { if (!box.hidden) place(); });
  window.addEventListener('scroll', () => { if (!box.hidden) place(); }, { passive: true });
  if (window.visualViewport) window.visualViewport.addEventListener('resize', () => { if (!box.hidden) place(); });
})();
