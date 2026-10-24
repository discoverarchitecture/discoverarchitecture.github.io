#!/usr/bin/env python3
"""Pull buildings that won an architecture prize from Wikidata: the Aga Khan Award, the Mies van der Rohe Award
(EU Prize for Contemporary Architecture), the Stirling Prize, RIBA awards, the AIA Twenty-five Year Award and other
prizes whose English name says architecture.

  python -u tools/harvest_awards.py    # writes tools/harvest/awards.json

An item counts when it has "award received" (P166) for such a prize, or the prize lists it as "winner" (P1346).
Each record carries `awards` (the prize names, with the year when Wikidata gives one), a design reason the Haiku
and Sonnet checks can cite. Records have the same shape as tools/harvest/candidates.json, so cheap_prep.py can
read them. Needs open internet access, so it runs on GitHub Actions (run-tool.yml).
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harvest import sparql, entities, labels  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'tools' / 'harvest' / 'awards.json'
NAMED = ('architect', 'country', 'located', 'instance', 'style', 'heritage', 'state')
# searches for architecture prizes for buildings (prizes for people, such as the Pritzker or the Royal Gold Medal,
# go to architects, not buildings, so they never match here)
SEARCHES = ['architecture award', 'architecture prize', 'Aga Khan Award for Architecture', 'Mies van der Rohe Award',
            'European Union Prize for Contemporary Architecture', 'Stirling Prize', 'RIBA National Award',
            'RIBA International Prize', 'RIBA European Award', 'Twenty-five Year Award', 'AIA Honor Award',
            'Lubetkin Prize', "Prix de l'Équerre d'argent", 'World Building of the Year', 'Civic Trust Award',
            'Deutscher Architekturpreis', 'Premio Nacional de Arquitectura', 'Architectural Institute of Japan Prize',
            'Japan Institute of Architects Award', 'BNA Kubus', 'Mies Crown Hall Americas Prize', 'Architecture MasterPrize',
            'Rudy Bruner Award', 'Governor General\'s Medal in Architecture', 'Sulman Medal', 'Wilkinson Award',
            'Zevaco', 'Bauherrenpreis', 'Kasper Salin Prize', 'Piranesi Award', 'Plečnik Award', 'Ithuriel']


def prizes():
    """Prize items found by Wikidata's own search for each name above that are an award (Q618779) and that some
    item received or won."""
    found = {}
    for w in SEARCHES:
        try:
            rows = sparql(f'''SELECT DISTINCT ?p ?l WHERE {{
              SERVICE wikibase:mwapi {{ bd:serviceParam wikibase:endpoint "www.wikidata.org" ;
                wikibase:api "EntitySearch" ; mwapi:search "{w}" ; mwapi:language "en" ; mwapi:limit "30" .
                ?p wikibase:apiOutputItem mwapi:item . }}
              ?p wdt:P31/wdt:P279* wd:Q618779 .
              FILTER EXISTS {{ {{ ?x wdt:P166 ?p }} UNION {{ ?p wdt:P1346 ?x }} }}
              ?p rdfs:label ?l . FILTER(LANG(?l) = "en")
            }}''')
        except Exception as e:  # a slow search shouldn't stop the rest
            print(f'  {w}: {e}', flush=True)
            continue
        for r in rows:
            found[r['p']['value'].rsplit('/', 1)[1]] = r['l']['value']
        print(f'  {w}: {", ".join(r["l"]["value"] for r in rows)[:200]}', flush=True)
    return found


def winners(ps):
    """qid -> {prize name with year}, for buildings (items with an architect) that received or won each prize."""
    got = {}
    for p, name in sorted(ps.items()):
        try:
            rows = sparql(f'''SELECT DISTINCT ?x ?y WHERE {{
              {{ ?x p:P166 ?s . ?s ps:P166 wd:{p} . OPTIONAL {{ ?s pq:P585 ?t }} }}
              UNION {{ wd:{p} p:P1346 ?s . ?s ps:P1346 ?x . OPTIONAL {{ ?s pq:P585 ?t }} }}
              ?x wdt:P84 ?a .
              BIND(YEAR(?t) AS ?y)
            }}''')
        except Exception as e:
            print(f'  {name}: {e}', flush=True)
            continue
        for r in rows:
            q = r['x']['value'].rsplit('/', 1)[1]
            y = r.get('y', {}).get('value')
            got.setdefault(q, set()).add(f'{name} ({y})' if y else name)
        if rows:
            print(f'  {name}: {len(rows)}', flush=True)
    return got


def main():
    ps = prizes()
    print(f'{len(ps)} architecture prizes', flush=True)
    got = winners(ps)
    print(f'{len(got)} prize-winning buildings with an architect', flush=True)
    recs = entities(sorted(got))
    recs = {q: r for q, r in recs.items() if r.get('image') or r.get('commons')}
    print(f'{len(recs)} of them have a free photo or Commons folder', flush=True)
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
    rows = sorted(recs.values(), key=lambda r: -len(r['awards']))
    OUT.write_text(json.dumps(rows, ensure_ascii=False, separators=(',', ':')))
    print(f'Wrote {len(rows)} buildings to {OUT.relative_to(ROOT)}', flush=True)


if __name__ == '__main__':
    sys.exit(main())
