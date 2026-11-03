#!/usr/bin/env python3
"""One-off (SEO strategy chat, 3 Nov 2026): where today's US visits come from. Exports GoatCounter's page views (no IPs
are stored there) and prints only totals: by day and country, then for US views of the last three days, by source,
page, device, browser, hour and whether they look like bots. Runs on Actions with GOATCOUNTER_TOKEN."""
import collections, csv, datetime as dt, gzip, io, json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_analytics as fa

def call(method, path, body=None, raw=False):
    req = urllib.request.Request(f'{fa.API}/{path}', method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + os.environ['GOATCOUNTER_TOKEN'], 'Content-Type': 'application/json',
                                          'Accept': 'application/json', 'User-Agent': 'discoverarchitecture-analytics'})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    return data if raw else json.loads(data)

job = call('POST', 'export', {})
eid = job['id']
for _ in range(60):
    time.sleep(5)
    st = call('GET', f'export/{eid}')
    if st.get('finished_at'):
        break
data = call('GET', f'export/{eid}/download', raw=True)
try:
    data = gzip.decompress(data)
except OSError:
    pass
rows = list(csv.DictReader(io.StringIO(data.decode('utf8', 'replace'))))
print(len(rows), 'rows; columns:', list(rows[0].keys()) if rows else [])
day = lambda r: (r.get('Date') or r.get('2Date') or r.get('created_at') or '')[:10]
loc = lambda r: (r.get('Location') or '')
since = (dt.date.today() - dt.timedelta(days=6)).isoformat()
views = [r for r in rows if day(r) >= since and (r.get('Event') or 'false').lower() != 'true']
print('\n== page views per day and top countries (last 7 days, events excluded)')
for d in sorted({day(r) for r in views}):
    c = collections.Counter(loc(r)[:2] for r in views if day(r) == d)
    print(' ', d, sum(c.values()), c.most_common(6))
us = [r for r in views if loc(r).startswith('US') and day(r) >= (dt.date.today() - dt.timedelta(days=2)).isoformat()]
print('\n== US page views, last 3 days:', len(us), 'sessions:', len({r.get('Session') for r in us}))
for name, key in (('source', lambda r: (r.get('Referrer') or '(direct)') + ' [' + (r.get('Referrer scheme') or '') + ']'),
                  ('page', lambda r: r.get('Path') or ''), ('state/region', loc),
                  ('device size', lambda r: r.get('Screen size') or ''), ('browser', lambda r: r.get('Browser') or ''),
                  ('system', lambda r: r.get('System') or ''), ('hour UTC', lambda r: (r.get('Date') or '')[11:13]),
                  ('bot flag', lambda r: r.get('Bot') or ''), ('first visit', lambda r: r.get('FirstVisit') or r.get('First visit') or '')):
    print(f'-- by {name}:', collections.Counter(key(r) for r in us).most_common(15))
ev = [r for r in rows if day(r) >= (dt.date.today() - dt.timedelta(days=2)).isoformat() and (r.get('Event') or '').lower() == 'true' and loc(r).startswith('US')]
print('-- US events (last 3 days):', collections.Counter(r.get('Path') for r in ev).most_common(20))
