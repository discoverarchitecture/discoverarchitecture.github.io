"""Hub pages: findgreatarchitecture.com/styles/<slug>/, /types/, /cities/, /ideas/ (owner's decision, 20 Oct 2026; brief in tools/hubs/BRIEF.md, part C).

A hub gathers the buildings on the wall that share a style, a building type, a city or an idea, where Google can rank them
("brutalist architecture examples", "architecture in Chicago"). A hub page is an architect page (tools/architect_pages.py,
site/architect.css, design v24 option B) with these differences: the buildings sit in four columns on a computer (two on a
phone), the best-documented buildings come first, and "On the globe" opens the globe fitted to the hub.

Inputs (nothing is typed per hub here):
  tools/hubs/hubs.json              the list: kind, slug, label, match rule, h1, title_words
  tools/hubs/results/intros_*.json  approved introductions (Opus writer chat); a hub without one says nothing invented: its h1,
                                    buildings and links only, and it is noindex and left out of the sitemap
  tools/hubs/sources.json           overview_links per hub (checked pages about the whole subject), optional
  tools/books_seed.json via books.js, tools/pageviews.json (the tie-break for the order)
Called from build_pages.main(); `bp` is the build_pages module.
"""
import json
import re
from collections import Counter
from pathlib import Path

import architect_pages as ap

ROOT = Path(__file__).resolve().parent.parent
HUBS = ROOT / 'tools' / 'hubs'
KINDS = {  # kind -> (folder, singular, plural)
    'style': ('styles', 'Style', 'Styles'),
    'type': ('types', 'Building type', 'Building types'),
    'city': ('cities', 'City', 'Cities'),
    'idea': ('ideas', 'Idea', 'Ideas'),
}
INIT = 48        # tiles written into the page; the rest are drawn from the page's own data as you scroll
IDEA_CHIPS = 9
COLS = 4


def kind_url(kind):
    return KINDS[kind][0] + '/'


def load_hubs():
    return json.loads((HUBS / 'hubs.json').read_text())['hubs']


def load_intros():
    """slug -> {intro, meta, ...} for every approved introduction; a later file wins."""
    out = {}
    for f in sorted((HUBS / 'results').glob('intros_*.json')) if (HUBS / 'results').exists() else []:
        for r in json.loads(f.read_text()):
            if not r.get('skip') and (r.get('intro') or '').strip():
                out[r['slug']] = r
    return out


def load_sources():
    f = HUBS / 'sources.json'
    return {r['slug']: r for r in json.loads(f.read_text())} if f.exists() else {}


def matches(bp, h, b):
    m = h['match']
    if 'movement' in m:
        return b['movement'] == m['movement']
    if 'type' in m:
        return b['type'] == m['type']
    if 'city' in m:
        return bp.place_full(b) == m['city']
    return m['concept'] in (b.get('concepts') or [])


def score(bp, b, arch, pv):
    """What the building's own page offers (owner, 20 Oct 2026): photos up to 8, a drawing link, an About summary, an
    architect page, links up to 10 (halved), map coordinates. Ties go to the more looked-up building."""
    s = min(8, len(b.get('images') or []))
    s += 3 if bp.has_drawings(b) else 0
    s += 2 if b.get('about') else 0
    s += 2 if any(n in arch for n in (bp.NM.list(b['by']) if bp.NM else [])) else 0
    s += min(10, len(b.get('links') or [])) / 2
    s += 1 if b.get('coords') else 0
    return (s, pv.get(b['id'], 0))


def plan(bp, items, arch):
    """The hubs, each with its buildings best first: [{kind, slug, label, h1, url, path, buildings, intro, sources}]."""
    pv = json.loads((ROOT / 'tools' / 'pageviews.json').read_text()) if (ROOT / 'tools' / 'pageviews.json').exists() else {}
    intros, sources = load_intros(), load_sources()
    out = []
    for h in load_hubs():
        bs = sorted((b for b in items if matches(bp, h, b)), key=lambda b: score(bp, b, arch, pv), reverse=True)
        if not bs:
            continue
        path = f'{kind_url(h["kind"])}{h["slug"]}/'
        out.append({**h, 'path': path, 'url': bp.BASE + path, 'buildings': bs, 'intro': intros.get(h['slug']), 'sources': sources.get(h['slug']) or {}})
    return out


