#!/usr/bin/env python3
"""Pulls the site's Google Search Console numbers and saves them into a folder.

Run daily by .github/workflows/search-console.yml (needs the GSC_SERVICE_ACCOUNT secret; setup in tools/search_console.md).
Writes, into --out:
  daily.csv      day,clicks,impressions,ctr,position  Google web search, one row per day, grows over time
  latest.json    the last 28 days: top queries, pages, countries, devices, query+page pairs, and the same for image search
  indexing.json  Google's verdict on each page it has been asked about (indexed or not, and why), a few hundred pages a day,
                 so the whole sitemap is checked every week or two; its summary counts pages per verdict
Fails loudly (non-zero exit) on any problem, so a broken job is never mistaken for "no searches".

    GSC_SERVICE_ACCOUNT="$(cat key.json)" python3 tools/fetch_search_console.py --out /tmp/gsc
    GSC_TOKEN=ya29... python3 tools/fetch_search_console.py --out /tmp/gsc   # an access token instead of a key, for a quick try
"""
import argparse, base64, csv, datetime as dt, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

API = os.environ.get('GSC_API') or 'https://searchconsole.googleapis.com'  # the override is for tests
TOKEN_URL = os.environ.get('GSC_TOKEN_URL') or 'https://oauth2.googleapis.com/token'
SCOPE = 'https://www.googleapis.com/auth/webmasters.readonly'
DOMAIN = 'findgreatarchitecture.com'
SITEMAP = os.path.join(os.path.dirname(__file__), '..', 'site', 'sitemap.xml')
WINDOW = 28          # days in latest.json, as in Search Console's own default view
ROWS = 1000          # rows per breakdown in latest.json
INSPECT_PER_RUN = 300  # Google allows 2,000 page checks a day per site; 300 checks the whole sitemap in under two weeks


def access_token():
    """A bearer token: GSC_TOKEN as given, or one made from the service account key in GSC_SERVICE_ACCOUNT."""
    if os.environ.get('GSC_TOKEN'):
        return os.environ['GSC_TOKEN']
    raw = os.environ.get('GSC_SERVICE_ACCOUNT')
    if not raw:
        raise SystemExit('GSC_SERVICE_ACCOUNT is not set. Follow "Search Console data for Claude" in tools/search_console.md.')
    try:
        key = json.loads(raw)
        email, pem = key['client_email'], key['private_key']
    except (ValueError, KeyError):
        raise SystemExit('GSC_SERVICE_ACCOUNT is not a service account key: paste the whole JSON file Google gave you.')
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b'=')
    now = int(time.time())
    head = b64(json.dumps({'alg': 'RS256', 'typ': 'JWT'}).encode())
    claim = b64(json.dumps({'iss': email, 'scope': SCOPE, 'aud': TOKEN_URL, 'iat': now, 'exp': now + 3600}).encode())
    signer = serialization.load_pem_private_key(pem.encode(), password=None)
    sig = b64(signer.sign(head + b'.' + claim, padding.PKCS1v15(), hashes.SHA256()))
    body = urllib.parse.urlencode({'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                                   'assertion': (head + b'.' + claim + b'.' + sig).decode()}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=body), timeout=30) as r:
            return json.load(r)['access_token']
    except urllib.error.HTTPError as e:
        raise SystemExit(f'Google refused the service account key ({e.code}): {short(e.read())}')


def call(token, method, path, body=None, attempts=5, waits=(10, 30, 60, 120)):
    """One Search Console request. On a busy server or the per-minute limit it waits (the pause grows) and tries again."""
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json',
                                          'User-Agent': 'findgreatarchitecture-search-console'})
    for attempt in range(attempts):
        pause = waits[min(attempt, len(waits) - 1)]
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < attempts - 1:
                time.sleep(pause)
                continue
            raise SystemExit(f'Search Console said {e.code} for {path}: {short(e.read())}')
        except (urllib.error.URLError, OSError) as e:
            if attempt < attempts - 1:
                time.sleep(pause)
                continue
            raise SystemExit(f'Could not reach Search Console for {path} after {attempts} tries: {e}')


def short(body):
    """An error body as one short plain line."""
    text = body[:4000].decode('utf8', 'replace')
    try:
        err = json.loads(text).get('error')
        if isinstance(err, dict):
            return err.get('message', '')[:300]
        return str(err)[:300]
    except ValueError:
        return ' '.join(re.sub(r'<[^>]+>', ' ', text).split())[:300]


def pick_site(token):
    """The Search Console property for the site: GSC_SITE if set, else the one this key can see (the Domain kind first)."""
    if os.environ.get('GSC_SITE'):
        return os.environ['GSC_SITE']
    sites = [s['siteUrl'] for s in call(token, 'GET', '/webmasters/v3/sites').get('siteEntry') or []
             if DOMAIN in s['siteUrl'] and s.get('permissionLevel') != 'siteUnverifiedUser']
    if not sites:
        raise SystemExit(f'This key sees no Search Console property for {DOMAIN}. In Search Console, Settings, Users and '
                         'permissions, add the service account\'s email address as a user (Restricted is enough).')
    return sorted(sites, key=lambda s: (not s.startswith('sc-domain:'), s))[0]


