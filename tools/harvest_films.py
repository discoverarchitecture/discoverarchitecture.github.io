#!/usr/bin/env python3
"""Collect candidate architecture documentaries. Writes tools/films_candidates.json.

  python3 tools/harvest_films.py

Nothing here reaches the site. Claude curates the candidates into tools/films_seed.json with tools/films_batch.py.
Sources, all public:

  1. Wikidata: documentary films whose main subject (P921) is an architect (P106 = Q42973) or a building
     (Q41176 / Q811979). Each query asks only for film ids, so it finishes quickly; the facts for those ids
     come afterwards from wbgetentities in batches of 50.
  2. English Wikipedia: the film pages in a handful of architecture film categories, and their subcategories
     one level down. Their Wikidata ids come from the same batch lookup, so the two sources merge cleanly.
  3. TMDB (only if the TMDB_API_KEY environment variable is set, from a GitHub secret): keyword searches, with
     the TMDB id, poster path and vote count. The key is never written to a file.

Every candidate keeps where it came from and which wall architects it matched, so the one-line summary can be
written from a source. The report counts every source, so a source that returns nothing is obvious.

Needs network access, so it runs on GitHub Actions (first line of tools/films_request.txt:
python -u tools/harvest_films.py). Writes tools/films_harvest_report.md.
"""
import collections, json, os, re, sys, time, unicodedata, urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILDINGS = ROOT / 'site' / 'data' / 'buildings.js'
OUT = ROOT / 'tools' / 'films_candidates.json'
REPORT = ROOT / 'tools' / 'films_harvest_report.md'
UA = 'FindGreatArchitecture/1.0 (https://findgreatarchitecture.com/; architecture documentaries; akshatpagariya909@gmail.com)'
SPARQL = 'https://query.wikidata.org/sparql'
WD_API = 'https://www.wikidata.org/w/api.php'
WP_API = 'https://en.wikipedia.org/w/api.php'
TMDB = 'https://api.themoviedb.org/3'

# Documentary films whose subject is an architect, or a building. Each returns ids only, so it stays fast.
SUBJECT_QUERIES = {
    'architect-subject': '''SELECT DISTINCT ?film WHERE {
  ?subject wdt:P106 wd:Q42973 .
  ?film wdt:P921 ?subject .
  { ?film wdt:P31 wd:Q93204 } UNION { ?film wdt:P136 wd:Q93204 }
}''',
    'building-subject': '''SELECT DISTINCT ?film WHERE {
  ?subject wdt:P31/wdt:P279* wd:Q41176 .
  ?film wdt:P921 ?subject .
  { ?film wdt:P31 wd:Q93204 } UNION { ?film wdt:P136 wd:Q93204 }
}''',
    'structure-subject': '''SELECT DISTINCT ?film WHERE {
  ?subject wdt:P31/wdt:P279* wd:Q811979 .
  ?film wdt:P921 ?subject .
  { ?film wdt:P31 wd:Q93204 } UNION { ?film wdt:P136 wd:Q93204 }
}''',
}

# Categories whose films are about architecture itself. "Documentary films about cities" is left out on purpose:
# it is mostly films about what happened in a city, not about how it was built.
WP_CATEGORIES = ['Documentary films about architecture', 'Films about architecture', 'Documentary films about architects',
                 'Documentary films about urban planning', 'Documentary films about buildings and structures']