def lookup(hubs):
    """(kind, value) -> hub, for the links in from building pages: ('style', 'Brutalism'), ('type', 'Museum'),
    ('idea', 'Adaptive reuse'), ('city', 'London, United Kingdom')."""
    out = {}
    for h in hubs:
        m = h['match']
        out[(h['kind'], m.get('movement') or m.get('type') or m.get('city') or m.get('concept'))] = h
    return out


def globe_data(bp, hubs):
    """data/hubs.js: what the wall needs to fit the globe to a hub (#map=style:brutalism). The wall's own filters do the
    rest; a city is a list of the places (as the wall writes them) because the wall has no city filter."""
    out = {}
    for h in hubs:
        m = h['match']
        key = f'{h["kind"]}:{h["slug"]}'
        if 'movement' in m:
            out[key] = {'movement': m['movement']}
        elif 'type' in m:
            out[key] = {'type': m['type']}
        elif 'concept' in m:
            out[key] = {'concepts': m['concept']}
        else:
            out[key] = {'places': sorted({b['place'] for b in h['buildings']})}
    return out


# ---------- the left pane ----------

def link_names(bp, text, buildings, up):
    """Escape a paragraph and link the first mention of each building named exactly as the wall names it (longest names first)."""
    spans = []
    for b in sorted(buildings, key=lambda b: -len(b['name'])):
        if len(b['name']) < 5:
            continue
        m = re.search(r'(?<![\w])' + re.escape(b['name']) + r'(?![\w])', text)
        if m and not any(m.start() < e and s < m.end() for s, e, _ in spans):
            spans.append((m.start(), m.end(), b['id']))
    out, at = [], 0
    for s, e, i in sorted(spans):
        out += [bp.e(text[at:s]), f'<a href="{up}buildings/{i}/">{bp.e(text[s:e])}</a>']
        at = e
    return ''.join(out) + bp.e(text[at:])


def related(hubs, h, n=6):
    """Other hubs whose buildings overlap most (a city's neighbours in its own country first)."""
    mine = {b['id'] for b in h['buildings']}
    country = h['match'].get('city', '').rsplit(', ', 1)[-1]
    def key(o):
        shared = len(mine & {b['id'] for b in o['buildings']})
        near = h['kind'] == 'city' and o['kind'] == 'city' and o['match']['city'].endswith(country)
        return (near, shared / ((len(mine) * len(o['buildings'])) ** 0.5 or 1))
    pool = [o for o in hubs if o is not h and len(mine & {b['id'] for b in o['buildings']}) >= 3]
    return sorted(pool, key=key, reverse=True)[:n]


def books_for(h, books):
    """Books whose buildings are on this hub, or whose tags name it (Brutalism, Museums, Timber...), best match first."""
    ids = {b['id'] for b in h['buildings']}
    m = h['match']
    norm = lambda s: re.sub(r's$', '', s.lower().replace('-', ' ').strip())
    names = {norm(v) for v in (h['label'], m.get('movement'), m.get('type'), m.get('concept'), (m.get('city') or '').split(',')[0]) if v}
    if h['kind'] == 'type' and h['slug'] == 'houses':
        names.add('house')
    scored = []
    for k in books:
        hit = len(ids & set(k.get('buildings') or []))
        tag = any(norm(t) in names for t in k.get('tags') or [])
        if hit or tag:
            scored.append((tag * 3 + hit, -(k.get('y') or 0), k))
    return [k for _, _, k in sorted(scored, key=lambda x: (-x[0], x[1]))[:6]]


# ---------- the right pane's script: sort, idea chips, more tiles as you scroll, photos that flip ----------

