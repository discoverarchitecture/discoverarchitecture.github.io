#!/usr/bin/env python3
"""Build one static page per building, a building index, link previews, a sitemap and robots.txt.

  python3 tools/build_pages.py

Run it again whenever site/data/buildings.js or site/data/links.js changes. Pages are plain HTML (no JavaScript),
so search engines and link previews see everything. Output:
  site/buildings/<id>/index.html   one page per building, with its photo gallery
  site/buildings/index.html        A–Z list of all buildings
  site/og.jpg                      preview image for the home page
  site/sitemap.xml, site/robots.txt
  site/index.html                  the "About this wall" block between <!-- about:start --> and <!-- about:end -->

Page titles lead with the building and its architect, the way people search ("Casa Rotonda by Mario Botta"),
then say what the page has: "plans" appears only when a verified link leads to drawings. Pages with an entry in
site/data/summaries.js get an "About" section quoted from Wikipedia. tools/pageviews.json ranks the
buildings people look up most (Wikipedia pageviews, Oct 2025 to Sep 2026) for the home page's list.
"""
import html, json, os, random, re, textwrap, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
BASE = os.environ.get('SITE_URL', 'https://findgreatarchitecture.com/')
NAME = 'Find Great Architecture'

COUNTRY = {
    'US': 'United States', 'BD': 'Bangladesh', 'IN': 'India', 'JP': 'Japan', 'ES': 'Spain', 'DE': 'Germany',
    'CZ': 'Czech Republic', 'AU': 'Australia', 'UK': 'United Kingdom', 'CA': 'Canada', 'BR': 'Brazil',
    'FR': 'France', 'IT': 'Italy', 'CN': 'China', 'NL': 'Netherlands', 'FI': 'Finland', 'MX': 'Mexico',
    'DK': 'Denmark', 'PT': 'Portugal', 'CH': 'Switzerland', 'NO': 'Norway', 'TR': 'Türkiye', 'CL': 'Chile',
    'LK': 'Sri Lanka', 'VN': 'Vietnam', 'EG': 'Egypt', 'BF': 'Burkina Faso', 'ZA': 'South Africa',
    'AE': 'United Arab Emirates', 'AZ': 'Azerbaijan',
}
# Every other country by its two-letter code, from the world map's names (site/data/world.js); the list above wins.
try:
    _world = json.loads((SITE / 'data' / 'world.js').read_text().split('window.WORLD = ', 1)[1].rstrip().rstrip(';'))
    COUNTRY = {**next((v for v in _world.values() if isinstance(v, dict) and v.get('GB') == 'United Kingdom'), {}), **COUNTRY}
except (OSError, IndexError, ValueError):
    pass
# Buildings that no longer stand, so their pages say "was".
GONE = {'nakagin-capsule-tower': 'demolished in 2022'}

e = lambda s: html.escape(str(s or ''), quote=True)
q = lambda s: urllib.parse.quote(str(s))

TOTAL = '100'  # set from the data in main()
CSS_V = ''  # a short fingerprint of pages.css and the shared theme files, so browsers fetch them again when they change


def at(base, path):
    """Our own files are relative to the site; photos served by Wikimedia are full URLs."""
    return path if path.startswith('http') else base + path


def read_js(name, var):
    """A data file that sets window.<var> = {...}; missing file means {}."""
    path = SITE / 'data' / name
    return json.loads(path.read_text().split(f'window.{var} = ', 1)[1].rstrip().rstrip(';')) if path.exists() else {}


def load():
    text = (SITE / 'data' / 'buildings.js').read_text()
    items = json.loads(text.split('window.BUILDINGS = ', 1)[1].rstrip().rstrip(';'))
    found = read_js('links.js', 'LINKS')  # from tools/find_links.py
    about = read_js('summaries.js', 'SUMMARIES')  # from tools/fetch_summaries.py
    return [{**b, **found.get(b['id'], {}), **({'about': about[b['id']]} if b['id'] in about else {})} for b in items]


def place_full(b):
    parts = [p.strip() for p in b['place'].split(',')]
    if len(parts) >= 2 and parts[-1] in COUNTRY:
        return ', '.join(parts[:-1] + [COUNTRY[parts[-1]]])
    return b['place']


# Sites whose verified links lead to drawings, so a page may say "plans & sections" in its title.
DRAWING_SITES = {'WikiArquitectura', 'ArchDaily'}


def has_drawings(b):
    return any(l['site'] in DRAWING_SITES for l in (b.get('links') or []))


def anonymous(b):
    return b['by'].lower().startswith('unknown')


TITLE_MAX = 60   # Google cuts a title at about 580 px, roughly 60 characters
DESC_MAX = 155   # and a description at about 155


def lead(b):
    """The first architect named, for a title: 'Arthur Erickson (Erickson/Massey Architects)' -> 'Arthur Erickson',
    'Giuseppe Terragni, Pietro Lingeri' -> 'Giuseppe Terragni'. A firm of surnames ('McKim, Mead & White',
    'Skidmore, Owings & Merrill') stays whole. The full credit is on the page."""
    by = re.sub(r'\s*\(.*?\)', '', b['by'])
    firm = re.match(r"[A-Z][\w'’.-]+(?:, [A-Z][\w'’.-]+)+,? (?:&|and) [A-Z][\w'’.-]+\b", by)
    return firm.group(0) if firm else re.split(r',| and | & |;', by)[0].strip()


def title(b):
    """Villa Savoye by Le Corbusier, 1931: photos, plans & key features   (at most TITLE_MAX characters).
    Searches pair a building's name with its architect ("casa rotonda mario botta"), so "Name by Architect" comes first
    and is kept longest; then the year and what the page offers, each only when it fits. A long name loses its
    bracketed part before anything else."""
    name, year, who = b['name'], b['year'], lead(b)
    if not b.get('images'):
        full = short = 'plans & key features' if has_drawings(b) else 'key features'
    else:
        full, short = ('photos, plans & key features', 'photos & plans') if has_drawings(b) else ('photos & key features', 'photos')
    names = [name] + ([re.sub(r'\s*\(.*?\)', '', name)] if '(' in name else [])
    whos = [who] + ([re.split(r',| and | & ', who)[0]] if ',' in who else [])   # a long firm falls back to its first name
    options = []
    for n in names:
        for w in whos:
            by = '' if anonymous(b) else f' by {w}'
            options += ([f'{n}{by}, {year}: {full}'] if b.get('y') else []) + [f'{n}{by}: {full}', f'{n}{by}: {short}', f'{n}{by}']
        options.append(f'{n}: {short}')
    return next((o for o in options if len(o) <= TITLE_MAX), names[-1])


# How a typology starts the description's second sentence ("House in Stabio, Switzerland, 1982."). Types that would
# read wrongly for some of their buildings (a restaurant filed under Hospitality) say "Built 1958 in ..." instead.
KIND = {'House': 'House', 'Museum': 'Museum', 'Library': 'Library', 'Memorial': 'Memorial', 'Pavilion': 'Pavilion',
        'Palace': 'Palace', 'Housing': 'Housing', 'Religious': 'Religious building', 'Office & tower': 'Office building'}


def clause_cut(s, room):
    """Shortens a sentence to fit at a natural break (; : , —), and mid-sentence with "…" only when there is none."""
    if len(s) <= room:
        return s
    cut = max(s.rfind(c, 0, room) for c in (';', ':', ',', ' —', ' –'))
    if cut > room * 0.5:
        return s[:cut].rstrip()
    return s[:room - 1].rsplit(' ', 1)[0].rstrip(' ,;:-') + '…'


