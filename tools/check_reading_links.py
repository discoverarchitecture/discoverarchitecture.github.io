#!/usr/bin/env python3
"""Opens every candidate reading link and keeps only those that load, so the "Read about" lists never send a student
to a dead page. Runs on GitHub Actions (.github/workflows/reading-check.yml), which can reach every publisher; the
cloud chats can only reach Wikipedia, so they find candidates with web search and this checks them.

Reads  tools/reading/candidates_<group>.json   the same format as <group>.json (see tools/reading/BRIEF.md), unchecked
Writes tools/reading/<group>.json               only the links that loaded, each with "checked" (today) and the page's
                                                real title when the candidate had none
       tools/reading/check_<group>.md           every link that failed, and why, so the chat can find replacements

    python3 tools/check_reading_links.py --group architects_01
"""
import argparse, concurrent.futures, datetime as dt, html, json, re, sys, urllib.error, urllib.parse, urllib.request
from pathlib import Path

DIR = Path(__file__).resolve().parent / 'reading'
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/126.0 Safari/537.36')
# Big publishers that turn away automated visitors (403) though the page is there for a reader. A link from one of
# these that answers 401, 402 or 403 is kept, marked "blocked_check": true, because it came from a web search result.
BLOCKS_BOTS = ('nytimes.com', 'newyorker.com', 'ft.com', 'wsj.com', 'theatlantic.com', 'economist.com',
               'architectural-review.com', 'architectsjournal.co.uk', 'dezeen.com', 'archdaily.com', 'domusweb.it',
               'architecturaldigest.com', 'wallpaper.com', 'theguardian.com', 'bbc.com', 'washingtonpost.com',
               'bloomberg.com', 'vogue.com', 'smithsonianmag.com', 'britannica.com', 'jstor.org', 'tandfonline.com')


def host(url):
    return urllib.parse.urlsplit(url).netloc.lower().removeprefix('www.')


def check(link):
    """(ok, reason, title) for one link."""
    url = link.get('url') or ''
    if not url.startswith('http'):
        return False, 'not a web address', ''
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml',
                                               'Accept-Language': 'en-GB,en;q=0.9'})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            final, body = r.geturl(), r.read(200_000).decode('utf8', 'replace')
    except urllib.error.HTTPError as e:
        if e.code in (401, 402, 403, 429) and any(host(url).endswith(h) for h in BLOCKS_BOTS):
            return True, f'blocked_check:{e.code}', ''
        return False, f'HTTP {e.code}', ''
    except Exception as e:  # timeouts, bad certificates, refused connections
        return False, f'could not open ({type(e).__name__})', ''
    if urllib.parse.urlsplit(final).path in ('', '/') and urllib.parse.urlsplit(url).path not in ('', '/'):
        return False, f'sent to the home page ({final})', ''
    m = (re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)', body, re.I)
         or re.search(r'<title[^>]*>(.*?)</title>', body, re.I | re.S))
    title = ' '.join(html.unescape(m.group(1)).split()) if m else ''
    if re.search(r'\b(page not found|404 not found|no longer available)\b', title, re.I):
        return False, f'error page ("{title[:60]}")', title
    return True, 'ok', title


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--group', required=True)
    group = ap.parse_args().group
    src = DIR / f'candidates_{group}.json'
    if not src.exists():
        sys.exit(f'{src} not found')
    entries = json.loads(src.read_text())
    jobs = [(i, j, l) for i, e in enumerate(entries) for j, l in enumerate(e.get('links') or [])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = dict(zip(((i, j) for i, j, _ in jobs), pool.map(lambda job: check(job[2]), jobs)))
    today, out, failed, kept = dt.date.today().isoformat(), [], [], 0
    for i, e in enumerate(entries):
        links = []
        for j, l in enumerate(e.get('links') or []):
            ok, why, title = results[(i, j)]
            if not ok:
                failed.append(f"- {e['key']}: {l.get('url')} — {why}")
                continue
            l = {**l, 'checked': today}
            if why.startswith('blocked_check'):
                l['blocked_check'] = True
            if title and not l.get('title'):
                l['title'] = title
            links.append(l)
        kept += len(links)
        out.append({'key': e['key'], 'links': links})
    (DIR / f'{group}.json').write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n')
    short = [f"- {e['key']}: {len(e['links'])} links" for e in out if len(e['links']) < 10]
    (DIR / f'check_{group}.md').write_text(
        f'# Link check for {group}, {today}\n\n{kept} links kept, {len(failed)} failed.\n\n'
        '## Failed (find replacements)\n\n' + ('\n'.join(failed) or 'None.') +
        '\n\n## Pages with fewer than 10 links\n\n' + ('\n'.join(short) or 'None.') + '\n')
    print(f'{group}: {kept} links kept, {len(failed)} failed, {len(short)} pages under 10.')


if __name__ == '__main__':
    main()