def query(token, site, start, end, dimensions, kind='web', rows=ROWS):
    body = {'startDate': str(start), 'endDate': str(end), 'dimensions': dimensions, 'type': kind,
            'rowLimit': rows, 'dataState': 'all'}  # 'all' includes the last two days, which Google is still counting
    path = f'/webmasters/v3/sites/{urllib.parse.quote(site, safe="")}/searchAnalytics/query'
    out = []
    for r in call(token, 'POST', path, body).get('rows') or []:
        row = dict(zip(dimensions, r.get('keys') or []))
        row.update(clicks=int(r['clicks']), impressions=int(r['impressions']), ctr=round(r['ctr'], 4),
                   position=round(r['position'], 1))
        out.append(row)
    return out


def sitemap_urls():
    with open(SITEMAP) as f:
        return re.findall(r'<loc>(.*?)</loc>', f.read())


def inspect(token, site, out_dir, limit):
    """Asks Google about pages it has not been asked about yet, then the longest-unchecked ones. Keeps every answer."""
    path = os.path.join(out_dir, 'indexing.json')
    pages = {}
    try:
        with open(path) as f:
            pages = json.load(f).get('pages', {})
    except (OSError, ValueError):
        pass
    urls = sitemap_urls()
    listed = set(urls)
    pages = {u: p for u, p in pages.items() if u in listed}  # pages that left the sitemap are dropped
    todo = sorted(urls, key=lambda u: (u in pages, pages.get(u, {}).get('checked', '')))[:limit]
    done = 0
    for u in todo:
        try:
            res = call(token, 'POST', '/v1/urlInspection/index:inspect', {'inspectionUrl': u, 'siteUrl': site},
                       attempts=3)['inspectionResult']['indexStatusResult']
        except SystemExit as e:  # the search numbers are already saved, and Google's daily limit may simply be used up
            print(f'::warning::stopped checking pages after {done}: {e}')
            break
        pages[u] = {'checked': dt.date.today().isoformat(), 'verdict': res.get('verdict'),
                    'state': res.get('coverageState'), 'last_crawl': (res.get('lastCrawlTime') or '')[:10],
                    'google_canonical': res.get('googleCanonical') if res.get('googleCanonical') not in (None, u) else None}
        done += 1
        time.sleep(0.2)  # well inside 600 a minute
    states = {}
    for p in pages.values():
        states[p['state'] or 'unknown'] = states.get(p['state'] or 'unknown', 0) + 1
    indexed = sum(1 for p in pages.values() if p['verdict'] == 'PASS')
    summary = {'sitemap_pages': len(urls), 'checked': len(pages), 'indexed': indexed,
               'indexed_share': round(indexed / len(pages), 3) if pages else None,
               'by_state': dict(sorted(states.items(), key=lambda kv: -kv[1]))}
    with open(path, 'w') as f:
        json.dump({'updated_at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), 'site': site,
                   'summary': summary, 'pages': dict(sorted(pages.items()))}, f, indent=1)
    return done, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--inspect', type=int, default=INSPECT_PER_RUN, help='pages to check for indexing this run (0 to skip)')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    token = access_token()
    site = pick_site(token)
    today = dt.datetime.now(dt.timezone.utc).date()

    # Daily totals for the last 90 days (Search Console keeps 16 months; older saved days stay in the file).
    days = query(token, site, today - dt.timedelta(days=89), today, ['date'], rows=200)
    path = os.path.join(args.out, 'daily.csv')
    old = {}
    if os.path.exists(path):
        with open(path, newline='') as f:
            old = {r['day']: r for r in csv.DictReader(f)}
    for d in days:
        old[d['date']] = {'day': d['date'], 'clicks': d['clicks'], 'impressions': d['impressions'], 'ctr': d['ctr'],
                          'position': d['position']}
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['day', 'clicks', 'impressions', 'ctr', 'position'])
        w.writeheader()
        for d in sorted(old):
            w.writerow(old[d])

    # The last 28 days, broken down, for web and image search.
    start = today - dt.timedelta(days=WINDOW - 1)
    latest = {'fetched_at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), 'site': site,
              'window_days': WINDOW, 'start': str(start), 'end': str(today)}
    for kind in ('web', 'image'):
        total = query(token, site, start, today, [], kind)
        latest[kind] = {
            'total': total[0] if total else {'clicks': 0, 'impressions': 0},
            'queries': query(token, site, start, today, ['query'], kind),
            'pages': query(token, site, start, today, ['page'], kind),
            'countries': query(token, site, start, today, ['country'], kind, rows=100),
            'devices': query(token, site, start, today, ['device'], kind, rows=10),
            'query_pages': query(token, site, start, today, ['query', 'page'], kind, rows=5000),
        }
    with open(os.path.join(args.out, 'latest.json'), 'w') as f:
        json.dump(latest, f, indent=1)

    done, summary = inspect(token, site, args.out, args.inspect) if args.inspect else (0, None)

    last = sorted(old)[-3:]
    web = latest['web']['total']
    print(f'Property {site}. Saved {len(old)} days to daily.csv; latest:',
          ', '.join(f"{d}={old[d]['clicks']} clicks/{old[d]['impressions']} shown" for d in last))
    print(f"Last {WINDOW} days, web: {web['clicks']} clicks, {web['impressions']} impressions,",
          f"{len(latest['web']['queries'])} queries, {len(latest['web']['pages'])} pages.",
          f"Image search: {latest['image']['total']['clicks']} clicks.")
    if summary:
        print(f"Checked {done} pages for indexing this run; {summary['indexed']} of {summary['checked']} checked so far are in Google.")


if __name__ == '__main__':
    main()
