#!/usr/bin/env python3
"""Pull recent buildings (opened or started 2000 or later) from Wikidata, with a lower fame bar than harvest.py.

  python -u tools/harvest_recent.py    # writes tools/harvest/recent.json

Items with an architect (P84), an inception (P571) or opening (P1619) in a year from 2000 on, and at least
MIN_SITELINKS Wikipedia editions; one query per year so none times out. Keeps those with a free photo or a
Commons folder. Records have the same shape as tools/harvest/candidates.json, so cheap_prep.py can read them.
Needs open internet access, so it runs on GitHub Actions (run-tool.yml).
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harvest import sparql, entities, labels  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'tools' / 'harvest' / 'recent.json'
MIN_SITELINKS = 2
NAMED = ('architect', 'country', 'located', 'instance', 'style', 'heritage', 'state')


def ids():
    found = {}
    for year in range(2000, 2027):
        try:
            rows = sparql(f'''SELECT ?item ?n WHERE {{
              ?item wdt:P84 ?a ; wikibase:sitelinks ?n .
              {{ ?item wdt:P571 ?d }} UNION {{ ?item wdt:P1619 ?d }}
              FILTER(YEAR(?d) = {year} && ?n >= {MIN_SITELINKS})
            }}''')
        except Exception as e:  # one slow year shouldn't stop the rest
            print(f'  {year}: {e}', flush=True)
            continue
        for r in rows:
            qid = r['item']['value'].rsplit('/', 1)[1]
            found[qid] = max(found.get(qid, 0), int(r['n']['value']))
        print(f'  {year}: {len(rows)}', flush=True)
    return found


def main():
    found = ids()
    print(f'{len(found)} recent buildings with an architect', flush=True)
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
