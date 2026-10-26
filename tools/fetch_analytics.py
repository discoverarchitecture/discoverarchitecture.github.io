#!/usr/bin/env python3
"""Pulls the site's visitor numbers from GoatCounter and saves them into a folder.

Run daily by .github/workflows/analytics.yml (needs the GOATCOUNTER_TOKEN secret).
Writes, into --out:
  daily.csv    day,visits  one row per day, grows over time (old days are kept, recent days refreshed)
  signups.csv  day,signups FGA Studio waitlist sign-ups per day (the GoatCounter event studio/signup; no emails)
  events.csv   day,path,count  the FGA Studio page and its events (studio/ai-button, studio/ai-link, studio/signup,
               studio/details), the map (map/open) and the game (/play, play/...), per day. Fetched on their own,
               because latest.json keeps only the 100 busiest paths and the many opened buildings can push these out
  latest.json  the last 30 days: pages, referrers, browsers, systems, locations, screen sizes, languages
Fails loudly (non-zero exit) on any problem, so a broken job is never mistaken for "no visitors".

    GOATCOUNTER_TOKEN=... python3 tools/fetch_analytics.py --out /tmp/analytics
"""
import argparse, csv, datetime as dt, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

CODE = os.environ.get('GOATCOUNTER_CODE', 'akshatpagaria')
API = os.environ.get('GOATCOUNTER_API') or f'https://{CODE}.goatcounter.com/api/v0'  # the override is for tests
SECTIONS = {  # name in latest.json -> endpoint
    'pages': 'stats/hits', 'referrers': 'stats/toprefs', 'browsers': 'stats/browsers', 'systems': 'stats/systems',
    'locations': 'stats/locations', 'sizes': 'stats/sizes', 'languages': 'stats/languages',
}


def get(path, attempts=5, timeout=40, waits=(15, 45, 90, 120), **params):
    """One GoatCounter request. On a reset connection or a busy server it waits (the pause grows) and tries again.
    GoatCounter sometimes answers a moment's 404 for a page that exists (stats/total, 18 and 19 Oct 2026), so a 404
    is tried again too; a path that is really wrong still fails after the last try."""
    url = f'{API}/{path}?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + os.environ['GOATCOUNTER_TOKEN'],
                                               'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'discoverarchitecture-analytics'})
    for attempt in range(attempts):
        pause = waits[min(attempt, len(waits) - 1)]
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (404, 429, 500, 502, 503, 504) and attempt < attempts - 1:
                time.sleep(min(int(e.headers.get('Retry-After') or pause), 120))
                continue
            raise SystemExit(f'GoatCounter said {e.code} for {path}: {short(e.read())}')
        except (urllib.error.URLError, OSError) as e:  # includes a reset connection and a timeout
            if attempt < attempts - 1:
                time.sleep(pause)
                continue
            raise SystemExit(f'Could not reach GoatCounter for {path} after {attempts} tries: {e}')


def short(body):
    """An error body as one short plain line (GoatCounter answers some errors with a whole HTML page)."""
    text = body[:4000].decode('utf8', 'replace')
    title = re.search(r'<title>(.*?)</title>', text, re.S)
    text = re.sub(r'<style.*?</style>|<[^>]+>', ' ', text, flags=re.S)
    return ((title.group(1) + ' | ') if title else '') + ' '.join(text.split())[:200]


def day_visits(entry):
    """One day's visits from a /stats/total entry: its daily figure, or the sum of its hours."""
    if entry.get('daily') is not None:
        return int(entry['daily'])
    return sum(int(h or 0) for h in entry.get('hourly') or [])


def signups(out, start, end, event='studio/signup'):
    """FGA Studio waitlist sign-ups per day, from the event the /studio/ page counts after each sign-up (a number only;
    the emails themselves go to the owner's Google Sheet). Kept like daily.csv: old days stay, recent days refresh.
    A failure here only warns: it must never cost the daily visits."""
    try:
        time.sleep(1)
        data = get('stats/hits', attempts=2, timeout=25, waits=(20,), start=start, end=end, filter=event, daily='true', limit=20)
    except SystemExit as e:
        print(f'::warning::waitlist sign-ups could not be fetched ({e}); keeping the numbers saved earlier')
        return
    days = {}
    for h in data.get('hits') or []:
        if h.get('path') != event:
            continue
        for d in h.get('stats') or []:
            if d.get('day'):
                days[d['day'][:10]] = days.get(d['day'][:10], 0) + day_visits(d)
    path = os.path.join(out, 'signups.csv')
    old = {}
    if os.path.exists(path):
        with open(path, newline='') as f:
            old = {r['day']: int(r['signups']) for r in csv.DictReader(f)}
    old.update(days)
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['day', 'signups'])
        for d in sorted(old):
            w.writerow([d, old[d]])
    print('Waitlist sign-ups:', sum(days.values()), 'in the last 90 days')


