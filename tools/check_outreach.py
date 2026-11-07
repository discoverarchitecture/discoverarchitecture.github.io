#!/usr/bin/env python3
"""Opens every candidate library guide and notes what the SEO strategy chat needs to judge it, so the owner only writes
to librarians whose guide loads, is about architecture and lists outside websites. Runs on GitHub Actions
(.github/workflows/outreach-check.yml), because the cloud chats can only reach Wikipedia. Brief: tools/outreach/BRIEF.md.

Reads  tools/outreach/candidates_<group>.json
Writes tools/outreach/<group>.json        guides that loaded, each with "checked", "page_title", "about_architecture",
                                          "outside_sites" (hosts it links to beyond the school), "links_to_us",
                                          "profile_found" (a librarian profile or contact link on the page)
       tools/outreach/check_<group>.md    failures and weak guides, so the chat can replace them

Email addresses are never written: the repository is public, and the owner finds them on the guide when sending.

    python3 tools/check_outreach.py --group libguides
"""
import argparse, concurrent.futures, datetime as dt, html, json, re, sys, urllib.parse
from pathlib import Path
from check_reading_links import UA, host
import urllib.request

DIR = Path(__file__).resolve().parent / 'outreach'
US = ('findgreatarchitecture.com', 'discoverarchitecture.github.io')
# Hosts every guide carries (the guide platform, the school's own catalogue, social buttons): not "outside sites".
SKIP = ('libguides.com', 'springshare.com', 'libapps.com', 'libanswers.com', 'libcal.com', 'facebook.com', 'twitter.com',
        'x.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'google.com', 'googleapis.com', 'gstatic.com',
        'jquery.com', 'bootstrapcdn.com', 'cloudflare.com', 'jsdelivr.net', 'fontawesome.com', 'doi.org', 'proxy',
        'ezproxy', 'worldcat.org', 'creativecommons.org')


def base(h):
    """The registrable part, roughly: guides.lib.umich.edu -> umich.edu, www.ox.ac.uk -> ox.ac.uk."""
    parts = h.split('.')
    return '.'.join(parts[-3:] if len(parts) > 2 and parts[-2] in ('ac', 'edu', 'co', 'org', 'gov') else parts[-2:])


def check(c):
    url = c.get('url') or ''
    if not url.startswith('http'):
        return None, 'not a web address'
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html', 'Accept-Language': 'en-GB,en;q=0.9'})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            final, body = r.geturl(), r.read(1_500_000).decode('utf8', 'replace')
    except Exception as e:
        return None, f'could not open ({getattr(e, "code", type(e).__name__)})'
    m = re.search(r'<title[^>]*>(.*?)</title>', body, re.I | re.S)
    title = ' '.join(html.unescape(m.group(1)).split()) if m else ''
    if re.search(r'\b(page not found|404|log ?in|sign ?in)\b', title, re.I):
        return None, f'error or sign-in page ("{title[:60]}")'
    school = base(host(final))
    hrefs = re.findall(r'href=["\'](https?://[^"\'#]+)', body, re.I)
    outside = sorted({host(h) for h in hrefs if base(host(h)) != school and not any(s in host(h) for s in SKIP)})
    profile = next((urllib.parse.urljoin(final, h) for h in re.findall(r'href=["\']([^"\']*(?:prf\.php\?account_id=|/profile/|/staff/|/subject-librarian)[^"\']*)', body, re.I)), '')
    text = re.sub(r'<[^>]+>', ' ', body)
    return {**{k: v for k, v in c.items() if '@' not in str(v)}, 'url': final, 'checked': dt.date.today().isoformat(),
            'page_title': title, 'about_architecture': bool(re.search(r'architect', title + text[:200_000], re.I)),
            'outside_sites': outside[:60], 'n_outside': len(outside), 'links_to_us': any(any(u in h for u in US) for h in outside),
            'profile_found': profile}, 'ok'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--group', required=True)
    group = ap.parse_args().group
    src = DIR / f'candidates_{group}.json'
    if not src.exists():
        sys.exit(f'{src} not found')
    cands = json.loads(src.read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(check, cands))
    good, notes = [], []
    for c, (r, why) in zip(cands, results):
        if r is None:
            notes.append(f"- {c.get('school')}: {c.get('url')} — {why}")
            continue
        if not r['about_architecture']:
            notes.append(f"- {c.get('school')}: {r['url']} — weak: the page never mentions architecture")
        elif r['n_outside'] < 3:
            notes.append(f"- {c.get('school')}: {r['url']} — weak: links to only {r['n_outside']} outside sites")
        good.append(r)
    (DIR / f'{group}.json').write_text(json.dumps(good, indent=1, ensure_ascii=False) + '\n')
    strong = sum(1 for r in good if r['about_architecture'] and r['n_outside'] >= 3)
    (DIR / f'check_{group}.md').write_text(
        f'# Guide check for {group}, {dt.date.today().isoformat()}\n\n{len(good)} guides loaded, {strong} look strong, '
        f'{len(cands) - len(good)} failed.\n\n## Failed or weak (replace these)\n\n' + ('\n'.join(notes) or 'None.') + '\n')
    print(f'{group}: {len(good)} loaded, {strong} strong, {len(cands) - len(good)} failed.')


if __name__ == '__main__':
    main()