# Titles to look up by name. These are probes, not facts: a title here only asks Wikipedia whether such a film
# exists. Everything the shelf shows — director, year, runtime, the quoted line — comes from the page that is
# found, exactly as for every other source, and a title that resolves to nothing is simply dropped. The list
# leans Western, as the audience does, with some work from elsewhere that is under-represented.
TITLE_SEEDS = [
    'Citizen Jane: Battle for the City', 'Koolhaas Houselife', 'The Human Scale', 'Cathedrals of Culture',
    'The Infinite Happiness', 'Microtopia', 'Archiculture', 'Coast Modern', 'The Destruction of Memory',
    'Integral Man', 'The Experimental City', 'Eero Saarinen: The Architect Who Saw the Future',
    'How Much Does Your Building Weigh, Mr Foster?', 'Bauhaus Spirit', 'The New Bauhaus', 'Modern Ruin',
    'Regular or Super', 'A Machine to Live In', 'Barbicania', 'Leaning Into the Wind',
    'Making Space: 5 Women Changing the Face of Architecture', 'The Oyler House: Richard Neutra\'s Desert Retreat',
    'Louis Kahn: Silence and Light', 'Glenn Murcutt: Spirit of Place', 'Objectified',
    'Citizen Architect: Samuel Mockbee and the Spirit of the Rural Studio', 'Brasilia: Life After Design',
    'Bird\'s Nest: Herzog & de Meuron in China', 'Rem Koolhaas: A Kind of Architect', 'My Playground',
    'Tokyo Ride', 'The Competition', 'Gray Matters', 'Concrete Love', 'Moriyama-San',
    'Visual Acoustics: The Modernism of Julius Shulman', 'Abstract: The Art of Design',
    'The World\'s Most Extraordinary Homes', 'Grand Designs', 'Infinite Space: The Architecture of John Lautner',
    'Sketches of Frank Gehry', 'Unfinished Spaces', 'The Vision of Paolo Soleri', 'Garbage Warrior',
    'Urbanized', 'Maya Lin: A Strong Clear Vision', 'My Architect', 'The Pruitt-Igoe Myth',
    'Eames: The Architect and the Painter', 'Mendelsohn\'s Incessant Visions', 'Sagrada: The Mystery of Creation',
    'Antonio Gaudi', 'Loos Ornamental', 'Spaces: The Architecture of Paul Rudolph', 'Taq Kasra: Wonder of Architecture',
]

TMDB_KEYWORDS = ['architecture', 'architect', 'brutalism', 'bauhaus', 'urban planning', 'skyscraper', 'modernist architecture']


def get(url, timeout=90):
    """One GET, with the backoff Wikimedia asks for. Returns bytes, or None once it has given up."""
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                out = r.read()
            time.sleep(1.0)
            return out
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                wait = int(e.headers.get('Retry-After') or 0) or 10 * (attempt + 1)
                print(f'  HTTP {e.code}, waiting {wait}s', file=sys.stderr)
                time.sleep(wait); continue
            print(f'  HTTP {e.code} {url[:110]}', file=sys.stderr); return None
        except Exception as e:
            print(f'  retry after {e}', file=sys.stderr); time.sleep(5 * (attempt + 1))
    print(f'  gave up on {url[:110]}', file=sys.stderr)
    return None


def sparql_ids(name, query):
    """Run one id-only query and return its film QIDs."""
    raw = get(SPARQL + '?format=json&query=' + urllib.parse.quote(query), timeout=180)
    if raw is None:
        print(f'{name}: FAILED', file=sys.stderr); return []
    rows = json.loads(raw)['results']['bindings']
    ids = [r['film']['value'].rsplit('/', 1)[-1] for r in rows]
    print(f'{name}: {len(ids)} films')
    return ids


def wp_category(cat, depth=1):
    """Film pages in a Wikipedia category, and in its subcategories one level down."""
    url = WP_API + '?' + urllib.parse.urlencode({'action': 'query', 'format': 'json', 'list': 'categorymembers',
                                                 'cmtitle': f'Category:{cat}', 'cmlimit': '500'})
    raw = get(url)
    if raw is None:
        return [], []
    members = json.loads(raw).get('query', {}).get('categorymembers', [])
    pages = [m['title'] for m in members if m['ns'] == 0]
    subs = [m['title'].split(':', 1)[1] for m in members if m['ns'] == 14]
    if depth > 0:
        for s in subs:
            p, _ = wp_category(s, depth - 1)
            pages += p
    return pages, subs