SCRIPT = """<script>
(function () {
  var data = JSON.parse(document.getElementById('hubdata').textContent), cols = [].slice.call(document.querySelectorAll('.wallpane .col'));
  var wrap = document.querySelector('.wallpane .cols'), count = document.getElementById('shown'), more = document.getElementById('more');
  var st = { sort: 'b', idea: '', shown: 0 }, swiped = false, MAXD = 6, STEP = 48, n = innerWidth >= 700 ? 4 : 2, heights = [], list = data.slice(), placed = 0;
  var by = { b: function (a, b) { return a.o - b.o; },
             y: function (a, b) { return a.y - b.y || a.n.localeCompare(b.n); },
             n: function (a, b) { return a.n.localeCompare(b.n); },
             c: function (a, b) { return a.c.localeCompare(b.c) || a.y - b.y; } };
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function tall(d) { return d.r + 0.06 + (d.sw && d.th.length > 1 ? 0.08 : 0); }
  function dots(k, total) {
    var shown = Math.min(total, MAXD), at = Math.min(k, shown - 1), out = '';
    for (var j = 0; j < shown; j++) out += '<i class="' + (j === at ? 'on' : '') + (total > MAXD && j === shown - 1 && at < shown - 1 ? ' sm' : '') + '"></i>';
    return '<span class="dots" aria-hidden="true">' + out + '</span>';
  }
  function src(s) { return /^https?:/.test(s) ? s : '../../' + s; }
  function tile(d) {
    var m = d.th.length, sw = d.sw && m > 1, el = document.createElement('div');
    el.className = 't' + (sw ? ' sw' : '') + (m > 1 ? ' sx' : '');
    el.dataset.id = d.id; el.dataset.k = 0; el.style.aspectRatio = '1/' + d.r.toFixed(3);
    el.innerHTML = '<a class="open" href="../../buildings/' + d.id + '/" aria-label="' + esc(d.n + ', ' + d.by + ', ' + d.yr + ', ' + d.c) + '">' +
      (m ? '<img src="' + esc(src(d.th[0])) + '" width="' + d.w + '" height="' + d.h + '" loading="lazy" decoding="async" alt="">' : '<span class="slot">No free photos yet</span>') + '</a>' +
      (m > 1 ? '<button type="button" class="flip prev" aria-label="Previous photo"><svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg></button><button type="button" class="flip next" aria-label="Next photo"><svg viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg></button>' : '') +
      (sw ? dots(0, m) : '') + '<span class="cap" aria-hidden="true"><b>' + esc(d.n) + '</b><span class="r2">' + esc(d.yr) + ' · ' + esc(d.c) + '</span></span>';
    el.hubd = d;
    return el;
  }
  function put(d, el) { var k = heights.indexOf(Math.min.apply(null, heights)); cols[k].appendChild(el || tile(d)); heights[k] += tall(d); }
  function layout() {
    cols.forEach(function (c, i) { while (c.firstChild) c.removeChild(c.firstChild); c.hidden = i >= n; });
    heights = cols.slice(0, n).map(function () { return 0; });
    list = data.filter(function (d) { return !st.idea || d.i.indexOf(st.idea) > -1; }).sort(by[st.sort]);
    placed = 0;
    draw(Math.max(INIT, st.shown));
    if (count) count.textContent = list.length;
  }
  var INIT = STEP;
  function draw(upto) { while (placed < list.length && placed < upto) put(list[placed++]); st.shown = placed; more.hidden = placed >= list.length; }
  // The page arrives with the best tiles already written in four columns; on a phone they are dealt again into two.
  if (n === 4) {
    cols.forEach(function (c) { [].forEach.call(c.children, function (el) { el.hubd = data.filter(function (d) { return d.id === el.dataset.id; })[0]; }); });
    heights = cols.map(function (c) { return [].reduce.call(c.children, function (s, el) { return s + tall(el.hubd); }, 0); });
    placed = cols.reduce(function (s, c) { return s + c.children.length; }, 0); st.shown = placed; more.hidden = placed >= list.length;
  } else { layout(); }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) { if (e[0].isIntersecting) draw(placed + STEP); }, { rootMargin: '1400px 0px' }).observe(more);
  } else { draw(data.length); }
  [].forEach.call(document.querySelectorAll('[data-sort]'), function (b) {
    b.addEventListener('click', function () {
      st.sort = b.dataset.sort; st.shown = 0;
      [].forEach.call(document.querySelectorAll('[data-sort]'), function (x) { x.setAttribute('aria-pressed', x === b); });
      layout();
    });
  });
  [].forEach.call(document.querySelectorAll('[data-idea]'), function (b) {
    b.addEventListener('click', function () {
      var on = b.getAttribute('aria-pressed') === 'true';
      [].forEach.call(document.querySelectorAll('[data-idea]'), function (x) { x.setAttribute('aria-pressed', 'false'); });
      st.idea = on ? '' : b.dataset.idea; st.shown = 0;
      if (!on) b.setAttribute('aria-pressed', 'true');
      layout();
    });
  });
  function flip(t, dir) {
    var d = t.hubd, m = d.th.length, k = ((+t.dataset.k || 0) + dir + m) % m, o = t.querySelector('.dots');
    t.dataset.k = k;
    t.querySelector('.open img').src = src(d.th[k]);
    if (o) o.outerHTML = dots(k, m);
  }
  // Delegated, so tiles drawn later work too. A tap opens the building as a popup over the wall; closing it returns here.
  var x0 = null, y0 = 0;
  wrap.addEventListener('click', function (e) {
    var f = e.target.closest('.flip'), t = e.target.closest('.t');
    if (f && t) { e.stopPropagation(); flip(t, f.classList.contains('next') ? 1 : -1); return; }
    var o = e.target.closest('.open');
    if (!o || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return;
    e.preventDefault();
    if (swiped) return;
    try { sessionStorage.setItem('da-from-arch', location.pathname); } catch (x) { /* fine without it */ }
    location.href = '../../#' + t.dataset.id;
  });
  wrap.addEventListener('pointerdown', function (e) { x0 = e.clientX; y0 = e.clientY; });
  wrap.addEventListener('pointerup', function (e) {
    var t = e.target.closest('.t'), dx = e.clientX - x0;
    if (t && t.hubd && t.hubd.th.length > 1 && x0 != null && Math.abs(dx) > 30 && Math.abs(dx) > Math.abs(e.clientY - y0)) {
      swiped = true; flip(t, dx < 0 ? 1 : -1); setTimeout(function () { swiped = false; }, 400);
    }
    x0 = null;
  });
  wrap.addEventListener('pointercancel', function () { x0 = null; });
})();
</script>"""

