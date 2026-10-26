#!/usr/bin/env python3
"""Collect candidate architecture documentaries from Wikidata (and TMDB, when a key is set). Writes tools/films_candidates.json.

  python3 tools/harvest_films.py

Nothing here reaches the site. Claude curates the candidates into tools/films_seed.json with tools/films_batch.py.
Sources:
  1. Wikidata: documentary films and series (Q93204, Q24862 subclasses) whose main subject (P921) is an architect
     (occupation P106 = Q42973), a building (Q41176 and subclasses) or architecture itself (Q12271), or that
     have the genre "architecture film".
  2. TMDB (only if the TMDB_API_KEY environment variable is set, from a GitHub secret): keyword searches, with the
     TMDB id, poster path and watch providers per country. The key is never written to a file.

Every candidate keeps where it came from and which wall architects and buildings it matched, so the one-line
summary can be written from a source. Needs network access, so it runs on GitHub Actions (first line of
tools/films_request.txt: python -u tools/harvest_films.py). Writes tools/films_harvest_report.md.
"""
import collections, json, os, re, sys, time, unicodedata, urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILDINGS = ROOT / 'site' / 'data' / 'buildings.js'
OUT = ROOT / 'tools' / 'films_candidates.json'
REPORT = ROOT / 'tools' / 'films_harvest_report.md'
UA = 'DiscoverArchitecture/1.0 (https://findgreatarchitecture.com/; films harvest)'
SPARQL = 'https://query.wikidata.org/sparql'
TMDB = 'https://api.themoviedb.org/3'
KEYWORDS = ['architecture', 'architect', 'brutalism', 'modernism', 'skyscraper', 'urban planning', 'building design', 'bauhaus']


def get(url, data=None, timeout=90, accept='application/json'):
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, data=data, headers={'User-Agent': UA, 'Accept': accept})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                out = r.read()
            time.sleep(0.4)
            return out
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(5 * (attempt + 1)); continue
            print('HTTP', e.code, url[:120], file=sys.stderr); return None
        except Exception as e:
            time.sleep(3 * (attempt + 1)); print('retry', e, file=sys.stderr)
    return None


def sparql(q):
    raw = get(SPARQL + '?format=json&query=' + urllib.parse.quote(q))
    return json.loads(raw)['results']['bindings'] if raw else []


def fold(s):
    return re.sub(r'[^a-z0-9 ]+', ' ', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()).strip()


def wall():
    t = BUILDINGS.read_text()
    B = json.loads(t[t.index('['):t.rindex(']') + 1])
    names = collections.Counter(a.strip() for b in B for a in b['by'].split(','))
    return B, names


def val(r, k):
    return r.get(k, {}).get('value')


QUERY = '''
SELECT ?film ?filmLabel ?year ?runtime ?directorLabel ?subject ?subjectLabel ?imdb ?tmdb ?desc WHERE {
  VALUES ?cls { wd:Q93204 wd:Q24862 wd:Q5398426 wd:Q15416 }
  ?film wdt:P31/wdt:P279* wd:Q93204 .
  { ?film wdt:P921 ?subject . ?subject wdt:P106 wd:Q42973 }
  UNION { ?film wdt:P921 ?subject . ?subject wdt:P31/wdt:P279* wd:Q41176 }
  UNION { ?film wdt:P921 wd:Q12271 . BIND(wd:Q12271 AS ?subject) }
  UNION { ?film wdt:P136 wd:Q1063457 . BIND(wd:Q12271 AS ?subject) }
  OPTIONAL { ?film wdt:P577 ?date . BIND(YEAR(?date) AS ?year) }
  OPTIONAL { ?film wdt:P2047 ?runtime }
  OPTIONAL { ?film wdt:P57 ?director }
  OPTIONAL { ?film wdt:P345 ?imdb }
  OPTIONAL { ?film wdt:P4947 ?tmdb }
  OPTIONAL { ?film schema:description ?desc FILTER(LANG(?desc) = "en") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
} LIMIT 3000
'''


def from_wikidata(names):
    out = {}
    for r in sparql(QUERY):
        q = val(r, 'film').rsplit('/', 1)[-1]
        c = out.setdefault(q, {'qid': q, 'title': val(r, 'filmLabel'), 'year': val(r, 'year'), 'runtime_min': val(r, 'runtime'),
                               'director': [], 'subjects': [], 'imdb': val(r, 'imdb'), 'tmdb': val(r, 'tmdb'),
                               'wd_desc': val(r, 'desc'), 'sources': ['wikidata'], 'architects': []})
        d = val(r, 'directorLabel')
        if d and d not in c['director']:
            c['director'].append(d)
        s = val(r, 'subjectLabel')
        if s and s not in c['subjects']:
            c['subjects'].append(s)
            if s in names:
                c['architects'].append(s)
    return [c for c in out.values() if c['title'] and not re.match(r'^Q\d+$', c['title'])]


def from_tmdb(key):
    found = {}
    for kw in KEYWORDS:
        for page in (1, 2, 3):
            for kind in ('movie', 'tv'):
                url = f'{TMDB}/search/{kind}?api_key={key}&query={urllib.parse.quote(kw + " documentary")}&page={page}'
                raw = get(url)
                for x in (json.loads(raw)['results'] if raw else []):
                    k = (kind, x['id'])
                    if k not in found:
                        found[k] = {'tmdb': x['id'], 'tmdb_kind': kind, 'title': x.get('title') or x.get('name'),
                                    'year': (x.get('release_date') or x.get('first_air_date') or '')[:4], 'overview': x.get('overview', '')[:400],
                                    'poster': x.get('poster_path'), 'votes': x.get('vote_count'), 'sources': ['tmdb-search:' + kw]}
    return list(found.values())


def main():
    B, names = wall()
    cands = from_wikidata(names)
    key = os.environ.get('TMDB_API_KEY')
    tm = from_tmdb(key) if key else []
    by_tmdb = {str(c['tmdb']): c for c in cands if c.get('tmdb')}
    by_title = {fold(c['title']): c for c in cands}
    for t in tm:
        hit = by_tmdb.get(str(t['tmdb'])) or by_title.get(fold(t['title']))
        if hit:
            hit.update({k: v for k, v in t.items() if k not in ('sources', 'title') and v})
            hit['sources'].append(t['sources'][0])
        else:
            cands.append(t)
    OUT.write_text(json.dumps(cands, ensure_ascii=False, indent=0) + '\n')
    REPORT.write_text(f'# Films harvest\n\n- Candidates: {len(cands)}\n- From Wikidata: {sum("wikidata" in c["sources"] for c in cands)}\n'
                      f'- From TMDB: {len(tm)} (key {"set" if key else "not set, TMDB skipped"})\n'
                      f'- Matching a wall architect: {sum(bool(c.get("architects")) for c in cands)}\n')
    print(open(REPORT).read())


if __name__ == '__main__':
    main()