def wp_search_categories():
    """Category names on Wikipedia that pair films with architecture, so a renamed category cannot silently vanish."""
    found = []
    for term in ['architecture films', 'documentary films architecture', 'films about architects', 'urban planning films']:
        url = WP_API + '?' + urllib.parse.urlencode({'action': 'query', 'format': 'json', 'list': 'search',
                                                     'srsearch': term, 'srnamespace': '14', 'srlimit': '20'})
        raw = get(url)
        for r in (json.loads(raw).get('query', {}).get('search', []) if raw else []):
            t = r['title'].split(':', 1)[-1]
            if re.search(r'film|documentar|cinema', t, re.I) and re.search(r'architect|urban|building|structure', t, re.I):
                if t not in found:
                    found.append(t)
    print(f'category search found: {found}')
    return found


def wp_by_title(probe):
    """Ask Wikipedia whether a film of roughly this name has a page. Returns its real page title, or None."""
    url = WP_API + '?' + urllib.parse.urlencode({'action': 'query', 'format': 'json', 'list': 'search',
                                                 'srsearch': probe, 'srnamespace': '0', 'srlimit': '3'})
    raw = get(url)
    hits = (json.loads(raw).get('query', {}).get('search', []) if raw else [])
    stop = {'the', 'a', 'an', 'of', 'and', 'in', 'on', 'to', 'for'}
    want = {w for w in re.findall(r'[a-z0-9]+', probe.lower())} - stop
    for h in hits:
        got = {w for w in re.findall(r'[a-z0-9]+', h['title'].lower())} - stop
        # every distinctive word asked for must be in the page's own title. A looser rule drifted from a film to
        # the architect's own article: "Tadao Ando documentary" came back as the page about Tadao Ando.
        if want and want <= got:
            return h['title']
    return None


def wp_extracts(titles):
    """The opening paragraph of each film's Wikipedia page, so a summary can be written from a source, not invented."""
    out = {}
    for i in range(0, len(titles), 20):
        chunk = titles[i:i + 20]
        url = WP_API + '?' + urllib.parse.urlencode({'action': 'query', 'format': 'json', 'prop': 'extracts',
                                                     'exintro': '1', 'explaintext': '1', 'exlimit': '20',
                                                     'titles': '|'.join(chunk), 'redirects': '1'})
        raw = get(url)
        if raw is None:
            continue
        for pg in (json.loads(raw).get('query', {}).get('pages') or {}).values():
            if pg.get('extract'):
                out[pg['title']] = pg['extract'][:1200]
        print(f'  extracts {min(i + 20, len(titles))}/{len(titles)}')
    return out


def wd_entities(qids):
    """Facts for up to 50 Wikidata ids at a time: label, year, runtime, directors, subjects, IMDb, TMDB."""
    out = {}
    for i in range(0, len(qids), 50):
        chunk = qids[i:i + 50]
        url = WD_API + '?' + urllib.parse.urlencode({'action': 'wbgetentities', 'format': 'json', 'ids': '|'.join(chunk),
                                                     'props': 'labels|descriptions|claims|sitelinks', 'languages': 'en', 'sitefilter': 'enwiki'})
        raw = get(url)
        if raw is None:
            continue
        for q, e in (json.loads(raw).get('entities') or {}).items():
            if 'missing' in e:
                continue
            out[q] = e
        print(f'  facts {min(i + 50, len(qids))}/{len(qids)}')
    return out


def wd_by_titles(titles):
    """Wikidata id -> English Wikipedia page title, 50 at a time."""
    out = {}
    for i in range(0, len(titles), 50):
        chunk = titles[i:i + 50]
        url = WD_API + '?' + urllib.parse.urlencode({'action': 'wbgetentities', 'format': 'json', 'sites': 'enwiki',
                                                     'titles': '|'.join(chunk), 'props': 'sitelinks', 'sitefilter': 'enwiki'})
        raw = get(url)
        if raw is None:
            continue
        for q, e in (json.loads(raw).get('entities') or {}).items():
            if q.startswith('Q'):
                out[q] = ((e.get('sitelinks') or {}).get('enwiki') or {}).get('title') or e.get('title')
    return out