GLOBE = ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
         '<path d="M3 12h18M12 3c2.6 2.8 3.8 5.8 3.8 9s-1.2 6.2-3.8 9c-2.6-2.8-3.8-5.8-3.8-9S9.4 5.8 12 3z"/></svg>')


def title_for(bp, h):
    n = len(h['buildings'])
    words = h['title_words']
    short = words.split(':')[0]  # "Religious architecture: churches, mosques and temples" -> "Religious architecture"
    for w in dict.fromkeys((words, short)):
        for o in (f'{w}: {n} buildings with photos & plans', f'{w}: {n} buildings & photos', f'{w}: {n} buildings'):
            if len(o) <= bp.TITLE_MAX:
                return o
    return h['h1'][:bp.TITLE_MAX]


def desc_for(bp, h):
    if h['intro'] and h['intro'].get('meta'):
        return h['intro']['meta']
    n = len(h['buildings'])
    return f'{n} {h["label"]} buildings on Find Great Architecture, with free credited photos and links to plans and articles.'[:bp.DESC_MAX]


def tile_data(bp, b, o, swipe):
    ims = b.get('images') or []
    im = ims[0] if ims else {}
    return {'o': o, 'id': b['id'], 'n': b['name'], 'by': b['by'], 'yr': b['year'], 'y': b.get('y') or 0, 'c': b['place'].split(',')[0],
            'i': b.get('concepts') or [], 'r': round(ap.ratio_of(b), 3), 'sw': 1 if swipe else 0,
            'w': im.get('w', 4), 'h': im.get('h', 3), 'th': [i['thumb'] for i in ims[:8]]}


