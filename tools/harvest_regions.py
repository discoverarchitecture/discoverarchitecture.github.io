#!/usr/bin/env python3
"""Pull buildings from under-represented regions from Wikidata: Africa, Latin America and Asia except Japan.

  python -u tools/harvest_regions.py    # writes tools/harvest/regions.json

Items with an architect (P84) and at least MIN_SITELINKS Wikipedia editions in each country of Africa, South
America, Central America and the Caribbean, and Asia (Japan left out: it is already well represented on the wall).
One query per country so none times out. Keeps those with a free photo or a Commons folder. Records have the same
shape as tools/harvest/candidates.json, so cheap_prep.py can read them. South Asian work gets extra representation
because it is under-represented, not because the audience is Indian (see CLAUDE.md).
Needs open internet access, so it runs on GitHub Actions (run-tool.yml).
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harvest import sparql, entities, labels  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'tools' / 'harvest' / 'regions.json'
MIN_SITELINKS = 2
NAMED = ('architect', 'country', 'located', 'instance', 'style', 'heritage', 'state')
CONTINENTS = 'wd:Q15 wd:Q18 wd:Q48'  # Africa, South America, Asia
LATIN = ['Q96', 'Q774', 'Q241', 'Q800', 'Q804', 'Q783', 'Q811', 'Q792', 'Q786', 'Q1183', 'Q766', 'Q790', 'Q242']
SKIP = {'Q17'}  # Japan


def countries():
    rows = sparql(f'''SELECT DISTINCT ?c WHERE {{
      ?c wdt:P31 wd:Q6256 ; wdt:P30 ?k . VALUES ?k {{ {CONTINENTS} }}
    }}''')
    cs = {r['c']['value'].rsplit('/', 1)[1] for r in rows} | set(LATIN)
    return sorted(cs - SKIP)


def ids():
    found = {}
    for c in countries():
        try:
            rows = sparql(f'''SELECT ?item ?n WHERE {{
              ?item wdt:P84 ?a ; wdt:P17 wd:{c} ; wikibase:sitelinks ?n .
              FILTER(?n >= {MIN_SITELINKS})
            }}''')
        except Exception as e:  # one slow country shouldn't stop the rest
            print(f'  {c}: {e}', flush=True)
            continue
        for r in rows:
            qid = r['item']['value'].rsplit('/', 1)[1]
            found[qid] = max(found.get(qid, 0), int(r['n']['value']))
        print(f'  {c}: {len(rows)}', flush=True)
    return found


def main():
    found = ids()
    print(f'{len(found)} buildings with an architect in these regions', flush=True)
    recs = entities(sorted(found))
    recs = {q: r for q, r in recs.items() if r.get('image') or r.get('commons')}
    print(f'{len(recs)} of them have a free photo or Commons folder', flush=True)
    refs = set()
    for r in recs.values():
        r['sitelinks'] = found.get(r['qid'], 0)
        for key in NAMED:
            refs.update(v for v in r.get(key, []) if isinstance(v, str) and v.startswith('Q'))
    names = labels(refs)
    for r in recs.values():
        for key in NAMED:
            if key in r:
                r[key] = [names.get(v, v) if isinstance(v, str) else v for v in r[key]]
    rows = sorted(recs.values(), key=lambda r: -r['sitelinks'])
    OUT.write_text(json.dumps(rows, ensure_ascii=False, separators=(',', ':')))
    print(f'Wrote {len(rows)} buildings to {OUT.relative_to(ROOT)}', flush=True)


if __name__ == '__main__':
    sys.exit(main())