def summary(b):
    """The page description, at most DESC_MAX characters so Google shows all of it: the key features as a whole
    sentence, then where and when, then what the page offers. Parts are left out, never cut, until it fits."""
    study = ' '.join(b['study'].split()).rstrip('.')
    if not b.get('y'):  # no source gives a year: say where only
        where = f"{KIND[b['type']]} in {place_full(b)}" if b['type'] in KIND else f"In {place_full(b)}"
    else:
        where = f"{KIND[b['type']]} in {place_full(b)}, {b['year']}" if b['type'] in KIND else f"Built {b['year']} in {place_full(b)}"
    if b['id'] in GONE:
        where += f"; {GONE[b['id']]}"
    if b.get('images'):
        gives = 'Free credited photos, with links to plans and sections' if has_drawings(b) else 'Free credited photos'
        tails = [f'{gives} for a case study.', f'{gives}.', 'Free photos.', '']
    else:
        tails = ['Links to plans and sections for a case study.' if has_drawings(b) else 'Notes for a case study.', '']
    for w in (where + '. ', ''):
        for tail in tails:
            text = f'{study}. {w}{tail}'.strip()
            if len(text) <= DESC_MAX:
                return text
    room = DESC_MAX - len(where) - 3
    if room > 60:
        cut = clause_cut(study, room)
        return f"{cut}{'' if cut.endswith('…') else '.'} {where}."
    cut = clause_cut(study, DESC_MAX - 1)
    return cut if cut.endswith('…') else cut + '.'


def related(b, items, n=6):
    def score(x):
        shared = len(set(x['concepts']) & set(b['concepts']))
        s = shared * 2 + (1 if x['type'] == b['type'] else 0) + (2.5 if x['by'] == b['by'] else 0)
        return s + ((x['n'] * 13 + b['n'] * 7) % 17) / 100
    return sorted((x for x in items if x['id'] != b['id']), key=score, reverse=True)[:n]


# Without a verified page on one of these sites, the link opens that site's own search for the building.
CORE = [('Projects & drawings', 'ArchDaily', 'https://www.archdaily.com/search/projects?q='),
        ('Plans & sections', 'WikiArquitectura', 'https://en.wikiarquitectura.com/?s='),
        ('News & features', 'Dezeen', 'https://www.dezeen.com/?s=')]


def links(b):
    """(kind, site, url, direct): verified pages from tools/find_links.py, then the core sites' own search."""
    name, city, found = b['name'], b['place'].split(',')[0], b.get('links') or []
    out = [(l['kind'], l['site'], l['url'], True) for l in found]
    out += [(k, n, search + q(name), False) for k, n, search in CORE if not any(l['site'] == n for l in found)]
    commons = 'https://commons.wikimedia.org/wiki/' + q(b['commons'].replace(' ', '_')) if b.get('commons') else 'https://commons.wikimedia.org/w/index.php?search=' + q(name)
    return out + [
        ('Read', 'Wikipedia', b.get('wiki') or 'https://en.wikipedia.org/w/index.php?search=' + q(f'{name} {city}'), bool(b.get('wiki'))),
        ('Watch', 'YouTube', 'https://www.youtube.com/results?search_query=' + q(f"{name} {b['by']} architecture"), True),
        ('More photos', 'Wikimedia Commons', commons, True),
    ]


HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="{up}favicon.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="{up}apple-touch-icon.png">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="{site}">
<meta property="og:type" content="{ogtype}">
<meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700..900&family=Barlow:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Barlow+Condensed:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}theme.css?v={css_v}">
<script src="{up}theme.js?v={css_v}"></script>
<link rel="stylesheet" href="{up}pages.css?v={css_v}">
<link rel="stylesheet" href="{up}ai.css?v={css_v}">
<script src="{up}analytics.js"></script>
<script src="{up}rows.js?v={css_v}" defer></script>
<script src="{up}ai.js?v={css_v}" defer></script>
{extra}
</head>
<body>
{topbar}"""

# Thumbnails scroll the strip sideways rather than jumping the page to the anchor.
GALLERY_JS = """<script>
(function () {
  var g = document.currentScript.previousElementSibling, s = g.querySelector('.slides'), t = [].slice.call(g.querySelectorAll('.thumbs a'));
  function mark() { var k = Math.round(s.scrollLeft / s.clientWidth); t.forEach(function (a, i) { if (i === k) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); }); }
  t.forEach(function (a, i) { a.addEventListener('click', function (ev) { ev.preventDefault(); s.scrollTo({ left: i * s.clientWidth }); }); });
  s.addEventListener('scroll', function () { clearTimeout(s._m); s._m = setTimeout(mark, 60); }, { passive: true });
  mark();
})();
</script>"""

THEME_BTN = ('<button type="button" class="theme-btn" data-theme-toggle aria-label="Night view" aria-pressed="false">'
             '<svg class="moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>'
             '<svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button>')
# Every page has the wall's slim bar (search, Filter, night view, the games) and its dock (Home, Map, Surprise me).
# Search goes to the wall as /?q=…; Filter, Map and Surprise me land on the wall as #filter, #map and #surprise.
TOPBAR = """<header class="top" data-nosnippet>
  <a class="mark" href="{up}" aria-label="Find Great Architecture: back to the wall">A<span class="accent">.</span></a>
  <form class="search" action="{up}" method="get" role="search"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg><label class="sr" for="tq">Search buildings, architects, cities or ideas</label><input id="tq" type="search" name="q" placeholder="Search a building, architect, city or idea…" autocomplete="off" enterkeyhint="search"></form>
  <a class="tbtn fbtn" href="{up}#filter" aria-label="Filter"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M7 12h10M10 17h4"/></svg><span>Filter</span></a>
  {theme_btn}
  <a class="ai-btn ai-bar" href="{up}studio/?ref=page" aria-haspopup="dialog" aria-expanded="false">{ai_spark}<span class="ai-long">AI Jury Presentation Generator</span><span class="ai-short">AI</span></a>
  <div class="play"><button type="button" class="tbtn play-btn" aria-haspopup="menu" aria-expanded="false"><svg class="pi" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l12.5-7.5z"/></svg><span>Guess the building?</span><svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg></button>
    <div class="play-menu" role="menu" hidden><a role="menuitem" href="{up}play/#daily"><b>Daily five</b><span>Same five for everyone. New every day.</span></a><a role="menuitem" href="{up}play/#endless"><b>Endless</b><span>Keep going until you miss one.</span></a></div></div>
  <script>(function () { var p = document.currentScript.parentNode.querySelector('.play'), b = p.querySelector('button'), m = p.querySelector('.play-menu');
    function set(o) { m.hidden = !o; b.setAttribute('aria-expanded', o); }
    b.addEventListener('click', function (e) { e.stopPropagation(); set(m.hidden); });
    document.addEventListener('click', function (e) { if (!p.contains(e.target)) set(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') set(false); }); })();</script>
</header>
"""
# The AI jury presentation generator's spark (site/ai.css, site/ai.js): in every page's bar, so it is always in sight (owner, 24 Oct 2026).
AI_SPARK = ('<svg class="ai-spark" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5c.6 4.6 2.9 6.9 7.5 7.5-4.6.6-6.9 2.9-7.5 7.5-.6-4.6-2.9-6.9-7.5-7.5 4.6-.6 6.9-2.9 7.5-7.5z"/>'
            '<path d="M19 14.5c.3 2 1.3 3 3.3 3.3-2 .3-3 1.3-3.3 3.3-.3-2-1.3-3-3.3-3.3 2-.3 3-1.3 3.3-3.3z"/></svg>')
TOPBAR = TOPBAR.replace('{theme_btn}', THEME_BTN).replace('{ai_spark}', AI_SPARK)
DOCK = ('<nav class="dock" data-nosnippet aria-label="Browse"><a href="{up}">Home</a>'
        '<a class="map" href="{up}#map"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/></svg>Map</a>'
        '<a class="go" href="{up}#surprise">Surprise me</a></nav>')
HEAD = HEAD.replace('{topbar}', TOPBAR.replace('{', '{{').replace('}', '}}').replace('{{up}}', '{up}'))

# The legal links and who runs the site, at the foot of every page (owner, 21 Oct 2026, for the Dodo Payments review).
# The same lines are in architect_pages.py and hub_pages.py (through legal_foot), tools/studio/gen.py, site/index.html,
# site/play/index.html and the hand-written pages (terms, privacy, pricing, refunds, contact).
LEGAL = ('<p class="legal-links"><a href="{up}pricing/">Pricing</a> · <a href="{up}terms/">Terms</a> · '
         '<a href="{up}privacy/">Privacy</a> · <a href="{up}refunds/">Refunds</a> · <a href="{up}contact/">Contact</a></p>'
         '<p>Find Great Architecture · run by Akshat Pagaria · India</p>')


def legal_foot(up):
    return LEGAL.replace('{up}', up)


FOOT = """<footer class="foot" data-nosnippet>
  <p>Photos are public domain or Creative Commons, credited under each photo and sourced from Wikimedia Commons; a few historic drawings and photos come from the Art Institute of Chicago (public domain).</p>
  <p><a href="{up}">Find Great Architecture</a> · <a href="{up}buildings/">All buildings</a></p>
  <p><a href="{up}studio/?ref=footer">Studio FGA: make an architecture presentation board from your own drawings →</a></p>
  {legal}
</footer>
{dock}
</body>
</html>
"""
FOOT = FOOT.replace('{dock}', DOCK).replace('{legal}', LEGAL)


def about_block(b):
    """A short description quoted from Wikipedia (tools/fetch_summaries.py), credited and linked. Most pages have none."""
    a = b.get('about')
    if not a:
        return ''
    paras = ''.join(f'<p>{e(p)}</p>' for p in a['paragraphs'])
    return (f'<section class="block about"><h2>About {e(b["name"])}</h2>{paras}'
            f'<p class="src">Shortened from <a href="{e(a["url"])}" rel="noopener">Wikipedia</a>, '
            f'<a href="https://creativecommons.org/licenses/by-sa/4.0/" rel="noopener">CC BY-SA 4.0</a>.</p></section>\n')


def hub_links():
    """The hub pages by kind, for the home page's text block, so crawlers (and people without JavaScript) can reach them."""
    if not HUBS:
        return ''
    import hub_pages
    out = ''
    for kind, (folder, _, plural) in hub_pages.KINDS.items():
        mine = [h for h in HUBS if h['kind'] == kind]
        if mine:
            out += (f'  <h3><a href="{folder}/">{plural}</a></h3>\n  <p>' + ' · '.join(f'<a href="{h["path"]}">{e(h["label"])}</a>' for h in mine) + '</p>\n')
    return out


def home_block(items):
    """Crawler-readable text for the home page, which is otherwise drawn by JavaScript: what the wall is, and the
    twenty buildings people look up most (tools/pageviews.json). Written between the about:start/end markers."""
    pv = json.loads((ROOT / 'tools' / 'pageviews.json').read_text()) if (ROOT / 'tools' / 'pageviews.json').exists() else {}
    top = sorted((b for b in items if b['id'] in pv), key=lambda b: -pv[b['id']])[:20]
    places = sorted({COUNTRY.get(b['place'].split(', ')[-1], '') for b in items} - {''})
    row = lambda b: f'<li><a href="buildings/{b["id"]}/">{e(b["name"])}</a> <small>{e(b["place"].split(",")[0] if anonymous(b) else b["by"])}</small></li>'
    return (f'<section class="about-wall" id="about">\n'
            f'  <h2>About this wall</h2>\n'
            f'  <p>Find Great Architecture is a huge, growing wall of great buildings, curated for architects, architecture students '
            f'and anyone who loves buildings: the modern masters, contemporary and parametric work, brutalism and regionalism. '
            f'Wander it instead of searching. Every building has '
            f'free photos with credits, its key features, and links to plans, sections and articles for a case study. '
            f'Spin the globe to explore buildings from all over the world, <a href="buildings/">see them all A–Z</a>, '
            f'or test yourself with the <a href="play/">guess-the-building games</a>. '
            f'Short building videos on <a href="https://www.youtube.com/@findgreatarchitecture" rel="noopener">YouTube</a>.</p>\n'
            f'{hub_links()}'
            f'  <h3>Most looked-up buildings</h3>\n  <ol>{"".join(row(b) for b in top)}</ol>\n'
            f'  <div class="about-legal">{legal_foot("")}</div>\n'
            f'</section>')


def license_url(name):
    """Link to the licence text. Google's licensable-image markup wants a link, not the licence's name."""
    n = (name or '').strip()
    if n == 'CC0':
        return 'https://creativecommons.org/publicdomain/zero/1.0/'
    if n == 'Public domain':
        return 'https://creativecommons.org/publicdomain/mark/1.0/'
    m = re.match(r'^CC (BY|BY-SA) (\d\.\d)(?: ([a-z]+))?$', n)
    if not m:
        return ''
    return f'https://creativecommons.org/licenses/{m.group(1).lower()}/{m.group(2)}/' + (f'{m.group(3)}/' if m.group(3) else '')


# Commons descriptions that crept into captions: template boilerplate, file names, truncated scraps.
BOILERPLATE = re.compile(r"^this (is a |photo|picture|image)|identified (by|as) |\(Q\d+\)|uploaded via|wikimedia|file:|\.jpe?g|\.png|^img[_ ]?\d|^dsc"
                         r"|digital camera|^title:|more information|plus d.infos|immovable heritage|heritage monument|^[a-z]+-\d{4}$", re.I)
PHRASE = {'Exterior': 'exterior', 'Interior': 'interior', 'Context': 'seen in its setting', 'Detail': 'detail', 'Model': 'model',
          'Plan': 'plan', 'Elevation': 'elevation', 'Drawing': 'drawing'}


def photo_kind(im):
    return (im.get('caption') or '').split(' · ')[0].strip() or 'Photo'


def photo_note(im):
    """The useful part of a caption after its kind ('Exterior · The terrace of ...'), or '' when it is boilerplate."""
    note = ' '.join((im.get('caption') or '').partition(' · ')[2].split())
    return '' if len(note) < 4 or len(note) > 140 or BOILERPLATE.search(note) else note


def photo_caption(im):
    note = photo_note(im)
    return photo_kind(im) + (f' · {note}' if note else '')


def photo_alt(b, im):
    """Alt text for a photo: the building, its city, what the photo shows, and its own description when it has a good one."""
    alt = f"{b['name']}, {b['place'].split(',')[0]}: {PHRASE.get(photo_kind(im), photo_kind(im).lower())}"
    note = photo_note(im)
    return textwrap.shorten(alt + (f'. {note}' if note else ''), 125, placeholder='…')


def ld_image(b, im):
    """schema.org ImageObject with licence markup, so Google Images can show the photo as licensable."""
    credit, lic = (im.get('credit') or '').rstrip('.'), im.get('license') or ''
    credit = credit or 'Wikimedia Commons contributor'  # Google's licensable-image markup wants a creator on every photo
    d = {'@type': 'ImageObject', 'contentUrl': at(BASE, im['src']), 'name': f"{b['name']}: {photo_kind(im)}", 'caption': photo_alt(b, im),
         'width': im['w'], 'height': im['h'], 'creator': {'@type': 'Person', 'name': credit}, 'creditText': credit,
         'copyrightNotice': f'{credit}, {lic}' if lic else credit}
    if license_url(lic):
        d['license'] = license_url(lic)
    if im.get('source'):
        d['acquireLicensePage'] = im['source']
    return d


ARCH = {}  # canonical architect name -> page slug, filled in by main() before any page is written (tools/architect_pages.py)
NM = None  # names_py.Names, the same one-name-per-architect rule as the wall
HUBS = []  # the hub pages (tools/hub_pages.py), planned in main() before any page is written
HUBLOOK = {}  # (kind, value) -> hub, so building pages can link their style, type, city and ideas to a hub


def hub_href(kind, value, up):
    h = HUBLOOK.get((kind, value))
    return f'{up}{h["path"]}' if h else ''


def architect_html(b, up):
    """The building's credit as text, with the architect's own page linked when they have one."""
    text = e(b['by'])
    for n in (NM.list(b['by']) if NM else []):
        if n in ARCH:
            link = f'<a href="{up}architects/{ARCH[n]}/">{e(n)}</a>'
            return text.replace(e(n), link, 1) if e(n) in text else f'{text}<br>{link}: all buildings'
    return text


# The facts table: a small drawing to the left of each fact, on the same 24 x 24 grid as the filter's drawings;
# the architect's row shows their portrait (black and white) when there is a free one.
FACT_ART = {
    'Architect': '<circle cx="12" cy="8" r="4"/><path d="M4 21c1-4.5 4.5-7 8-7s7 2.5 8 7"/>',
    'Place': '<path d="M12 21s-7-6.5-7-12a7 7 0 0 1 14 0c0 5.5-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    'Year': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    'Typology': '<path d="M3 21h18M5 21V9l7-5 7 5v12M9 21v-6h6v6"/>',
    'Movement': '<path d="M3 12h4l3-7 4 14 3-7h4"/>',
    'Region': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.8 3.8 5.8 3.8 9s-1.2 6.2-3.8 9c-2.6-2.8-3.8-5.8-3.8-9S9.4 5.8 12 3z"/>',
}
PEOPLE = {}  # architects.js, read once by fact_icon
FILTER_ART = read_js('filters.js', 'FILTER_ART')  # the filter's drawings, for the building type


def fact_icon(k, b):
    if k == 'Architect':
        if not PEOPLE:
            PEOPLE.update(read_js('architects.js', 'ARCHITECTS') or {'people': {}, 'buildings': {}})
        for qid in PEOPLE.get('buildings', {}).get(b['id'], []):
            p = PEOPLE['people'].get(qid)
            if p and p.get('thumb'):
                return f'<img class="fi face" src="{e(p["thumb"])}" alt="" loading="lazy">'
    if k == 'Typology':
        d = (FILTER_ART.get('typeIcons') or {}).get(b['type'])
        if d:
            return f'<svg class="fi" viewBox="0 0 24 24" aria-hidden="true"><path d="{e(d)}"/></svg>'
    return f'<svg class="fi" viewBox="0 0 24 24" aria-hidden="true">{FACT_ART[k]}</svg>'


def facts_html(b, up):
    facts = [('Architect', b['by']), ('Place', place_full(b)), ('Year', b['year']), ('Typology', b['type']), ('Movement', b['movement']), ('Region', b['region'])]
    hubs = {'Place': hub_href('city', place_full(b), up), 'Typology': hub_href('type', b['type'], up), 'Movement': hub_href('style', b['movement'], up)}
    def cell(k, v):
        if k == 'Architect':
            return architect_html(b, up)
        return f'<a href="{hubs[k]}">{e(v)}</a>' if hubs.get(k) else e(v)
    return '<dl class="facts">' + ''.join(
        f'<div>{fact_icon(k, b)}<dt>{e(k)}</dt><dd>{cell(k, v)}</dd></div>' for k, v in facts) + '</dl>'


# ---------- the building page as the opened building from the wall (v27 · 02, approved 20 Oct 2026) ----------
# The same parts in the same order as the opened building on the wall: the portrait byline and the country map, the
# key features, three small "threads" (the game, the globe, an idea), photo rows of more buildings, then the links.
WORLD = {}
CODE_FIX = {'UK': 'GB', 'Hong Kong': 'HK'}
COUNTS = {}  # filled once per run: idea and type counts, buildings per architect


def country_of(b):
    c = b['place'].split(', ')[-1]
    return CODE_FIX.get(c, c)


def project(lat, lon):
    """Natural Earth I, the same as app.js and tools/make_world.py."""
    import math
    x0, sc, y0, top, bottom = WORLD['proj']
    ph = max(bottom, min(top, lat)) * math.pi / 180
    la = lon * math.pi / 180
    p2 = ph * ph
    p4 = p2 * p2
    x = la * (0.8707 - 0.131979 * p2 + p4 * (-0.013791 + p4 * (0.003971 * p2 - 0.001529 * p4)))
    y = ph * (1.007226 + p2 * (0.015085 + p4 * (-0.044475 + 0.028874 * p2 - 0.005916 * p4)))
    return [(x - x0) * sc, (y0 - y) * sc]


def fit_path(d, frame, u):
    """A country's outline cut to the map's frame and thinned to what shows at the map's size (about 190 px wide):
    points closer than a pixel are dropped, and each step is written in whole units from the last."""
    x0, y0, x1, y1 = frame
    out = []
    for ring in re.split(r'Z', d):
        nums = [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?', ring)]
        pts = list(zip(nums[0::2], nums[1::2]))
        for inside, cut in ((lambda p: p[0] >= x0, lambda a, b: (x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0]))),
                            (lambda p: p[0] <= x1, lambda a, b: (x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0]))),
                            (lambda p: p[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0)),
                            (lambda p: p[1] <= y1, lambda a, b: (a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1))):
            kept = []
            for i, cur in enumerate(pts):  # Sutherland-Hodgman, one edge of the frame at a time
                prev = pts[i - 1]
                if inside(cur):
                    if not inside(prev):
                        kept.append(cut(prev, cur))
                    kept.append(cur)
                elif inside(prev):
                    kept.append(cut(prev, cur))
            pts = kept
            if not pts:
                break
        thin = []
        for x, y in pts:
            x, y = round(x), round(y)
            if not thin or abs(x - thin[-1][0]) + abs(y - thin[-1][1]) >= max(1, u):
                thin.append((x, y))
        if len(thin) < 3:
            continue
        steps = ' '.join(f'{x - a} {y - b}' for (a, b), (x, y) in zip(thin, thin[1:]))
        out.append(f'M{thin[0][0]} {thin[0][1]}l{steps}z')
    return ''.join(out)


def where_html(b, up):
    """The small country map beside the byline, framed like the wall's (app.js mapHtml), but carrying only the countries
    that show inside the frame, so each page stays light. Drawn inline, so it follows day and night."""
    if not WORLD:
        WORLD.update(read_js('world.js', 'WORLD'))
    if not WORLD:
        return ''
    code = country_of(b)
    name = WORLD['names'].get(code, code)
    W, H = WORLD['w'], WORLD['h']
    pt = project(*b['coords']) if b.get('coords') else WORLD['centre'].get(code)
    c = pt or [W / 2, H / 2]
    box = WORLD['box'].get(code) or [c[0], c[1], c[0], c[1]]
    ratio = H / W
    vw = min(W, max(170, (box[2] - box[0]) * 2.4, (box[3] - box[1]) * 2.4 / ratio)) if box[2] - box[0] < W / 2 else W
    vh = vw * ratio
    cx, cy = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2) if vw < W else (c[0], c[1])
    vx = max(0, min(W - vw, cx - vw / 2))
    vy = max(0, min(H - vh, cy - vh / 2))
    u = vw / 190
    tiny = (box[2] - box[0]) / u < 6
    frame = (vx - 4 * u, vy - 4 * u, vx + vw + 4 * u, vy + vh + 4 * u)
    near = ''.join(fit_path(d, frame, u) for k, d in WORLD['paths'].items() if k in WORLD['box'] and not (
        WORLD['box'][k][2] < vx or WORLD['box'][k][0] > vx + vw or WORLD['box'][k][3] < vy or WORLD['box'][k][1] > vy + vh))
    here = fit_path(WORLD['paths'].get(code, ''), frame, u)
    at = f'cx="{pt[0]:.1f}" cy="{pt[1]:.1f}"' if pt else ''
    city = b['place'].split(',')[0]
    label = city if city == name else f'{city}, {name}'
    return (f'<a class="where" href="{up}#map{"=" + e(b["id"]) if b.get("coords") else ""}" aria-label="On the globe: {e(label)}">'
            f'<svg viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}" role="img" aria-label="World map with {e(name)} marked"><path class="land" d="{near}"/>'
            + (f'<path class="here" d="{here}"/>' if here else '')
            + (f'<circle class="ring" {at} r="{8 * u:.1f}"/>' if pt and tiny else '')
            + (f'<circle class="pin" {at} r="{3.5 * u:.1f}"/>' if pt and b.get('coords') else '')
            + f'</svg><span class="where-name">{e(label)} ↗</span></a>')


def counts(items):
    if not COUNTS:
        from collections import Counter
        COUNTS['idea'] = Counter(c for x in items for c in x['concepts'])
        COUNTS['type'] = Counter(x['type'] for x in items)
        COUNTS['arch'] = {}
        for x in items:
            for n in (NM.list(x['by']) if NM else [x['by']]):
                COUNTS['arch'].setdefault(n, []).append(x)
    return COUNTS


def first_architect(b):
    names = NM.list(b['by']) if NM else [b['by']]
    return names[0] if names else b['by']


def portrait(b):
    if not PEOPLE:
        PEOPLE.update(read_js('architects.js', 'ARCHITECTS') or {'people': {}, 'buildings': {}})
    for qid in PEOPLE.get('buildings', {}).get(b['id'], []):
        p = PEOPLE['people'].get(qid)
        if p and p.get('thumb'):
            return p
    return None


def initials(name):
    import re as _re
    words = [w for w in name.split() if _re.search(r'[^\W\d_]', w)]
    if len(words) < 2:
        return (words[0] if words else '?')[:3].upper()
    return (words[0][0] + words[-1][0]).upper()


def arch_link(name, up):
    """An architect's own page when they have one, else the wall searched for them."""
    return f'{up}architects/{ARCH[name]}/' if name in ARCH else f'{up}?q={q(name)}'


def byline_html(b, up, mine):
    who, p = first_architect(b), portrait(b)
    face = (f'<img class="face" src="{e(p["thumb"])}" alt="{e(p["name"])}" loading="lazy">' if p
            else f'<span class="face initials" aria-hidden="true">{e(initials(who))}</span>')
    n = len(mine) + 1
    long = len(b['by']) > 28 or any(len(w) > 10 for w in re.split(r'[\s-]', b['by']))  # as on the wall
    see = f'<span class="see">See all {n} buildings →</span>' if n > 1 else ''
    return (f'<a class="by-link" href="{arch_link(who, up)}">{face}<span class="by-text"><i>by</i>'
            f'<b{" class=" + chr(34) + "long" + chr(34) if long else ""}>{e(b["by"]).replace("/", "/<wbr>")}</b>{see}</span></a>')


def tile(x, up):
    im = x.get('images') or []
    ph = f'<img src="{e(at(up, im[0]["thumb"]))}" alt="" loading="lazy">' if im else ''
    return (f'<a href="{up}buildings/{x["id"]}/"><span class="ph">{ph}</span><b>{e(x["name"])}</b>'
            f'<small>{e(x["year"])} · {e(x["place"].split(",")[0])}</small></a>')


THREAD_ART = {
    'game': '<path d="M8 5.5v13l10-6.5z"/>',
    'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/>',
}


def threads_html(b, up, n_idea):
    idea = b['concepts'][0] if b.get('concepts') else ''
    d = (FILTER_ART.get('ideaIcons') or {}).get(idea) or 'M4 6h16M4 12h16M4 18h10'
    city = b['place'].split(',')[0]
    cards = [
        ('game', f'{up}play/#daily', 'Guess the building', "Play today’s five", THREAD_ART['game']),
        ('globe', f'{up}#map={e(b["id"])}', 'On the globe', f'Fly to {e(city)}', THREAD_ART['globe']) if b.get('coords') else
        ('globe', f'{up}#map', 'On the globe', 'Spin the globe', THREAD_ART['globe']),  # only buildings with coordinates are on it
    ]
    if idea:
        cards.append(('idea', f'{up}?q={q(idea)}', 'Follow an idea', f'{e(idea)}<span class="n"> · {n_idea}</span>', f'<path d="{e(d)}"/>'))
    return '<nav class="threads" aria-label="Keep exploring">' + ''.join(
        f'<a class="thread {k}" href="{h}"><span class="ic"><svg viewBox="0 0 24 24" aria-hidden="true">{art}</svg></span>'
        f'<span class="tx"><small>{lab}</small><b>{t}</b></span><i class="go" aria-hidden="true">→</i></a>' for k, h, lab, t, art in cards) + '</nav>'


# Building pages Google may index (owner, 29 Oct 2026, after Google dropped the site on 25 Oct): those Google showed at
# least once before the drop, listed in tools/seo/index_keep.txt by tools/index_keep.py. The rest stay on the wall and in
# every link but tell Google alone not to index them ("googlebot", so Bing and ChatGPT search keep them) and leave the
# sitemap. Without the file every building page is indexable.
KEEP_FILE = Path(__file__).resolve().parent / 'seo' / 'index_keep.txt'
KEEP = ({l.strip() for l in KEEP_FILE.read_text().splitlines() if l.strip() and not l.startswith('#')}
        if KEEP_FILE.exists() else None)


def indexable(b):
    return KEEP is None or b['id'] in KEEP


def building_page(b, items):
    up = '../../'
    url = f"{BASE}buildings/{b['id']}/"
    desc = summary(b)
    ims = b.get('images') or []
    og = at(BASE, ims[0]['src']) if ims else BASE + 'og.jpg'
    ld = {'@context': 'https://schema.org', '@type': 'LandmarksOrHistoricalBuildings', 'name': b['name'], 'description': desc, 'url': url,
          'address': place_full(b),
          'isPartOf': {'@type': 'WebSite', 'name': NAME, 'url': BASE}}
    photos = [ld_image(b, im) for im in ims if not im['src'].endswith('drawing.svg')]  # not our own placeholder drawing
    if photos:
        ld['image'] = photos
    if b.get('wiki'):
        ld['sameAs'] = b['wiki']
    head = HEAD.format(title=e(title(b)), desc=e(desc), url=e(url), site=NAME, ogtype='article',
                       ogtitle=e(f"{b['name']} — {b['by']}, {b['year']}"), image=e(og), up=up, wallhash='#' + b['id'],
                       extra=('' if indexable(b) else '<meta name="googlebot" content="noindex, follow">\n') + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', total=TOTAL, css_v=CSS_V)
    if ims:
        figs = ''.join(
            f'<figure id="photo-{k + 1}"><img src="{e(at(up, im["src"]))}" alt="{e(photo_alt(b, im))}" width="{im["w"]}" height="{im["h"]}" loading="{"eager" if k == 0 else "lazy"}">'
            f'{"<span class=" + chr(34) + "nophoto" + chr(34) + ">Photos unavailable</span>" if im.get("kind") == "Drawing" else ""}'
            f'<figcaption><b>{k + 1}/{len(ims)}{"" if im.get("kind") == "Drawing" else " · " + e(photo_caption(im))}</b><span>{(("" if im.get("kind") == "Drawing" else "Photo: ") + e(im["credit"].rstrip(".")) + " · ") if im.get("credit") else ""}{e(im["license"])}'
            f'{(" · <a href=" + chr(34) + e(im["source"]) + chr(34) + ">source</a>") if im.get("source") else ""}</span></figcaption></figure>'
            for k, im in enumerate(ims))
        thumbs = ''.join(f'<a href="#photo-{k + 1}"><img src="{e(at(up, im["thumb"]))}" alt="Photo {k + 1}: {e(photo_kind(im))}" loading="lazy"></a>' for k, im in enumerate(ims))
        gallery = f'<div class="gallery"><div class="slides">{figs}</div><div class="thumbs">{thumbs}</div></div>' + GALLERY_JS
    else:
        gallery = '<div class="gallery none"><p>No free photos yet. Use the links to see photos and drawings elsewhere.</p></div>'
    C = counts(items)
    who = first_architect(b)
    mine = [x for x in C['arch'].get(who, []) if x['id'] != b['id']]
    mine.sort(key=lambda x: -(x.get('y') or 0))
    idea = b['concepts'][0] if b.get('concepts') else ''
    near = related(b, items, n=60)
    pool = [x for x in near if idea in x['concepts'] and x not in mine]
    kin = [x for x in near if x['type'] == b['type'] and x not in mine and x not in pool[:4]]
    rows = []
    if mine:
        rows.append(f'<section class="onward"><h2><span>More by {e(who)}</span><a href="{arch_link(who, up)}">All {len(mine) + 1} →</a></h2><div class="row">{"".join(tile(x, up) for x in mine[:4])}</div></section>')
    if idea and pool:
        rows.append(f'<section class="onward"><h2><span>More with {e(idea.lower())}</span><a href="{up}?q={q(idea)}">All {C["idea"][idea]} →</a></h2><div class="row">{"".join(tile(x, up) for x in pool[:4])}</div></section>')
    ideas = [(c, C['idea'][c], hub_href('idea', c, up)) for c in b['concepts']] + [(b['type'], C['type'][b['type']], hub_href('type', b['type'], up))]
    find = ('<section class="onward find"><h2><span>Find more with</span></h2>' + ''.join(
        f'<a href="{href or up + "?q=" + q(v)}"><span class="nm">{e(v)}</span><i aria-hidden="true"></i><span class="n">{n} buildings →</span></a>' for v, n, href in ideas)
        + '<p class="note">Each opens every building that shares the idea.</p></section>')
    nxt = (mine or pool or kin or near)[0]
    nim = (nxt.get('images') or [{}])[0].get('thumb')
    next_html = (f'<a class="nextcard" href="{up}buildings/{nxt["id"]}/">{f"<img src={chr(34)}{e(at(up, nim))}{chr(34)} alt={chr(34)}{chr(34)}>" if nim else ""}'
                 f'<span><small>Next</small><b>{e(nxt["name"])}</b></span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></a>'
                 '<script>(function () { var n = document.currentScript.previousElementSibling, f = function () { n.classList.toggle("on", scrollY > 480 || innerWidth > 820); };'
                 ' f(); addEventListener("scroll", f, { passive: true }); addEventListener("resize", f); })();</script>')
    deeper = links(b)
    link_html = lambda rows_: ''.join(f'<a href="{e(u)}" rel="noopener"{"" if d else " class=" + chr(34) + "guess" + chr(34)}><b class="lt"><span>{e(k)}</span>{e(n)} ↗</b>{logo_html(n, up)}</a>' for k, n, u, d in rows_)
    deeper_html = (f'<section class="onward deeper"><h2><span>Go deeper</span></h2><div class="links">{link_html(deeper[:6])}</div>'
                   + (f'<details class="more-links"><summary>See all {len(deeper)} links</summary><div class="links">{link_html(deeper[6:])}</div></details>' if len(deeper) > 6 else '')
                   + '</section>')
    same = (f'<section class="onward"><h2><span>More · {e(b["type"])}</span><a href="{up}?q={q(b["type"])}">All {C["type"][b["type"]]} →</a></h2><div class="row">{"".join(tile(x, up) for x in kin[:4])}</div></section>' if kin else '')
    p = portrait(b)
    credit = (f'<p class="credits">Portrait: {e(p["credit"]) + " · " if p.get("credit") else ""}{e(p.get("license", ""))}'
              f'{(" · <a href=" + chr(34) + e(p["source"]) + chr(34) + ">source</a>") if p.get("source") else ""}</p>') if p else ''
    body = f"""<main class="page">
  {gallery}
  <article class="info">
    <p class="kicker">{e(b['type'])} · {e(b['movement'])}</p>
    <h1>{e(b['name'])}</h1>
    <div class="whowhere">{byline_html(b, up, mine)}{where_html(b, up)}</div>
    <p class="meta">{e(b['year'])}</p>
    <p class="study"><span>Key features</span>{e(b['study'])}</p>
    {threads_html(b, up, C['idea'].get(idea, 0))}
    {''.join(rows)}
    {find}
    <section class="onward details"><h2><span>Details</span></h2>{facts_html(b, up)}</section>
    {deeper_html}
    {same}
    <a class="cta" href="{up}#{b['id']}">See it on the wall</a>
    {credit}
  </article>
</main>
{about_block(b)}{next_html}
"""
    return head + body + FOOT.format(up=up, total=TOTAL, css_v=CSS_V)


def index_page(items):
    up = '../'
    url = BASE + 'buildings/'
    desc = f'Every building on Find Great Architecture, curated for architects and students: modern masters, brutalism, regionalism, contemporary and parametric work.'
    head = HEAD.format(title=f'All buildings A–Z · {NAME}', desc=e(desc), url=url, site=NAME, ogtype='website',
                       ogtitle='All buildings A–Z', image=BASE + 'og.jpg', up=up, wallhash='', extra='', total=TOTAL, css_v=CSS_V)
    rows = ''.join(
        f'<a href="{x["id"]}/"><span class="ph">{f"<img src={chr(34)}{e(at(up, x["images"][0]["thumb"]))}{chr(34)} alt={chr(34)}{chr(34)} loading={chr(34)}lazy{chr(34)}>" if x.get("images") else ""}</span>'
        f'<b>{e(x["name"])}</b><small>{e(x["by"])} · {e(x["year"])}</small></a>'
        for x in sorted(items, key=lambda x: x['name'].lower()))
    body = f'<main class="index"><h1>All buildings</h1><p class="lede">{e(desc)}</p><div class="grid">{rows}</div></main>\n'
    return head + body + FOOT.format(up=up, total=TOTAL, css_v=CSS_V)


FONTS = Path(__file__).resolve().parent / 'fonts'
INK, RED = (17, 17, 16), (218, 58, 38)
# Strong exterior photos for the share image; the coolest go under the name.
OG_PICKS = ['saynatsalo-town-hall', 'phillips-exeter-academy-library', 'salk-institute', 'tate-modern', 'ningbo-history-museum', 'kimbell-art-museum']


def redness(im):
    """How red/brick a photo is, so red buildings stay away from the red "Architecture."."""
    r, g, b = [sum(c) / len(c) for c in zip(*im.convert('RGB').resize((24, 16)).getdata())]
    return r - (g + b) / 2


# Go deeper: each site's own logo (site/images/logos/c), in its colours where they read on white and on black, else in a
# mid grey, so the logos stay visible when a phone or browser turns the page dark.
LOGOS = {'ArchDaily': 'archdaily.png', 'WikiArquitectura': 'wikiarquitectura.svg', 'Dezeen': 'dezeen.png', 'Divisare': 'divisare.png',
         'archINFORM': 'archinform.png', 'Wikipedia': 'wikipedia.png', 'YouTube': 'youtube.png', 'Wikimedia Commons': 'commons.png',
         'Map': 'openstreetmap.png'}
GLOBE = '<svg class="lg" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.8 3.8 5.8 3.8 9s-1.2 6.2-3.8 9c-2.6-2.8-3.8-5.8-3.8-9S9.4 5.8 12 3z"/></svg>'


def logo_html(n, up):
    if n == 'Official website':
        return GLOBE
    return f'<img class="lg" src="{up}images/logos/c/{LOGOS[n]}" alt="" aria-hidden="true">' if n in LOGOS else ''


def og_image(items):
    """The share image: six buildings, with the name and address over a dark fade at the bottom.
    The coolest (least red) photos go along the bottom row, under the name."""
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    canvas = Image.new('RGB', (W, H), INK)
    by_id = {x['id']: x for x in items}
    pics = [by_id[i] for i in OG_PICKS if i in by_id and by_id[i].get('images')]
    if len(pics) < 6:  # fall back to any photos, never drawings
        more = [x for x in items if x.get('images') and not x['images'][0]['thumb'].endswith('.svg') and x not in pics]
        random.Random(4).shuffle(more)
        pics += more[:6 - len(pics)]
    ims = [Image.open(SITE / x['images'][0]['thumb']).convert('RGB') for x in pics[:6]]
    if len([i for i in OG_PICKS if i in by_id]) < 6:  # fallback photos: warm on top, cool below
        ims = sorted(ims, key=redness, reverse=True)[:3] + sorted(ims, key=redness)[:3]
    cols, rows, gap = 3, 2, 6
    cw, ch = (W - gap * (cols - 1)) // cols, (H - gap * (rows - 1)) // rows
    for k, im in enumerate(ims):
        r = max(cw / im.width, ch / im.height)
        im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1))
        left, top = (im.width - cw) // 2, (im.height - ch) // 2
        canvas.paste(im.crop((left, top, left + cw, top + ch)), ((k % cols) * (cw + gap), (k // cols) * (ch + gap)))
    fade = Image.new('L', (1, H))
    for y in range(H):
        t = max(0.0, (y - H * 0.36) / (H * 0.5))
        fade.putpixel((0, y), int(255 * min(0.88, t * 1.1)))
    canvas = Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), canvas, fade.resize((W, H)))
    d = ImageDraw.Draw(canvas)
    big = ImageFont.truetype(str(FONTS / 'BigShouldersDisplay-Black.ttf'), 104)
    small = ImageFont.truetype(str(FONTS / 'BarlowCondensed-SemiBold.ttf'), 30)
    x0, base = 44, H - 40
    d.text((x0, base - 92), 'ARCHITECTURE.', font=big, fill=RED, anchor='ls')
    d.text((x0, base - 184), 'FIND GREAT', font=big, fill=(255, 255, 255), anchor='ls')
    d.text((W - 44, base - 96), 'FINDGREATARCHITECTURE.COM', font=small, fill=(255, 255, 255), anchor='rs')
    canvas.save(SITE / 'og.jpg', quality=85, optimize=True)


def icons():
    """The tab and home-screen icon: a black A (for Architecture) with the red full stop, on white (v19)."""
    from PIL import Image, ImageDraw, ImageFont
    # Google shows a site's icon in results only if it is a multiple of 48 px (48, 96, 144, 192...), so those sizes and an .ico too.
    for size, name in [(32, 'favicon.png'), (48, 'favicon-48.png'), (96, 'favicon-96.png'), (180, 'apple-touch-icon.png'), (192, 'favicon-192.png'), (512, 'icon-512.png')]:
        S = size * 4
        im = Image.new('RGB', (S, S), (255, 255, 255))
        d = ImageDraw.Draw(im)
        f = ImageFont.truetype(str(FONTS / 'BigShouldersDisplay-Black.ttf'), int(S * 0.86))
        fw = d.textlength('A', font=f)
        dw = d.textlength('.', font=f)
        x = (S - fw - dw) / 2
        y = S * 0.5 + f.getbbox('A')[3] * 0.5 - f.getbbox('A')[1] * 0.5
        d.text((x, y), 'A', font=f, fill=INK, anchor='ls')
        d.text((x + fw, y), '.', font=f, fill=RED, anchor='ls')
        im.resize((size, size), Image.LANCZOS).save(SITE / name)
    Image.open(SITE / 'icon-512.png').save(SITE / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])


