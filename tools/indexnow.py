#!/usr/bin/env python3
"""Tells Bing (and the other IndexNow search engines: Yandex, Seznam, Naver) which pages changed, so they visit them
soon instead of whenever they next get round to it. Bing's index also feeds ChatGPT search, Copilot and DuckDuckGo.

Run by the deploy workflow (.github/workflows/pages.yml) after each deploy. The key is the file site/<KEY>.txt, which
proves the site is ours; it is not a secret.

    python3 tools/indexnow.py --changed <commit before> <commit after>   # the pages a push changed
    python3 tools/indexnow.py --all                                      # every page in the sitemap (once, or after a big change)
    python3 tools/indexnow.py --all --dry-run                            # list them without sending
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
    urls = (page_url(line) for line in out.stdout.splitlines())
    return [u for u in urls if u and '/yt/' not in u]  # the /yt/ redirects are noindex on purpose


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
