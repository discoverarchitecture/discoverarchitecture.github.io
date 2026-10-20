#!/usr/bin/env python3
"""Wikipedia pageviews over the last 12 months for every building with an English article.

  python -u tools/fetch_pageviews.py

Reads each building's article from site/data/links.js ("wiki"), asks the Wikimedia pageviews API for the
monthly views of the last 12 full months, and writes tools/pageviews.json (building id -> views), keeping
earlier numbers for buildings it could not reach. Also writes tools/top1000.txt: the 1,000 most looked-up
buildings, one id per line, which the drawings, links and "About" work for the most-studied buildings uses.
Runs on GitHub Actions (the sandbox can't reach Wikimedia).
"""
import json, time, urllib.parse, urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'tools' / 'pageviews.json'
UA = 'FindGreatArchitecture/1.0 (https://github.com/discoverarchitecture/discoverarchitecture.github.io; pageviews script)'


def read_js(name):
    t = (ROOT / 'site' / 'data' / name).read_text(encoding='utf-8')
    return json.loads(t[t.index('= ') + 2:].rstrip().rstrip(';'))


def views(title, start, end):
    url = ('https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/'
           f'{urllib.parse.quote(title, safe="")}/monthly/{start}/{end}')
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r:
                return sum(i['views'] for i in json.load(r).get('items', []))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 0
            time.sleep(2 ** attempt)
        except Exception:
            time.sleep(2 ** attempt)
    return None


def main():
    links = read_js('links.js')
    ids = [b['id'] for b in read_js('buildings.js')]
    today = date.today()
    end = date(today.year, today.month, 1)
    start = date(end.year - 1, end.month, 1)
    s, e = start.strftime('%Y%m%d'), end.strftime('%Y%m%d')
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    out = {}
    for n, i in enumerate(ids):
        wiki = (links.get(i) or {}).get('wiki') or ''
        if '/wiki/' not in wiki:
            continue
        title = urllib.parse.unquote(wiki.split('/wiki/', 1)[1]).replace(' ', '_')
        v = views(title, s, e)
        if v is None:
            v = old.get(i)
        if v:
            out[i] = v
        if n % 200 == 0:
            print(n, i, v, flush=True)
        time.sleep(0.05)
    OUT.write_text(json.dumps(dict(sorted(out.items(), key=lambda kv: -kv[1])), indent=1) + '\n')
    top = sorted(out, key=lambda i: -out[i])[:1000]
    (ROOT / 'tools' / 'top1000.txt').write_text('\n'.join(top) + '\n')
    print(len(out), 'buildings with views;', 'top 1000 written')


if __name__ == '__main__':
    main()