def fingerprint(path):
    import hashlib
    return hashlib.md5(path.read_bytes()).hexdigest()[:8]


def fingerprint_all(*paths):
    import hashlib
    return hashlib.md5(b''.join(p.read_bytes() for p in paths)).hexdigest()[:8]


def stamp_wall():
    """Add ?v=<fingerprint> to the wall's scripts and stylesheet, so a new version reaches browsers at once
    instead of waiting for their cached copy to expire."""
    page = SITE / 'index.html'
    html = page.read_text()
    for name in ('theme.css', 'theme.js', 'styles.css', 'data/wall.js', 'data/names.js', 'data/architects.js', 'data/pritzker.js', 'data/filters.js', 'data/world.js', 'data/books.js', 'data/book_lines.js', 'data/swipe.js', 'data/arch_pages.js', 'app.js', 'filter.js', 'rows.js', 'map.js', 'ai.css'):
        html = re.sub(r'(["\'])' + re.escape(name) + r'(\?v=[0-9a-f]*)?\1', lambda m: f'{m.group(1)}{name}?v={fingerprint(SITE / name)}{m.group(1)}', html)
    page.write_text(html)
    play = SITE / 'play' / 'index.html'  # the game page: its own script and styles, and the buildings it asks about
    if play.exists():
        html = play.read_text()
        for name, path in (('../theme.css', SITE / 'theme.css'), ('../theme.js', SITE / 'theme.js'), ('play.css', SITE / 'play' / 'play.css'), ('play.js', SITE / 'play' / 'play.js'), ('../data/buildings.js', SITE / 'data' / 'buildings.js'), ('../data/links.js', SITE / 'data' / 'links.js'), ('../data/architects.js', SITE / 'data' / 'architects.js'), ('../data/names.js', SITE / 'data' / 'names.js'), ('../ai.css', SITE / 'ai.css'), ('../ai.js', SITE / 'ai.js')):
            html = re.sub(r'(["\'])' + re.escape(name) + r'(\?v=[0-9a-f]*)?\1', lambda m: f'{m.group(1)}{name}?v={fingerprint(path)}{m.group(1)}', html)
        play.write_text(html)
    for extra in ('privacy', 'terms', 'pricing', 'refunds', 'contact'):
        page = SITE / extra / 'index.html'
        if page.exists():
            html = page.read_text()
            for name, path in (('../theme.css', SITE / 'theme.css'), ('../theme.js', SITE / 'theme.js'), ('../pages.css', SITE / 'pages.css'), ('../ai.css', SITE / 'ai.css'), ('../ai.js', SITE / 'ai.js')):
                html = re.sub(r'(["\'])' + re.escape(name) + r'(\?v=[0-9a-f]*)?\1', lambda m: f'{m.group(1)}{name}?v={fingerprint(path)}{m.group(1)}', html)
            page.write_text(html)