EVENT_PREFIXES = ('/studio', 'studio/', 'map/', '/play', 'play/')


def events(out, start, end):
    """Per-day counts for the studio page and the map and game events, kept like daily.csv (old days stay, recent days
    refresh). GoatCounter's filter matches titles too, so only paths that start with EVENT_PREFIXES are kept. Warns on failure."""
    days = {}
    for f in ('studio', 'map/', 'play'):
        try:
            time.sleep(1)
            data = get('stats/hits', attempts=2, timeout=25, waits=(20,), start=start, end=end, filter=f, daily='true', limit=50)
        except SystemExit as e:
            print(f'::warning::{f} events could not be fetched ({e}); keeping the numbers saved earlier')
            return
        for h in data.get('hits') or []:
            if not (h.get('path') or '').startswith(EVENT_PREFIXES):
                continue
            for d in h.get('stats') or []:
                if d.get('day') and day_visits(d):
                    days[(d['day'][:10], h['path'])] = day_visits(d)
    path = os.path.join(out, 'events.csv')
    old = {}
    if os.path.exists(path):
        with open(path, newline='') as f:
            old = {(r['day'], r['path']): int(r['count']) for r in csv.DictReader(f)}
    old.update(days)
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['day', 'path', 'count'])
        for k in sorted(old):
            w.writerow([k[0], k[1], old[k]])
    totals = {}
    for (d, p), n in days.items():
        totals[p] = totals.get(p, 0) + n
    print('Studio, map and game, last 90 days:', ', '.join(f'{p}={n}' for p, n in sorted(totals.items())) or 'none yet')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    if not os.environ.get('GOATCOUNTER_TOKEN'):
        raise SystemExit('GOATCOUNTER_TOKEN is not set. Create a read-only key in GoatCounter (Settings, API) and add it as a repository secret.')
    os.makedirs(args.out, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    today = now.date()
    stamp = lambda d: d.strftime('%Y-%m-%dT00:00:00Z')
    until = now.strftime('%Y-%m-%dT%H:%M:%SZ')  # up to this moment: GoatCounter's days follow your own time zone, which can be a day ahead of UTC

    # Daily visits for the last 90 days.
    total = get('stats/total', start=stamp(today - dt.timedelta(days=89)), end=until)
    rows = {e['day'][:10]: day_visits(e) for e in total.get('stats') or [] if e.get('day')}
    if not rows:
        raise SystemExit('GoatCounter returned no days at all; refusing to save an empty result. Raw answer: ' + json.dumps(total)[:300])

    path = os.path.join(args.out, 'daily.csv')
    old = {}
    if os.path.exists(path):
        with open(path, newline='') as f:
            old = {r['day']: int(r['visits']) for r in csv.DictReader(f)}
    old = {d: v for d, v in old.items() if d <= max(rows)}  # drops any day saved ahead of time
    old.update(rows)  # the fetched days win; earlier days stay
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['day', 'visits'])
        for d in sorted(old):
            w.writerow([d, old[d]])

    signups(args.out, stamp(today - dt.timedelta(days=89)), until)
    events(args.out, stamp(today - dt.timedelta(days=89)), until)

    # The last 30 days, broken down.
    window = {'start': stamp(today - dt.timedelta(days=29)), 'end': until}
    latest = {'fetched_at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), 'site': f'{CODE}.goatcounter.com',
              'window_days': 30, 'visits_30d': total.get('total'), 'sections': {}}
    prev = {}  # the breakdowns saved last time, kept for any request that fails now
    try:
        with open(os.path.join(args.out, 'latest.json')) as f:
            prev = json.load(f).get('sections', {})
    except (OSError, ValueError):
        pass
    kept = []
    started = time.time()
    for name, endpoint in SECTIONS.items():
        time.sleep(1)  # stay well inside GoatCounter's rate limit
        try:
            if time.time() - started > 300:  # GoatCounter is very slow: stop trying, the daily visits are already saved
                raise SystemExit('out of time')
            data = get(endpoint, attempts=2, timeout=25, waits=(20,), limit=100, **window)
        except SystemExit as e:  # the daily visits are saved above, so a failing breakdown must not lose them
            print(f'::warning::{name} could not be fetched ({e}); keeping the numbers saved earlier')
            latest['sections'][name] = prev.get(name) or {'stats': [], 'more': False}
            kept.append(name)
            continue
        for h in data.get('hits') or []:  # the per-hour counts of every page are not needed here
            h.pop('stats', None)
        latest['sections'][name] = data
    latest['kept_from_earlier'] = kept
    with open(os.path.join(args.out, 'latest.json'), 'w') as f:
        json.dump(latest, f, indent=1)

    last = sorted(rows)[-3:]
    print('Saved', len(old), 'days to daily.csv. Latest:', ', '.join(f'{d}={rows[d]}' for d in last))


if __name__ == '__main__':
    main()