def claim_values(e, prop):
    vals = []
    for c in (e.get('claims') or {}).get(prop, []):
        v = ((c.get('mainsnak') or {}).get('datavalue') or {}).get('value')
        if v is not None:
            vals.append(v)
    return vals


def qid_of(v):
    return v.get('id') if isinstance(v, dict) else None


def fold(s):
    return re.sub(r'[^a-z0-9 ]+', ' ', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()).strip()


def wall_names():
    t = BUILDINGS.read_text()
    B = json.loads(t[t.index('['):t.rindex(']') + 1])
    return collections.Counter(a.strip() for b in B for a in b['by'].split(','))


def build_candidates(entities, labels, names, source_of):
    """Turn raw Wikidata entities into candidate records, naming any wall architect among their subjects."""
    out = []
    for q, e in entities.items():
        title = ((e.get('labels') or {}).get('en') or {}).get('value')
        if not title:
            continue
        year = None
        for v in claim_values(e, 'P577'):
            t = (v or {}).get('time')
            if t:
                year = int(t[1:5]); break
        runtime = None
        for v in claim_values(e, 'P2047'):
            try:
                runtime = int(float(v.get('amount', '0').lstrip('+')))
            except (TypeError, ValueError):
                pass
            break
        kind_ids = [qid_of(v) for v in claim_values(e, 'P31') if qid_of(v)]
        genre_ids = [qid_of(v) for v in claim_values(e, 'P136') if qid_of(v)]
        subj_ids = [qid_of(v) for v in claim_values(e, 'P921') if qid_of(v)]
        dir_ids = [qid_of(v) for v in claim_values(e, 'P57') if qid_of(v)]
        subjects = [labels.get(s, s) for s in subj_ids]
        out.append({'qid': q, 'title': title, 'year': year, 'runtime_min': runtime,
                    'instance_of': [labels.get(k, k) for k in kind_ids],
                    'genres_wd': [labels.get(g, g) for g in genre_ids],
                    'is_doc': 'Q93204' in kind_ids + genre_ids,
                    'director': [labels.get(d, d) for d in dir_ids],
                    'subjects': subjects,
                    'architects': [s for s in subjects if s in names],
                    'imdb': (claim_values(e, 'P345') or [None])[0],
                    'tmdb': (claim_values(e, 'P4947') or [None])[0],
                    'enwiki': ((e.get('sitelinks') or {}).get('enwiki') or {}).get('title'),
                    'wd_desc': ((e.get('descriptions') or {}).get('en') or {}).get('value'),
                    'sources': sorted(source_of.get(q, []))})
    return out


def from_tmdb(key):
    found = {}
    for kw in TMDB_KEYWORDS:
        for page in (1, 2):
            for kind in ('movie', 'tv'):
                raw = get(f'{TMDB}/search/{kind}?api_key={key}&query={urllib.parse.quote(kw + " documentary")}&page={page}')
                for x in (json.loads(raw).get('results', []) if raw else []):
                    found.setdefault((kind, x['id']), {
                        'tmdb': x['id'], 'tmdb_kind': kind, 'title': x.get('title') or x.get('name'),
                        'year': int((x.get('release_date') or x.get('first_air_date') or '0000')[:4] or 0) or None,
                        'overview': (x.get('overview') or '')[:400], 'poster': x.get('poster_path'),
                        'votes': x.get('vote_count'), 'sources': ['tmdb:' + kw]})
    print(f'tmdb: {len(found)} films')
    return list(found.values())


