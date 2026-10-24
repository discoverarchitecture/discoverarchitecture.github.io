#!/usr/bin/env python3
"""Buildings from the Wikipedia winner lists of architecture prizes: Wikidata rarely records which building won a
prize (tools/harvest_awards.py found only 48), but the prizes' own Wikipedia articles list them.

  python -u tools/harvest_award_lists.py    # writes tools/harvest/award_lists.json

For each article below, every page it links to is looked up through the MediaWiki API (pageprops gives the
Wikidata item), then kept only if Wikidata gives it an architect (P84): that leaves the buildings and drops the
architects, cities and years the lists also link. Each record carries `awards` (the article it came from), a design
reason the checks can cite. Records have the same shape as tools/harvest/candidates.json. Needs open internet
access, so it runs on GitHub Actions (run-tool.yml).
"""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harvest import entities, labels  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'tools' / 'harvest' / 'award_lists.json'
UA = {'User-Agent': 'DiscoverArchitecture/1.0 (https://findgreatarchitecture.com/; award lists)'}
NAMED = ('architect', 'country', 'located', 'instance', 'style', 'heritage', 'state')
# (language, article, the prize's name as shown to the checks). A missing article is skipped.
LISTS = [
    ('en', 'Stirling Prize', 'Stirling Prize'),
    ('en', 'RIBA International Prize', 'RIBA International Prize'),
    ('en', 'European Union Prize for Contemporary Architecture', 'Mies van der Rohe Award'),
    ('en', 'Aga Khan Award for Architecture', 'Aga Khan Award for Architecture'),
    ('en', 'List of Aga Khan Award for Architecture recipients', 'Aga Khan Award for Architecture'),
    ('en', 'Twenty-five Year Award', 'AIA Twenty-five Year Award'),
    ('en', 'Mies Crown Hall Americas Prize', 'Mies Crown Hall Americas Prize'),
    ('en', 'Lubetkin Prize', 'RIBA Lubetkin Prize'),
    ('en', 'Manser Medal', 'Manser Medal'),
    ('en', 'Sulman Medal', 'Sulman Medal'),
    ('en', 'Wilkinson Award', 'Wilkinson Award'),
    ('en', "Governor General's Medals in Architecture", "Governor General's Medal in Architecture"),
    ('en', 'World Architecture Festival', 'World Architecture Festival'),
    ('en', 'Architecture MasterPrize', 'Architecture MasterPrize'),
    ('en', 'Neave Brown Award for Housing', 'RIBA Neave Brown Award'),
    ('en', 'RIBA Stephen Lawrence Prize', 'RIBA Stephen Lawrence Prize'),
    ('en', 'Mies van der Rohe Award for Latin American Architecture', 'Mies van der Rohe Award for Latin American Architecture'),
    ('fr', "Équerre d'argent", "Équerre d'argent"),
    ('de', 'Deutscher Architekturpreis', 'Deutscher Architekturpreis'),
    ('de', 'Mies van der Rohe Award', 'Mies van der Rohe Award'),
    ('es', 'Premio Nacional de Arquitectura de España', 'Premio Nacional de Arquitectura (Spain)'),
    ('sv', 'Kasper Salin-priset', 'Kasper Salin Prize'),
    ('fi', 'Suomen arkkitehtuurin palkinnot', 'Finnish architecture prize'),
    ('ja', '日本建築学会賞', 'Architectural Institute of Japan Prize'),
    ('ja', 'BCS賞', 'BCS Prize (Japan)'),
    ('nl', 'BNA Kubus', 'BNA Kubus'),
    ('it', "Medaglia d'oro all'architettura italiana", "Medaglia d'oro all'architettura italiana"),
    ('no', 'Houens fonds diplom', 'Houens fond diploma'),
    ('da', 'Træprisen', 'Træprisen'),
]


def api(lang, params):
    q = urllib.parse.urlencode({**params, 'format': 'json', 'formatversion': 2})
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(f'https://{lang}.wikipedia.org/w/api.php?' + q, headers=UA), timeout=60) as r:
                return json.load(r)
        except Exception as e:  # 429s and timeouts: wait and retry
            print(f'    retry {k + 1}: {e}', flush=True)
            time.sleep(5 * (k + 1))
    return {}


def linked(lang, title):
    """Wikidata ids of the articles one Wikipedia article links to (main namespace), following continuation."""
    out, cont = set(), {}
    while True:
        d = api(lang, {'action': 'query', 'generator': 'links', 'titles': title, 'gplnamespace': 0, 'gpllimit': 'max',
                       'prop': 'pageprops', 'ppprop': 'wikibase_item', 'redirects': 1, **cont})
        for p in (d.get('query') or {}).get('pages', []):
            q = (p.get('pageprops') or {}).get('wikibase_item')
            if q:
                out.add(q)
        if 'continue' not in d:
            return out
        cont = d['continue']
        time.sleep(0.5)


def main():
    got = {}
    for lang, title, prize in LISTS:
        qs = linked(lang, title)
        print(f'  {lang}:{title}: {len(qs)} linked items', flush=True)
        for q in qs:
            got.setdefault(q, set()).add(prize)
    print(f'{len(got)} linked items in all', flush=True)
    recs = entities(sorted(got))
    recs = {q: r for q, r in recs.items() if r.get('architect') and (r.get('image') or r.get('commons'))}
    print(f'{len(recs)} of them have an architect and a free photo or Commons folder', flush=True)
    refs = set()
    for r in recs.values():
        r['awards'] = sorted(got[r['qid']])
        for key in NAMED:
            refs.update(v for v in r.get(key, []) if isinstance(v, str) and v.startswith('Q'))
    names = labels(refs)
    for r in recs.values():
        for key in NAMED:
            if key in r:
                r[key] = [names.get(v, v) if isinstance(v, str) else v for v in r[key]]
    rows = sorted(recs.values(), key=lambda r: (-len(r['awards']), r['qid']))
    OUT.write_text(json.dumps(rows, ensure_ascii=False, separators=(',', ':')))
    print(f'Wrote {len(rows)} buildings to {OUT.relative_to(ROOT)}', flush=True)


if __name__ == '__main__':
    sys.exit(main())