def outward(html):
    """Links to other websites open in a new tab, so our page stays where it was (owner, 22 Oct 2026)."""
    def tag(m):
        a = m.group(0)
        h = re.search(r'href="(https?://[^"]+)"', a)
        if not h or 'findgreatarchitecture.com' in h.group(1) or 'target=' in a:
            return a
        a = a[:-1] + ' target="_blank">'
        return a if 'rel=' in a else a[:-1] + ' rel="noopener">'
    return re.sub(r'<a\b[^>]*>', tag, html)


def write_swipe():
    """site/data/swipe.js: the buildings whose tiles get photo dots ("Worth the swipe", tools/worth_swipe.py)."""
    import worth_swipe
    ids = worth_swipe.chosen()
    (SITE / 'data' / 'swipe.js').write_text('// Buildings worth swiping through: photo dots under their tiles. Made by tools/build_pages.py from\n'
                                            '// tools/worth_swipe.py (the rule) and tools/worth_swipe.txt (decisions by eye); edit those, not this file.\n'
                                            'window.SWIPE = ' + json.dumps(ids) + ';\n')
    return len(ids)


# What the wall needs for every building up front. The rest of each building (all its photos, its links) is one small file
# in site/data/detail/, which the opened building fetches. The first photo is kept in the wall: it is the tile.
WALL_FIELDS = ('id', 'n', 'name', 'by', 'place', 'year', 'y', 'type', 'movement', 'region', 'era', 'concepts', 'study', 'coords')
DETAIL_FIELDS = ('images', 'commons', 'links', 'wiki')


