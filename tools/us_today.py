#!/usr/bin/env python3
"""One-off (SEO strategy chat, 3 Nov 2026): what changed today, especially from the US. GoatCounter's read-only key can't
export single page views, so this compares today's totals with the three days before: countries, US states, sources,
pages, screen sizes, browsers and systems. Totals only. Runs on Actions with GOATCOUNTER_TOKEN."""
import datetime as dt, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_analytics as fa

now = dt.datetime.now(dt.timezone.utc)
today = now.date()
win = {'today': (today, today), 'previous 3 days': (today - dt.timedelta(days=3), today - dt.timedelta(days=1))}
def stamp(d, end=False): return (d.isoformat() + ('T23:59:59Z' if end else 'T00:00:00Z'))
def get(path, a, b, **kw):
    time.sleep(1)
    try:
        return fa.get(path, attempts=2, timeout=40, waits=(20,), start=stamp(a), end=stamp(b, True), **kw)
    except SystemExit as e:
        print('  (failed:', e, ')'); return {}
print('now', now.isoformat(timespec='minutes'))
for label, (a, b) in win.items():
    print(f'\n######## {label}: {a} to {b}')
    t = get('stats/total', a, b); print('total visits:', t.get('total'), '| events and views:', t.get('total_events'))
    for name, ep in (('countries', 'stats/locations'), ('sources', 'stats/toprefs'), ('screen', 'stats/sizes'), ('browsers', 'stats/browsers'), ('systems', 'stats/systems')):
        d = get(ep, a, b, limit=15)
        print(f'-- {name}:', [((s.get('name') or s.get('id') or '(direct)'), s.get('count')) for s in d.get('stats') or []])
    d = get('stats/locations/US', a, b, limit=15)
    print('-- US states:', [((s.get('name') or s.get('id')), s.get('count')) for s in d.get('stats') or []])
    d = get('stats/hits', a, b, limit=25)
    print('-- pages:', [(h.get('path'), h.get('count')) for h in d.get('hits') or [] if not h.get('event')][:20])
    print('-- events:', [(h.get('path'), h.get('count')) for h in d.get('hits') or [] if h.get('event')][:15])