def main():
    names = wall_names()
    source_of = collections.defaultdict(set)
    counts = {}

    for name, query in SUBJECT_QUERIES.items():
        ids = sparql_ids(name, query)
        counts[name] = len(ids)
        for q in ids:
            source_of[q].add(name)

    cats = list(dict.fromkeys(WP_CATEGORIES + wp_search_categories()))
    wp_seen, page_cat = {}, collections.defaultdict(set)
    for cat in cats:
        pages, subs = wp_category(cat)
        wp_seen[cat] = len(pages)
        print(f'wikipedia "{cat}": {len(pages)} pages, {len(subs)} subcategories')
        for t in pages:
            page_cat[t].add(cat)
    for probe in TITLE_SEEDS:
        t = wp_by_title(probe)
        if t:
            page_cat[t].add('seed-title')
        print(f'  seed {probe[:46]:<48}-> {t or "no page"}')
    wp_pages = sorted(page_cat)
    title_qid = wd_by_titles(wp_pages)
    for q, title in title_qid.items():
        for cat in page_cat.get(title, ['?']):
            source_of[q].add('wikipedia:' + cat)
    counts['wikipedia (distinct pages)'] = len(wp_pages)

    qids = sorted(source_of)
    print(f'{len(qids)} distinct films; fetching facts')
    entities = wd_entities(qids)

    # second pass so subject and director ids read as names
    extra = sorted({qid_of(v) for e in entities.values() for p in ('P921', 'P57', 'P31', 'P136') for v in claim_values(e, p) if qid_of(v)})
    print(f'{len(extra)} people and places to name')
    labels = {q: ((e.get('labels') or {}).get('en') or {}).get('value') for q, e in wd_entities(extra).items()}

    cands = build_candidates(entities, labels, names, source_of)

    wiki_titles = sorted({c['enwiki'] for c in cands if c.get('enwiki')})
    print(f'{len(wiki_titles)} Wikipedia pages to read')
    extracts = wp_extracts(wiki_titles)
    for c in cands:
        if c.get('enwiki') and extracts.get(c['enwiki']):
            c['extract'] = extracts[c['enwiki']]

    key = os.environ.get('TMDB_API_KEY')
    tm = from_tmdb(key) if key else []
    by_tmdb = {str(c['tmdb']): c for c in cands if c.get('tmdb')}
    by_title = {(fold(c['title']), c.get('year')): c for c in cands}
    for t in tm:
        hit = by_tmdb.get(str(t['tmdb'])) or by_title.get((fold(t['title']), t.get('year')))
        if hit:
            hit.update({k: v for k, v in t.items() if k not in ('sources', 'title', 'year') and v})
            hit['sources'] += t['sources']
        else:
            cands.append(t)

    cands.sort(key=lambda c: (-len(c.get('architects') or []), -(c.get('votes') or 0), c['title']))
    OUT.write_text(json.dumps(cands, ensure_ascii=False, indent=0) + '\n')

    lines = ['# Films harvest', '', f'Candidates: **{len(cands)}**', '', '| Source | Films |', '|---|---|']
    lines += [f'| {k} | {v} |' for k, v in counts.items()]
    lines += [f'| wikipedia · {c} | {n} |' for c, n in wp_seen.items()]
    lines += [f'| tmdb | {len(tm)} ({"key set" if key else "no key, skipped"}) |', '',
              f'- Naming an architect on the wall: {sum(bool(c.get("architects")) for c in cands)}',
              f'- With a year: {sum(bool(c.get("year")) for c in cands)}',
              f'- With a runtime: {sum(bool(c.get("runtime_min")) for c in cands)}',
              f'- With an English Wikipedia page: {sum(bool(c.get("enwiki")) for c in cands)}',
              f'- With an opening paragraph to quote: {sum(bool(c.get("extract")) for c in cands)}',
              f'- Documentary by Wikidata (not fiction): {sum(bool(c.get("is_doc")) for c in cands)}']
    REPORT.write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
