#!/usr/bin/env python3
"""One-off diagnosis of the Google drop on 25 Oct 2026 (SEO strategy chat): which days, pages, countries and devices
lost impressions, what Google says about the sitemap, and how Google sees the top pages today. Prints to the log only.
Runs on GitHub Actions (.github/workflows/site-check.yml) with the GSC_SERVICE_ACCOUNT secret."""
import collections, datetime as dt, json, sys, urllib.parse
sys.path.insert(0, 'tools')
import fetch_search_console as g

tok = g.access_token()
site = g.pick_site(tok)
end = dt.date.today()
start = end - dt.timedelta(days=12)
print('site', site, start, end)
for dims in (['date'], ['date', 'device'], ['date', 'country']):
    rows = g.query(tok, site, start, end, dims, rows=5000)
    print(f'\n== {dims}')
    if dims == ['date', 'country']:
        rows = [r for r in rows if r['country'] in ('usa', 'gbr', 'ind', 'deu', 'can', 'aus', 'fra')]
    for r in sorted(rows, key=lambda r: tuple(r[d] for d in dims)):
        print(' ', ' '.join(str(r[d]) for d in dims), r['clicks'], r['impressions'], r['position'])
rows = g.query(tok, site, start, end, ['date', 'page'], rows=25000)
by = collections.defaultdict(list)
for r in rows:
    by[r['date']].append(r)
print('\n== pages with impressions per day, and the busiest')
for d in sorted(by):
    rs = sorted(by[d], key=lambda r: -r['impressions'])
    print(' ', d, len(rs), 'pages;', '; '.join(f"{r['page'].split('.com')[1]} {r['impressions']}@{r['position']}" for r in rs[:4]))
early = {r['page'] for r in rows if r['date'] <= str(end - dt.timedelta(days=5))}
late = {r['page'] for r in rows if r['date'] >= str(end - dt.timedelta(days=3))}
print('pages seen before, still seen in the last 3 days:', len(early & late), 'of', len(early))
print('\n== sitemaps')
print(json.dumps(g.call(tok, 'GET', f'/webmasters/v3/sites/{urllib.parse.quote(site, safe="")}/sitemaps'), indent=1)[:3000])
top = collections.Counter()
for r in rows:
    if r['date'] <= '2026-10-24':
        top[r['page']] += r['impressions']
print('\n== how Google sees the busiest pages now')
for u, n in top.most_common(8):
    res = g.call(tok, 'POST', '/v1/urlInspection/index:inspect', {'inspectionUrl': u, 'siteUrl': site})
    s = res.get('inspectionResult', {}).get('indexStatusResult', {})
    print(' ', u, n, '|', s.get('verdict'), s.get('coverageState'), 'crawled', s.get('lastCrawlTime'), 'fetch', s.get('pageFetchState'),
          'robots', s.get('robotsTxtState'), 'indexing', s.get('indexingState'), 'canonical', s.get('googleCanonical'))