def write_wall(items=None):
    """site/data/wall.js (window.BUILDINGS, the slim list the wall loads) and site/data/detail/<id>.json (one per building),
    both made from buildings.js and links.js. buildings.js stays the full source; the game still reads it."""
    import hashlib
    items = load() if items is None else items
    out = SITE / 'data' / 'detail'
    out.mkdir(parents=True, exist_ok=True)
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    rows, digest, ids = [], hashlib.md5(), set()
    for b in items:
        ids.add(b['id'])
        ims = b.get('images') or []
        row = {k: b[k] for k in WALL_FIELDS if b.get(k) is not None}
        row['images'] = [{k: ims[0][k] for k in ('thumb', 'w', 'h') if k in ims[0]}] if ims else []
        row['ni'] = len(ims)
        rows.append(dump(row))
        detail = dump({k: b[k] for k in DETAIL_FIELDS if b.get(k)})
        digest.update(detail.encode())
        path = out / (b['id'] + '.json')
        if not path.exists() or path.read_text() != detail:
            path.write_text(detail)
    for old in out.glob('*.json'):  # a building that left the list leaves its file too
        if old.stem not in ids:
            old.unlink()
    version = hashlib.md5((digest.hexdigest() + ''.join(rows)).encode()).hexdigest()[:8]
    (SITE / 'data' / 'wall.js').write_text('// The wall\'s buildings, one per line, first photo only; the rest of each is in data/detail/<id>.json.\n'
                                           '// Made by tools/build_pages.py from data/buildings.js and data/links.js; edit those, not this file.\n'
                                           f'window.WALL_V = "{version}";\nwindow.BUILDINGS = [\n' + ',\n'.join(rows) + '\n];\n')
    return len(rows)


