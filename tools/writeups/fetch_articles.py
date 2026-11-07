#!/usr/bin/env python3
"""Fetches the English Wikipedia articles for a write-up todo list (tools/writeups/todo_<n>.json) on GitHub Actions,
because the cloud chats share a connection Wikipedia rate-limits. Saves tools/writeups/articles_<n>/<id>.json:
the search candidates and the plain text of the first two, for a chat to take exact quotes from.

    python3 tools/writeups/fetch_articles.py <n>
"""
import json, sys, time, urllib.parse, urllib.request, os
N = sys.argv[1]
D = os.path.join(os.path.dirname(os.path.abspath(__file__)))
UA = 'FindGreatArchitecture/1.0 (https://findgreatarchitecture.com; facts for building pages)'
def get(params):
    url = 'https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode({**params, 'format': 'json', 'formatversion': 2})
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(60 * (k + 1)); continue
            raise
    raise RuntimeError('429 x4')
os.makedirs(os.path.join(D, f'articles_{N}'), exist_ok=True)
todo = json.load(open(os.path.join(D, f'todo_{N}.json')))
for b in todo:
    out = os.path.join(D, f'articles_{N}', b['id'] + '.json')
    if os.path.exists(out): continue
    q = f"{b['name']} {b['by'].split(',')[0]}"
    s = get({'action': 'query', 'list': 'search', 'srsearch': q, 'srlimit': 3})
    hits = s['query']['search']
    if not hits:
        s = get({'action': 'query', 'list': 'search', 'srsearch': b['name'], 'srlimit': 3}); hits = s['query']['search']
    time.sleep(1.5)
    res = {'id': b['id'], 'candidates': [h['title'] for h in hits], 'pages': []}
    for t in [h['title'] for h in hits[:2]]:
        e = get({'action': 'query', 'prop': 'extracts', 'explaintext': 1, 'titles': t, 'redirects': 1})
        p = e['query']['pages'][0]
        res['pages'].append({'title': p.get('title'), 'url': 'https://en.wikipedia.org/wiki/' + urllib.parse.quote(p.get('title', '').replace(' ', '_')), 'text': p.get('extract', '')[:30000]})
        time.sleep(1.5)
    json.dump(res, open(out, 'w'), ensure_ascii=False)
    print(b['id'], '->', res['candidates'][:2], flush=True)
