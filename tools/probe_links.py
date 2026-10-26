#!/usr/bin/env python3
"""Check that the link finder's site searches still answer, for buildings known to be on them.

  python -u tools/probe_links.py

Prints, for each source, the HTTP outcome, the first results and what find_links.py would keep. Runs on
GitHub Actions (the sandbox can't reach these sites).
"""
import json, sys, urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_images import fetch  # noqa: E402
import find_links as fl  # noqa: E402

TESTS = [('lascaux-iv', 'Lascaux IV'), ('allianz-arena', 'Allianz Arena'), ('senedd-cardiff', 'Senedd'),
         ('chrysler-building', 'Chrysler Building')]
RAW = {
    'archdaily': 'https://www.archdaily.com/search/api/v1/us/projects?q=',
    'wikiarquitectura': 'https://en.wikiarquitectura.com/wp-json/wp/v2/search?per_page=5&search=',
    'divisare': 'https://divisare.com/search?q=',
    'bing': 'https://www.bing.com/search?format=rss&count=30&q=',
}

for i, name in TESTS:
    print('==', name)
    for src, url in RAW.items():
        try:
            body = fetch(url + urllib.parse.quote(name), timeout=60)
            print(f'  {src}: {len(body)} bytes:', body[:300].decode('utf-8', 'ignore').replace('\n', ' '))
        except Exception as e:
            print(f'  {src}: FAILED', repr(e)[:300])
    b = {'id': i, 'name': name, 'by': '', 'place': ''}
    for f in (fl.archdaily, fl.wikiarquitectura, fl.divisare):
        print(f'  parsed {f.__name__}:', json.dumps(f(b)[:3], ensure_ascii=False)[:300])
