#!/usr/bin/env python3
"""Fetches the English Wikipedia articles for a write-up todo list (tools/writeups/todo_<n>.json) on GitHub Actions,
because the cloud chats share a connection Wikipedia rate-limits. Saves tools/writeups/articles_<n>/<id>.json:
the search candidates and the plain text of the first two, for a chat to take exact quotes from.

    python3 tools/writeups/fetch_articles.py <n>
"""
import json, sys, time, urllib.parse, urllib.request, os
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

def retry_titles(b):
    """Second pass (todo_r<n>.json, buildings the first search missed): the building's own English article, found by
    its Wikidata id or its exact name, then a search by name and city instead of name and architect."""
    out = []
    if b.get('qid'):
        url = 'https://www.wikidata.org/w/api.php?' + urllib.parse.urlencode({'action': 'wbgetentities', 'ids': b['qid'], 'props': 'sitelinks', 'sitefilter': 'enwiki', 'format': 'json'})
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r:
                ent = json.load(r)['entities'].get(b['qid'], {})
            t = ent.get('sitelinks', {}).get('enwiki', {}).get('title')
            if t: out.append(t)
        except Exception as e:
            print('wikidata', b['id'], e, flush=True)
        time.sleep(1)
    p = get({'action': 'query', 'titles': b['name'], 'redirects': 1, 'prop': 'pageprops'})['query']['pages'][0]
    if not p.get('missing') and 'disambiguation' not in p.get('pageprops', {}) and p.get('title') not in out:
        out.append(p['title'])
    time.sleep(1)
    city = (b.get('place') or '').split(',')[0]
    hits = get({'action': 'query', 'list': 'search', 'srsearch': f"{b['name']} {city}", 'srlimit': 3})['query']['search']
    for h in hits:
        if h['title'] not in out: out.append(h['title'])
    time.sleep(1)
    return out

for N in sys.argv[1].split():
  os.makedirs(os.path.join(D, f'articles_{N}'), exist_ok=True)
  todo = json.load(open(os.path.join(D, f'todo_{N}.json')))
  for b in todo:
    out = os.path.join(D, f'articles_{N}', b['id'] + '.json')
    if os.path.exists(out): continue
    if N.startswith('r'):
        titles = retry_titles(b)
        res = {'id': b['id'], 'candidates': titles, 'pages': []}
    else:
        q = f"{b['name']} {b['by'].split(',')[0]}"
        s = get({'action': 'query', 'list': 'search', 'srsearch': q, 'srlimit': 3})
        hits = s['query']['search']
        if not hits:
            s = get({'action': 'query', 'list': 'search', 'srsearch': b['name'], 'srlimit': 3}); hits = s['query']['search']
        time.sleep(1.5)
        titles = [h['title'] for h in hits]
        res = {'id': b['id'], 'candidates': titles, 'pages': []}
    for t in titles[:2]:
        e = get({'action': 'query', 'prop': 'extracts', 'explaintext': 1, 'titles': t, 'redirects': 1})
        p = e['query']['pages'][0]
        res['pages'].append({'title': p.get('title'), 'url': 'https://en.wikipedia.org/wiki/' + urllib.parse.quote(p.get('title', '').replace(' ', '_')), 'text': p.get('extract', '')[:30000]})
        time.sleep(1.5)
    json.dump(res, open(out, 'w'), ensure_ascii=False)
    print(b['id'], '->', res['candidates'][:2], flush=True)
