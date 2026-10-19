#!/usr/bin/env python3
"""Look at roark.archi before planning anything: robots.txt, sitemap, terms, the home page and a few sample pages.

Saves what it finds in tools/roark/probe/ (raw HTML trimmed to 300 KB each) and a short summary in
tools/roark/probe/summary.md, so the data-collection chat can read the site's structure, licences and terms
from a sandbox that cannot reach it.
"""
import re, time, urllib.request, urllib.error
from pathlib import Path

OUT = Path(__file__).resolve().parent / 'roark' / 'probe'
UA = 'FindGreatArchitecture/1.0 (https://github.com/discoverarchitecture/discoverarchitecture.github.io; one-off site survey)'
BASE = 'https://roark.archi'
START = ['/robots.txt', '/sitemap.xml', '/sitemap_index.xml', '/', '/architects', '/buildings', '/about', '/terms',
         '/legal', '/licence', '/license', '/api', '/data']


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.headers.get('content-type', ''), r.read(3_000_000)
    except urllib.error.HTTPError as e:
        return e.code, '', b''
    except Exception as e:
        return 0, str(e), b''


def name(path):
    return re.sub(r'[^a-z0-9]+', '_', path.lower()).strip('_') or 'home'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    lines, seen, queue = ['# roark.archi survey', ''], set(), list(START)
    while queue and len(seen) < 40:
        p = queue.pop(0)
        if p in seen:
            continue
        seen.add(p)
        code, ctype, body = get(BASE + p)
        lines.append(f'- `{p}`: {code} {ctype} {len(body)} bytes')
        if body:
            (OUT / (name(p) + ('.xml' if 'xml' in ctype or p.endswith('.xml') else '.html' if 'html' in ctype else '.txt'))).write_bytes(body[:300_000])
            text = body.decode('utf-8', 'replace')
            if p in ('/', '/architects', '/buildings') or p.endswith('.xml'):
                links = sorted(set(re.findall(r'(?:href=|<loc>)"?(?:https://roark\.archi)?(/[a-z0-9][^"<>\s#?]*)', text)))
                lines.append(f'  - {len(links)} internal links, e.g. ' + ', '.join(links[:15]))
                # follow a few sample pages of each kind
                kinds = {}
                for l in links:
                    k = l.strip('/').split('/')[0]
                    if l.count('/') >= 2 and len(kinds.setdefault(k, [])) < 2:
                        kinds[k].append(l)
                for v in kinds.values():
                    queue.extend(v)
            for m in re.findall(r'(?i)(licen[cs]e|copyright|terms of use|all rights reserved|creative commons|cc[- ]by[^<"]{0,20}|cc0|public domain)', text)[:0]:
                pass
            hits = re.findall(r'(?i)[^<>]{0,80}(?:licen[cs]e|copyright|terms|rights reserved|creative commons|europeana|wikimedia|art institute)[^<>]{0,80}', text)
            for h in hits[:8]:
                lines.append('  - > ' + ' '.join(h.split())[:200])
        time.sleep(2)
    (OUT / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
