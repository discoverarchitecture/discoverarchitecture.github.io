/* Search for the wall and the globe: window.FGASearch (owner's request, 6 Nov 2026).
   Students type the way they talk ("brutalist museums in london", "gugenheim", "flw", "1960s houses in japan"):
   - every word must be found at the START of a word in the building's name, architect, city, country, type, style,
     ideas, year or Key features, so "ando" finds Tadao Ando and no longer "Gando";
   - plurals and "-ist" words meet their root (museums: museum, brutalist: brutalism), US and UK spellings meet
     (theater, theatre), and nicknames, old city names and nationalities are understood (nyc, bombay, japanese);
   - a word nothing has is read as the nearest real one (one letter off, two for long words): "gugenheim";
   - small words (in, of, the, by, buildings, photos...) are optional;
   - words that name a type, style, country, city or decade are read as that and shown as chips;
   - results are ranked: the name first, then the architect, then place, type and style, then the Key features text,
     and among equals the wall's own order (n: the first hundred are the curated best-known, later ones added by renown).
   Reads the buildings app.js has prepared (window.DA.ALL, with .arch and .country); builds its index on first use. */
(function () {
  'use strict';
  const fold = s => String(s == null ? '' : s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/&/g, ' and ').replace(/['’.]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
  const words = s => { const f = fold(s); return f ? f.split(' ') : []; };
  const phrase = s => words(s).filter(w => !STOP.has(w)).map(stem); // what a label or alias means, word by word

  const SPELL = { theater: 'theatre', center: 'centre', color: 'colour', gray: 'grey', jewelry: 'jewellery', honor: 'honour' };
  function stem(w) {
    if (SPELL[w]) return SPELL[w];
    if (/^\d/.test(w)) return w;
    if (w.length > 4 && w.endsWith('ies')) w = w.slice(0, -3) + 'y';
    else if (w.length > 4 && /(ch|sh|ss|x|z)es$/.test(w)) w = w.slice(0, -2);
    else if (w.length > 3 && w.endsWith('s') && !/(ss|us|is|os)$/.test(w)) w = w.slice(0, -1);
    if (w.length > 6 && w.endsWith('ist')) w = w.slice(0, -3) + 'ism';
    return SPELL[w] || w;
  }

  // A word typed, and what else it can mean. The word itself always counts too.
  const ALIAS = {
    nyc: ['new york'], ny: ['new york'], la: ['los angeles'], sf: ['san francisco'], dc: ['washington'],
    st: ['saint'], saint: ['st'], mt: ['mount'],
    uk: ['united kingdom'], gb: ['united kingdom'], britain: ['united kingdom'], england: ['united kingdom'],
    scotland: ['united kingdom'], wales: ['united kingdom'], british: ['united kingdom'], english: ['united kingdom'],
    scottish: ['united kingdom'], us: ['united states'], usa: ['united states'], america: ['united states', 'americas'],
    american: ['united states', 'americas'], uae: ['united arab emirates'], emirati: ['united arab emirates'],
    holland: ['netherlands'], turkey: ['turkiye'], turkish: ['turkiye'], korea: ['south korea'], korean: ['south korea'],
    czech: ['czechia'], persian: ['iran'], iranian: ['iran'],
    bombay: ['mumbai'], madras: ['chennai'], calcutta: ['kolkata'], bangalore: ['bengaluru'], peking: ['beijing'],
    munchen: ['munich'], firenze: ['florence'], venezia: ['venice'], roma: ['rome'], lisboa: ['lisbon'], wien: ['vienna'],
    praha: ['prague'], kobenhavn: ['copenhagen'], koln: ['cologne'],
    japanese: ['japan'], chinese: ['china'], indian: ['india'], french: ['france'], german: ['germany'], italian: ['italy'],
    spanish: ['spain'], portuguese: ['portugal'], dutch: ['netherlands'], swiss: ['switzerland'], danish: ['denmark'],
    swedish: ['sweden'], norwegian: ['norway'], finnish: ['finland'], mexican: ['mexico'], brazilian: ['brazil'],
    chilean: ['chile'], argentine: ['argentina'], argentinian: ['argentina'], colombian: ['colombia'], peruvian: ['peru'],
    australian: ['australia'], canadian: ['canada'], austrian: ['austria'], belgian: ['belgium'], irish: ['ireland'],
    greek: ['greece'], israeli: ['israel'], egyptian: ['egypt'], russian: ['russia'], polish: ['poland'],
    pakistani: ['pakistan'], bangladeshi: ['bangladesh'], sri: ['sri lanka'], lankan: ['sri lanka'], nepali: ['nepal'],
    vietnamese: ['vietnam'], thai: ['thailand'], indonesian: ['indonesia'], singaporean: ['singapore'],
    african: ['africa'], european: ['europe'], asian: ['east asia', 'south asia', 'southeast asia'],
    scandinavian: ['denmark', 'sweden', 'norway'], nordic: ['denmark', 'sweden', 'norway', 'finland', 'iceland'],
    flw: ['frank lloyd wright'], corb: ['corbusier'], corbu: ['corbusier'], lc: ['corbusier'], hdm: ['herzog'],
    som: ['skidmore'], kpf: ['kohn pedersen fox'], big: ['bjarke ingels'], rem: ['koolhaas'], zha: ['zaha hadid'],
    bv: ['doshi'], decon: ['deconstructivism'], hightech: ['high tech'], postmodern: ['postmodernism'],
    skyscraper: ['office and tower'], highrise: ['office and tower'], hotel: ['hospitality'], hospital: ['health'],
    sacred: ['religious'], worship: ['religious'], spiritual: ['religious'],
  };
  const STOP = new Set(('a an the in of on at by for with from to near and or famous best great iconic top building ' +
    'architecture architectural architect architects work works project projects photo picture image plan drawing ' +
    'example design designed').split(' '));
  const DECADE_WORDS = { twenties: 1920, thirties: 1930, forties: 1940, fifties: 1950, sixties: 1960, seventies: 1970,
    eighties: 1980, nineties: 1990 };

  // Where a word is found, and what it is worth there.
  const FIELDS = [['name', 10], ['by', 10], ['city', 6], ['country', 6], ['type', 6], ['movement', 6], ['concepts', 4],
    ['region', 3], ['year', 4], ['study', 1]];

  let ALL = [], people = [], vocab = [], post = new Map(), strong = new Map(), facets = [], built = false;
  const countryName = code => (window.WORLD && window.WORLD.names[code]) || '';

  // The index is made in small pieces while the page is idle (warm), so the first key pressed never waits;
  // a search that comes sooner finishes it at once (build).
  let done = 0;
  const add = (word, i, wt, isStrong) => {
    let m = post.get(word);
    if (!m) post.set(word, m = new Map());
    if ((m.get(i) || 0) < wt) m.set(i, wt);
    if (isStrong) strong.set(word, (strong.get(word) || 0) + 1);
  };
  function indexOne(b, i) {
    b._si = i;
    const city = (b.place || '').split(',')[0];
    const text = {
      name: b.name, by: [b.by].concat(b.arch || []).join(' '), city, country: countryName(b.country) + ' ' + (b.country || ''),
      type: b.type, movement: b.movement, concepts: (b.concepts || []).join(' '), region: b.region,
      year: [b.year, b.y ? Math.floor(b.y / 10) * 10 + 's' : ''].join(' '), study: b.study,
    };
    b._name = fold(b.name);
    b._ns = words(b.name).map(stem);
    for (const [f, wt] of FIELDS) for (const w of words(text[f])) add(stem(w), i, wt, wt >= 4);
  }
  const start = () => { if (!ALL.length) ALL = (window.DA && window.DA.ALL) || window.BUILDINGS || []; };
  function warm() {
    if (built) return;
    start();
    const t0 = Date.now();
    while (done < ALL.length && Date.now() - t0 < 12) { indexOne(ALL[done], done); done++; }
    if (done < ALL.length) (window.requestIdleCallback || (f => setTimeout(f, 30)))(warm);
    else build();
  }
  function build() {
    if (built) return;
    start();
    for (; done < ALL.length; done++) indexOne(ALL[done], done);
    vocab = [...post.keys()].sort();
    const names = new Map(); ALL.forEach(b => (b.arch || []).forEach(a => names.set(a, (names.get(a) || 0) + 1)));
    names.forEach((n, a) => { if (n >= 2) people.push(words(a)); });
    // What a word can be read as: a type, style, country or city (with a few buildings), each with its count.
    const count = (key, val) => { const m = new Map(); ALL.forEach(b => { const v = val(b); if (v) m.set(v, (m.get(v) || 0) + 1); }); return m; };
    const seen = new Map();
    const push = (kind, key, value, label, n) => {
      const w = phrase(label), id = kind + ':' + w.join(' ');
      if (seen.has(id)) { seen.get(id).n += n; return; } // Montreal and Montréal are one city
      const f = { kind, key, value, label, n, w };
      seen.set(id, f); facets.push(f);
    };
    count('type', b => b.type).forEach((n, v) => push('Type', 'type', v, v, n));
    count('movement', b => b.movement).forEach((n, v) => push('Style', 'movement', v, v, n));
    count('country', b => b.country).forEach((n, v) => countryName(v) && push('Country', 'country', v, countryName(v), n));
    count('city', b => (b.place || '').split(',')[0]).forEach((n, v) => n >= 2 && push('City', 'city', v, v, n));
    const ideas = new Map(); ALL.forEach(b => (b.concepts || []).forEach(c => ideas.set(c, (ideas.get(c) || 0) + 1)));
    ideas.forEach((n, v) => push('Idea', 'concepts', v, v, n));
    facets = facets.filter(f => f.w.length);
    built = true;
  }

  // Every vocabulary word starting with p (binary search on the sorted list).
  function withPrefix(p) {
    let lo = 0, hi = vocab.length;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (vocab[mid] < p) lo = mid + 1; else hi = mid; }
    const out = [];
    for (let k = lo; k < vocab.length && vocab[k].startsWith(p); k++) out.push(vocab[k]);
    return out;
  }
  // How many edits apart two words are, up to max (then max + 1).
  function edits(a, b, max) {
    if (Math.abs(a.length - b.length) > max) return max + 1;
    let prev2 = null, prev = Array.from({ length: b.length + 1 }, (_, j) => j);
    for (let i = 1; i <= a.length; i++) {
      const cur = [i]; let low = i;
      for (let j = 1; j <= b.length; j++) {
        let v = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
        if (prev2 && i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) v = Math.min(v, prev2[j - 2] + 1);
        cur.push(v); if (v < low) low = v;
      }
      if (low > max) return max + 1;
      prev2 = prev; prev = cur;
    }
    return prev[b.length];
  }
  function nearest(w) {
    const max = w.length >= 8 ? 2 : 1;
    let best = null, bestD = max + 1, bestN = 0;
    for (const [v, n] of strong) {
      if (v.length < 4 || v[0] !== w[0] && max === 1) continue;
      const d = edits(w, v, max);
      if (d < bestD || (d === bestD && n > bestN)) { best = v; bestD = d; bestN = n; }
    }
    return best;
  }

  // The buildings one stemmed word finds, with the best weight each: whole words count fully, beginnings of words less.
  function hitsFor(w, prefixOk) {
    const out = new Map();
    const take = (word, k) => { const m = post.get(word); if (m) m.forEach((wt, i) => { const s = wt * k; if ((out.get(i) || 0) < s) out.set(i, s); }); };
    take(w, 1);
    // half-typed words: the same small weight in every field, so "lond" means London more than a bank's name
    if (prefixOk && w.length >= 3) for (const v of withPrefix(w)) if (v !== w) { const m = post.get(v); m.forEach((wt, i) => { const s = Math.min(wt, 6) * 0.6; if ((out.get(i) || 0) < s) out.set(i, s); }); }
    return out;
  }
  // A phrase ("new york", "frank lloyd wright"): every word must be there.
  function hitsForPhrase(ws, prefixLast) {
    let acc = null;
    ws.forEach((w, k) => {
      const h = hitsFor(stem(w), prefixLast && k === ws.length - 1 || w.length >= 4);
      if (!acc) { acc = h; return; }
      const next = new Map();
      acc.forEach((s, i) => { if (h.has(i)) next.set(i, s + h.get(i)); });
      acc = next;
    });
    if (acc) acc.forEach((s, i) => acc.set(i, s / ws.length));
    return acc || new Map();
  }

  // Read the query: chips for what it names, groups of words that must all be found, optional words.
  function parse(raw) {
    build();
    let ws = words(raw);
    const chips = [], groups = [], optional = [], fixed = [];
    // decades and centuries
    for (let k = 0; k < ws.length; k++) {
      const w = ws[k];
      let from = null, to = null;
      if (/^(1[0-9]|20)\d0s$/.test(w)) { from = +w.slice(0, 4); to = from + 9; }
      else if (/^\d0s$/.test(w)) { const d = +w.slice(0, 2); from = (d <= 20 ? 2000 : 1900) + d; if (d === 20) from = 1920; to = from + 9; }
      else if (DECADE_WORDS[w]) { from = DECADE_WORDS[w]; to = from + 9; }
      else if (/^(\d{1,2})(st|nd|rd|th)$/.test(w) && ws[k + 1] === 'century') { const c = parseInt(w, 10); from = (c - 1) * 100; to = from + 99; ws.splice(k + 1, 1); }
      if (from !== null) {
        chips.push({ kind: 'Years', label: to - from === 9 ? from + 's' : ws[k] + ' century', word: ws[k] });
        groups.push({ test: b => b.y >= from && b.y <= to, wt: 5 });
        ws.splice(k, 1); k--;
      }
    }
    // the longest run of words that names a type, style, country or city
    const sw = ws.map(stem);
    const used = new Array(ws.length).fill(false);
    const exp = ws.map(w => (ALIAS[w] || []).map(a => phrase(a).join(' ')));
    for (let len = 3; len >= 1; len--) {
      for (let k = 0; k + len <= ws.length; k++) {
        if (used.slice(k, k + len).some(Boolean)) continue;
        const run = sw.slice(k, k + len).join(' ');
        const alt = len === 1 ? exp[k] : [];
        const f = facets.filter(x => x.kind !== 'Idea').find(x => x.w.join(' ') === run) ||
          (alt.length === 1 && facets.filter(x => x.kind !== 'Idea').find(x => x.w.join(' ') === alt[0]));
        if (!f) continue;
        for (let j = k; j < k + len; j++) used[j] = true;
        chips.push({ kind: f.kind, label: f.label, word: ws.slice(k, k + len).join(' ') });
        const fw = f.w;
        const inName = b => fw.every(w => b._ns.some(x => x === w || (w.length >= 3 && x.startsWith(w))));
        const city = fold(f.value);
        const test = f.key === 'city' ? b => fold((b.place || '').split(',')[0]) === city : b => b[f.key] === f.value;
        groups.push({ test, inName, wt: 10 });
      }
    }
    // the remaining words
    ws.forEach((w, k) => {
      if (used[k]) return;
      const last = k === ws.length - 1;
      const alts = [[w]].concat((ALIAS[w] || []).map(a => a.split(' ')));
      let hits = new Map();
      for (const a of alts) {
        const h = a.length === 1 ? hitsFor(stem(a[0]), last || a[0].length >= 4) : hitsForPhrase(a, last);
        h.forEach((s, i) => { if ((hits.get(i) || 0) < s) hits.set(i, s); });
      }
      if (!hits.size && w.length >= 5 && /^[a-z]+$/.test(w)) {
        const near = nearest(stem(w));
        if (near) { hits = hitsFor(near, false); hits.forEach((s, i) => hits.set(i, s * 0.8)); fixed.push({ from: w, to: near }); }
      }
      if (STOP.has(w) || (w.length <= 2 && !ALIAS[w])) optional.push(hits);
      else groups.push({ hits });
    });
    if (!groups.length && optional.length) groups.push({ hits: optional.shift() });
    const q = ws.filter(w => !STOP.has(w)).join(' ');
    const person = q && people.some(nw => q.split(' ').every(w => nw.includes(w)) || ws.some(w => ALIAS[w] && ALIAS[w].some(a => a.split(' ').every(x => nw.includes(x)))));
    // one broad word ("house", "museums", "church"): the best-known first, not names that happen to start with it
    const broad = ws.length === 1 && (chips.length > 0 || (groups[0] && groups[0].hits && groups[0].hits.size > 30));
    return { chips, groups, optional, fixed, q: ws.join(' '), person, broad };
  }

  let last = null;
  function run(raw) {
    const key = fold(raw);
    if (last && last.key === key) return last;
    const p = parse(raw);
    const scores = new Map();
    if (p.groups.length) {
      ALL.forEach((b, i) => {
        let s = 0;
        for (const g of p.groups) {
          if (g.test) {
            if (g.test(b)) s += g.wt; else if (g.inName && g.inName(b)) s += 7; else return; // "Palais de Tokyo" is in Paris
          } else {
            const h = g.hits.get(i);
            if (!h) return;
            s += h;
          }
        }
        if (p.q) { // the building's own name typed: it comes first (unless the words are an architect's name)
          if (b._name === p.q) s += 100;
          else if (!p.person && !p.broad && (b._name + ' ').startsWith(p.q + ' ')) s += 40;
          else if (!p.person && !p.broad && (' ' + b._name + ' ').includes(' ' + p.q + ' ')) s += 20;
        }
        s += 3 / (1 + (b.n || 4000) / 300); // up to 3 for the best-known
        scores.set(i, s);
      });
    }
    const list = [...scores.keys()].sort((a, b) => scores.get(b) - scores.get(a) || (ALL[a].n || 0) - (ALL[b].n || 0)).map(i => ALL[i]);
    return (last = { key, scores, list, chips: p.chips, fixed: p.fixed });
  }

  // For the box under the search field: architects, topics and buildings that fit what is typed so far.
  function suggest(raw) {
    build();
    const ws = words(raw).filter(w => !STOP.has(w));
    if (!ws.length) return { architects: [], topics: [], buildings: [], total: 0, chips: [], fixed: [] };
    const res = run(raw);
    const fits = (nameWords, list) => list.every((w, k) => nameWords.some(n => n === w || ((k === list.length - 1 || w.length >= 3) && n.startsWith(w))));
    const qs = [ws].concat(ws.length === 1 && ALIAS[ws[0]] ? ALIAS[ws[0]].map(a => a.split(' ')) : []);
    if (res.fixed.length) qs.push(ws.map(w => (res.fixed.find(f => f.from === w) || {}).to || w));
    // architects, by how many of their buildings are on the wall
    const people = new Map();
    ALL.forEach(b => (b.arch || []).forEach(a => people.set(a, (people.get(a) || 0) + 1)));
    const architects = [];
    people.forEach((n, name) => { const nw = words(name); if (qs.some(q => fits(nw, q))) architects.push({ name, n }); });
    architects.sort((a, b) => b.n - a.n);
    const topics = facets.filter(f => qs.some(q => fits(f.w.concat(words(f.label)), q.map(stem)) || fits(words(f.label), q)))
      .sort((a, b) => b.n - a.n);
    return { architects: architects.slice(0, 3), topics: topics.slice(0, 4), buildings: res.list.slice(0, 5), total: res.list.length,
      chips: res.chips, fixed: res.fixed };
  }

  window.FGASearch = {
    fold, run, suggest, warm,
    has: (b, raw) => { const r = run(raw); return r.scores.has(b._si); },
    rank: (list, raw) => { const r = run(raw); return list.slice().sort((a, b) => (r.scores.get(b._si) || 0) - (r.scores.get(a._si) || 0) || (a.n || 0) - (b.n || 0)); },
  };
})();