REST = '<!-- resting -->'


def rest_pages(ids):
    """A building taken off the wall (held back for want of a photo of it) keeps its address, but its old page gives
    way to a short note that search engines leave out (noindex), so Google drops the old title and rejected photos.
    Pages that point to a building's new address ("This building has moved") are left as they are. When the building
    comes back, its full page is written over the note."""
    for page in (SITE / 'buildings').glob('*/index.html'):
        if page.parent.name in ids:
            continue
        text = page.read_text()
        if 'http-equiv="refresh"' in text or REST in text:
            continue
        found = re.search(r'<h1[^>]*>(.*?)</h1>', text, re.S) or re.search(r'<title>(.*?)(?: — | · |</title>)', text, re.S)
        name = html.unescape(re.sub(r'<[^>]+>', '', found.group(1))).strip() if found else page.parent.name.replace('-', ' ')
        page.write_text(f'<!doctype html>\n{REST}\n<html lang="en"><head><meta charset="utf-8"><title>{e(name)} · {NAME}</title>\n'
                        '<meta name="robots" content="noindex"><meta name="viewport" content="width=device-width, initial-scale=1"></head>\n'
                        f'<body><p>{e(name)} is off the wall for now, until we find a good free photo of it.</p>\n'
                        '<p><a href="../">Every building, A to Z</a> · <a href="../../">Back to the wall</a></p></body></html>\n')


