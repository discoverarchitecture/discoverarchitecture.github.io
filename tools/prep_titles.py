#!/usr/bin/env python3
"""Prepare buildings named by their English Wikipedia titles, for a hand-picked list (e.g. a librarian's suggestions).

  python -u tools/prep_titles.py tools/outreach/winnipeg_titles.json

The list holds {"title": "...", "id"?: "..."}. Each title is looked up on English Wikipedia (redirects followed) for its
Wikidata item; the rows are written to tools/cheap/pool_titles.json as "fill" rows, then tools/cheap_prep.py fetches
their Wikidata facts, Wikipedia leads and free Commons photos (tools/cheap/prep.json and contact sheets). The list may
also carry "save": [urls] at the top level as {"titles": [...], "save": [...]}: those pages are saved as text by
tools/fetch_pages.py into tools/cheap/titles_pages/, for checking facts and finding a source's own entry pages.
Needs open internet access, so it runs on GitHub Actions (run-tool.yml).
"""
import json, subprocess, sys, time, urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_images import api  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WP = 'https://en.wikipedia.org/w/api.php'


def main():
    spec = json.loads((ROOT / sys.argv[1]).read_text(encoding='utf-8'))
    rows = spec['titles'] if isinstance(spec, dict) else spec
    pool = []
    for r in rows:
        q = api(WP, action='query', titles=r['title'], prop='pageprops', ppprop='wikibase_item', redirects=1)
        pages = q.get('query', {}).get('pages', [])
        page = pages[0] if isinstance(pages, list) and pages else next(iter(pages.values()), {}) if isinstance(pages, dict) else {}
        qid = (page.get('pageprops') or {}).get('wikibase_item')
        if not qid:  # no page by that title: take Wikipedia's own top search hit, flagged for a person to check
            hit = (api(WP, action='query', list='search', srsearch=r['title'], srlimit=1).get('query', {}).get('search') or [{}])[0]
            if hit.get('title'):
                q = api(WP, action='query', titles=hit['title'], prop='pageprops', ppprop='wikibase_item', redirects=1)
                pages = q.get('query', {}).get('pages', [])
                page = pages[0] if isinstance(pages, list) and pages else {}
                qid = (page.get('pageprops') or {}).get('wikibase_item')
                page['searched'] = True
        print(r['title'], '->', page.get('title'), qid, '(searched)' if page.get('searched') else '', flush=True)
        if qid:
            pool.append({'qid': qid, 'label': page.get('title'), 'enwiki': page.get('title'), 'fill': True})
        time.sleep(0.5)
    out = ROOT / 'tools' / 'cheap' / 'pool_titles.json'
    out.write_text(json.dumps(pool, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(len(pool), 'of', len(rows), 'titles found', flush=True)
    subprocess.run([sys.executable, '-u', str(ROOT / 'tools' / 'cheap_prep.py'), 'tools/cheap/pool_titles.json', '--n', str(len(pool))], check=True)
    if isinstance(spec, dict) and spec.get('save'):
        urls = ROOT / 'tools' / 'cheap' / 'titles_urls.json'
        urls.write_text(json.dumps([{'url': u} for u in spec['save']], indent=1) + '\n', encoding='utf-8')
        subprocess.run([sys.executable, '-u', str(ROOT / 'tools' / 'fetch_pages.py'), str(urls), str(ROOT / 'tools' / 'cheap' / 'titles_pages')], check=True)


if __name__ == '__main__':
    sys.exit(main())