def page(bp, hubs, h, ctx):
    up = '../../'
    bs, kind = h['buildings'], h['kind']
    n = len(bs)
    intro = h['intro']
    url = h['url']
    title, desc = title_for(bp, h), desc_for(bp, h)
    swipe = ctx['swipe']
    # the intro: first paragraph always visible, the rest behind "Read more"; building names link to their pages
    paras = [p.strip() for p in re.split(r'\n\s*\n', intro['intro'].strip()) if p.strip()] if intro else []
    pool = bs
    body_intro = ''
    if paras:
        more = (f'<details class="more"><summary><span class="m">Read more</span><span class="l">Show less</span></summary>'
                f'{"".join(f"<p>{link_names(bp, p, pool, up)}</p>" for p in paras[1:])}</details>' if len(paras) > 1 else '')
        body_intro = f'<div class="bio"><p>{link_names(bp, paras[0], pool, up)}</p>{more}</div>'
    links = ap.links_block(bp, f'Read about {h["label"]}', ap.merge_links(ctx['reading'].get(f'hub:{kind}:{h["slug"]}'), ap.usable_links(h['sources'])), h['label'], up)
    bk = ''.join(
        f'<a class="bk" href="{up}#book:{bp.e(b["id"])}"><span class="cv">' +
        (f'<img src="{bp.e(bp.at(up, b["cover"]["thumb"]))}" alt="" loading="lazy" width="78" height="117">' if b.get('cover') and b['cover'].get('thumb')
         else f'<span class="standin">{bp.e(b["title"].split(":")[0])}</span>') +
        f'</span><span class="bt">{bp.e(b["title"])}<small>{bp.e(b["by"])}, {bp.e(b["year"])}</small></span></a>' for b in books_for(h, ctx['books']))
    books = f'<section class="blk"><h2>Books to read</h2><div class="books">{bk}</div></section>' if bk else ''
    rel = related(hubs, h)
    relh = (f'<section class="blk"><h2>Related</h2><p class="sim">' + ' · '.join(f'<a href="{up}{o["path"]}">{bp.e(o["label"])}</a>' for o in rel) + '</p></section>') if rel else ''
    globe = f'<a class="globe-link" href="{up}#map={kind}:{h["slug"]}">{GLOBE}<span>On the globe</span><small>See where they are</small></a>'
    ideas = Counter(c for b in bs for c in b.get('concepts') or [] if c != h['match'].get('concept'))
    chips = ''.join(f'<button type="button" class="chip" data-idea="{bp.e(c)}" aria-pressed="false">{bp.e(c)} <span>{k}</span></button>'
                    for c, k in ideas.most_common(IDEA_CHIPS) if k >= 3)
    kw = f'<div class="ideas" role="group" aria-label="Narrow by idea">{chips}</div>' if chips else ''
    first = bs[:INIT]
    tiles = [ap.tile(bp, b, up, b['id'] in swipe) for b in first]
    grid = ap.deal(tiles, [ap.tile_height(b, b['id'] in swipe) for b in first], COLS)
    data = [tile_data(bp, b, i, b['id'] in swipe) for i, b in enumerate(bs)]
    data_json = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    sorts = ''.join(f'<button type="button" class="chip" data-sort="{k}" aria-pressed="{str(k == "b").lower()}">{t}</button>'
                    for k, t in (('b', 'Best first'), ('y', 'Year'), ('n', 'A to Z'), ('c', 'Place')))
    ld = [{'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': h['h1'], 'url': url, 'description': desc, 'inLanguage': 'en',
           'isPartOf': {'@type': 'WebSite', 'name': bp.NAME, 'url': bp.BASE},
           'mainEntity': {'@type': 'ItemList', 'name': h['h1'], 'numberOfItems': n,
                          'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f'{bp.BASE}buildings/{b["id"]}/', 'name': b['name']} for i, b in enumerate(bs[:20])]}},
          {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
              {'@type': 'ListItem', 'position': 1, 'name': KINDS[kind][2], 'item': bp.BASE + kind_url(kind)},
              {'@type': 'ListItem', 'position': 2, 'name': h['label'], 'item': url}]}]
    extra = (('' if intro else '<meta name="robots" content="noindex,follow">\n')
             + f'<link rel="stylesheet" href="{up}architect.css?v={bp.fingerprint(bp.SITE / "architect.css")}">\n'
             + f'<link rel="stylesheet" href="{up}hub.css?v={bp.fingerprint(bp.SITE / "hub.css")}">\n'
             + '\n'.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld))
    og = bp.at(bp.BASE, bs[0]['images'][0]['thumb']) if bs[0].get('images') else bp.BASE + 'og.jpg'
    head = bp.HEAD.format(title=bp.e(title), desc=bp.e(desc), url=bp.e(url), site=bp.NAME, ogtype='website', ogtitle=bp.e(h['h1']),
                          image=bp.e(og), up=up, wallhash='', extra=extra, total=bp.TOTAL, css_v=bp.CSS_V)
    body = (
        f'<main class="arch hub">\n'
        f'<aside class="rail noport"><p class="kicker">{KINDS[kind][1]}</p>'
        f'<h1>{bp.e(h["h1"])}</h1><p class="facts">{n} buildings</p>'
        f'{body_intro}'
        f'<a class="cta" href="#buildings">See the {n} buildings ↓</a>'
        f'{globe}{links}{books}{relh}</aside>\n'
        f'<section class="wallpane" id="buildings"><div class="whead"><h2>Buildings <span><span id="shown">{n}</span></span></h2>'
        f'<div class="sorts"><span>Sort</span>{sorts}</div></div>{kw}'
        f'<div class="cols">{grid}</div><div id="more" aria-hidden="true"></div>'
        f'<footer class="foot" data-nosnippet><p>Photos are public domain or Creative Commons, credited under each photo and sourced from Wikimedia Commons.</p>'
        f'<p><a href="{up}">Find Great Architecture</a> · <a href="{up}{kind_url(kind)}">{KINDS[kind][2]}</a> · <a href="{up}buildings/">All buildings</a></p>{bp.legal_foot(up)}</footer></section>\n'
        f'</main>\n'
        f'<script type="application/json" id="hubdata">{data_json}</script>\n'
        f'{bp.DOCK.format(up=up)}\n'
        f'{SCRIPT}\n</body>\n</html>\n')
    return head + body


