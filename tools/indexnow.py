#!/usr/bin/env python3
"""Tells Bing (and the other IndexNow search engines: Yandex, Seznam, Naver) which pages changed, so they visit them
soon instead of whenever they next get round to it. Bing's index also feeds ChatGPT search, Copilot and DuckDuckGo.

Run by the deploy workflow (.github/workflows/pages.yml) after each deploy. The key is the file site/<KEY>.txt, which
proves the site is ours; it is not a secret.

    python3 tools/indexnow.py --changed <commit before> <commit after>   # the pages a push changed
    python3 tools/indexnow.py --all                                      # every page in the sitemap (once, or after a big change)
    python3 tools/indexnow.py --all --dry-run                            # list them without sending

--changed leaves out pages whose only change is a ?v= stamp, and when a push changes more than BULK pages (a template
change, such as the Studio banner on every building page) it leaves out existing building pages too (owner, 10 Nov 2026,
after Bing Webmaster Tools showed 115,000 addresses sent in three weeks). A big round of real new text on building pages
can be sent with a manual run of the deploy workflow, which sends the whole sitemap once.
"""
import argparse, json, re, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
HOST = 'findgreatarchitecture.com'
BASE = f'https://{HOST}/'
KEY = '076f730e235203ae9f9063c2ffda0cd4'
ENDPOINT = 'https://api.indexnow.org/indexnow'
LIMIT = 10000  # IndexNow takes at most 10,000 addresses per request


def page_url(path):
    """site/buildings/villa-savoye/index.html -> https://findgreatarchitecture.com/buildings/villa-savoye/"""
    p = Path(path)
    if p.suffix != '.html' or p.parts[0] != 'site':
        return None
    rel = Path(*p.parts[1:])
    if rel.name == 'index.html':
        rel = rel.parent
        return BASE + (str(rel) + '/' if str(rel) != '.' else '')
    return BASE + str(rel)


def changed(before, after):
    """Pages under site/ that a push added, changed or removed (removed and noindexed pages are worth telling too)."""
    if not before or set(before) == {'0'}:
        return []
    subprocess.run(['git', 'fetch', '-q', '--depth=1', 'origin', before], cwd=ROOT, check=False)
    out = subprocess.run(['git', 'diff', '--name-only', before, after, '--', 'site'], cwd=ROOT, capture_output=True, text=True)
    if out.returncode:
        print(f'Could not compare {before[:7]} and {after[:7]}: {out.stderr.strip()[:200]}')
        return []
    files = [f for f in out.stdout.splitlines() if page_url(f)]
    real = stamp_only_skipped(before, after, files)
    if len(real) > BULK:
        # A site-wide template change (the Studio banner, a footer line) touches every building page. Bing re-reads those
        # on its own visits; telling it about thousands at once only dilutes the pages that really are new or important.
        new_files = set(subprocess.run(['git', 'diff', '--name-only', '--diff-filter=A', before, after, '--', 'site'], cwd=ROOT,
                                       capture_output=True, text=True).stdout.split())
        kept = [f for f in real if not f.startswith('site/buildings/') or f in new_files]
        print(f'{len(real)} pages is a site-wide change: sending the {len(kept)} that are not existing building pages')
        real = kept
    urls = (page_url(f) for f in real)
    return [u for u in urls if u and '/yt/' not in u]  # the /yt/ redirects are noindex on purpose


BULK = 300  # more pages than this in one push is a template change, not new writing


STAMP = re.compile(r'\?v=[0-9a-f]{6,}')


def stamp_only_skipped(before, after, files):
    """The files whose change is more than new ?v= fingerprints. When a shared style sheet changes, every page's ?v=
    changes with it, and telling Bing that thousands of pages changed when their words did not (115,000 addresses in
    three weeks for a site of about 2,700 pages, seen in Bing Webmaster Tools on 10 Nov 2026) teaches it to ignore us."""
    if not files:
        return []
    out = subprocess.run(['git', 'diff', '-U0', '--no-color', before, after, '--'] + files, cwd=ROOT,
                         capture_output=True, text=True)
    if out.returncode:
        return files  # can't tell: keep them all
    real, cur, minus, plus = [], None, [], []

    def close():
        if cur and (cur not in real) and sorted(STAMP.sub('', l) for l in minus) != sorted(STAMP.sub('', l) for l in plus):
            real.append(cur)

    for line in out.stdout.splitlines():
        if line.startswith('diff --git '):
            close()
            cur, minus, plus = line.split(' b/', 1)[1], [], []
        elif line.startswith('new file') or line.startswith('deleted file'):
            if cur and cur not in real:
                real.append(cur)
        elif line.startswith('---') or line.startswith('+++'):
            continue
        elif line.startswith('-'):
            minus.append(line[1:])
        elif line.startswith('+'):
            plus.append(line[1:])
    close()
    print(f'{len(files)} pages changed on disk, {len(real)} of them in more than their ?v= stamps')
    return real


def sitemap():
    return re.findall(r'<loc>(.*?)</loc>', (SITE / 'sitemap.xml').read_text())


def send(urls):
    for i in range(0, len(urls), LIMIT):
        body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'{BASE}{KEY}.txt', 'urlList': urls[i:i + LIMIT]}).encode()
        req = urllib.request.Request(ENDPOINT, data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                print(f'IndexNow accepted {len(urls[i:i + LIMIT])} addresses (HTTP {r.status}).')
        except urllib.error.HTTPError as e:
            # 200 and 202 both mean accepted; 403 or 422 mean the key file is not live yet or does not match.
            print(f'IndexNow said {e.code}: {e.read()[:300].decode("utf8", "replace")}')
            return False
        except (urllib.error.URLError, OSError) as e:
            print(f'Could not reach IndexNow: {e}')
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--changed', nargs=2, metavar=('BEFORE', 'AFTER'))
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    urls = sitemap() if a.all else changed(*a.changed) if a.changed else []
    urls = list(dict.fromkeys(urls))
    if not urls:
        print('No pages changed; nothing to tell.')
        return
    print(f'{len(urls)} pages, for example: ' + ', '.join(urls[:3]))
    if not a.dry_run and not send(urls):
        sys.exit(0)  # never fail a deploy over this; the log says what went wrong


if __name__ == '__main__':
    main()