def main():
    import sys
    if '--stamp' in sys.argv:  # used by the deploy workflow: refresh the wall's data and the fingerprints only
        write_wall()
        stamp_wall()
        return
    global TOTAL, CSS_V
    items = load()
    TOTAL = f'{len(items):,}'
    CSS_V = fingerprint_all(SITE / 'pages.css', SITE / 'theme.css', SITE / 'theme.js', SITE / 'rows.js', SITE / 'popup.js', SITE / 'ai.css', SITE / 'ai.js')
    page = SITE / 'index.html'
    page.write_text(re.sub(r'<!-- about:start -->.*?<!-- about:end -->', lambda m: '<!-- about:start -->\n' + home_block(items) + '\n<!-- about:end -->',
                           page.read_text(), flags=re.S))
    write_swipe()
    write_wall(items)
    global NM
    import architect_pages
    NM, plans = architect_pages.build(sys.modules[__name__], items)
    ARCH.clear()
    ARCH.update({k: p['slug'] for k, p in plans.items()})
    (SITE / 'data' / 'arch_pages.js').write_text('// Architects who have their own page (site/architects/<slug>/). Made by tools/build_pages.py.\n'
                                                 'window.ARCH_PAGES = ' + json.dumps(ARCH, ensure_ascii=False, sort_keys=True) + ';\n')
    import hub_pages
    HUBS[:] = hub_pages.plan(sys.modules[__name__], items, ARCH)
    HUBLOOK.clear()
    HUBLOOK.update(hub_pages.lookup(HUBS))
    hub_pages.build(sys.modules[__name__], HUBS)
    page.write_text(re.sub(r'<!-- about:start -->.*?<!-- about:end -->', lambda m: '<!-- about:start -->\n' + home_block(items) + '\n<!-- about:end -->',
                           page.read_text(), flags=re.S))
    stamp_wall()
    for b in items:
        out = SITE / 'buildings' / b['id']
        out.mkdir(parents=True, exist_ok=True)
        (out / 'index.html').write_text(outward(building_page(b, items)))
    rest_pages({b['id'] for b in items})
    (SITE / 'buildings' / 'index.html').write_text(outward(index_page(items)))
    if any(x.get('images') for x in items):
        og_image(items)
    urls = [BASE, BASE + 'play/', BASE + 'studio/', BASE + 'pricing/', BASE + 'buildings/'] + ([BASE + 'architects/'] + [f"{BASE}architects/{v}/" for v in sorted(ARCH.values())] if ARCH else []) + [f"{BASE}{hub_pages.kind_url(k)}" for k in hub_pages.KINDS if any(h['intro'] for h in HUBS if h['kind'] == k)] + [f"{BASE}{h['path']}" for h in HUBS if h['intro']] + [f"{BASE}buildings/{b['id']}/" for b in items if indexable(b)] + [f'{BASE}{p}/' for p in ('terms', 'privacy', 'refunds', 'contact')]
    (SITE / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                       + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    (SITE / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
    icons()
    print(f'Built {len(items)} building pages, the index, og.jpg, sitemap.xml and robots.txt.')


if __name__ == '__main__':
    main()