def index_page(bp, hubs, kind):
    up = '../'
    mine = [h for h in hubs if h['kind'] == kind]
    plural = KINDS[kind][2]
    lede = {'style': 'Architectural styles and movements on the wall, each with its best-documented buildings first.',
            'type': 'Building types on the wall, from museums to memorials, each with its best-documented buildings first.',
            'city': 'Cities on the wall and the buildings they hold, each with its best-documented buildings first.',
            'idea': 'Ideas that run through the buildings on the wall, such as courtyards and cantilevers, with examples.'}[kind]
    published = any(h['intro'] for h in mine)
    head = bp.HEAD.format(title=f'{plural} in architecture · {bp.NAME}', desc=bp.e(lede), url=bp.BASE + kind_url(kind), site=bp.NAME, ogtype='website',
                          ogtitle=f'{plural} in architecture', image=bp.BASE + 'og.jpg', up=up, wallhash='',
                          extra='' if published else '<meta name="robots" content="noindex,follow">', total=bp.TOTAL, css_v=bp.CSS_V)
    rows = ''.join(f'<a href="{h["slug"]}/"><b>{bp.e(h["label"])}</b><small>{len(h["buildings"])} buildings</small></a>' for h in mine)
    body = f'<main class="index"><h1>{plural}</h1><p class="lede">{bp.e(lede)}</p><div class="names">{rows}</div></main>\n'
    return head + body + bp.FOOT.format(up=up, total=bp.TOTAL, css_v=bp.CSS_V)


def build(bp, hubs):
    """Write site/<kind folder>/<slug>/index.html for every hub and an index page per kind; remove pages left over from earlier runs."""
    import worth_swipe
    ctx = {'swipe': set(worth_swipe.chosen()), 'books': bp.read_js('books.js', 'BOOKS') or [], 'reading': ap.load_reading()}
    for kind, (folder, _, _) in KINDS.items():
        out = bp.SITE / folder
        out.mkdir(exist_ok=True)
        keep = set()
        for h in hubs:
            if h['kind'] != kind:
                continue
            d = out / h['slug']
            d.mkdir(exist_ok=True)
            (d / 'index.html').write_text(page(bp, hubs, h, ctx))
            keep.add(h['slug'])
        (out / 'index.html').write_text(index_page(bp, hubs, kind))
        for d in out.iterdir():
            if d.is_dir() and d.name not in keep:
                for f in d.iterdir():
                    f.unlink()
                d.rmdir()
    (bp.SITE / 'data' / 'hubs.js').write_text('// What the globe needs to fit a hub (#map=style:brutalism). Made by tools/build_pages.py from tools/hubs/hubs.json.\n'
                                              'window.HUBS = ' + json.dumps(globe_data(bp, hubs), ensure_ascii=False, sort_keys=True) + ';\n')
