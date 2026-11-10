#!/usr/bin/env python3
"""Finds Wikimedia's own resized copies of the wall's photos, so the site can load them from Wikimedia instead of
keeping copies (GitHub Pages' 1 GB limit; owner, 10 Nov 2026). Runs on GitHub Actions (photos-resolve.yml), because the
cloud chats can't reach Wikimedia. For every photo that is a Commons file, asks the Commons API for a 1,280 px and a
500 px copy (Wikimedia gives the original's own address when the original is smaller) and writes
tools/photos/resolved.json: {"File:Name.jpg": {"w1280": url, "w500": url, "width": w, "height": h}} plus a report.

    python3 tools/photos/resolve.py
"""
import json, os, time, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UA = 'FindGreatArchitecture/1.0 (https://findgreatarchitecture.com; photo addresses)'
CM = 'https://commons.wikimedia.org/w/api.php'
OUT = os.path.join(ROOT, 'tools', 'photos', 'resolved.json')


def api(**p):
    body = urllib.parse.urlencode({**p, 'format': 'json', 'formatversion': 2}).encode()  # POST: long file names
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(CM, data=body, headers={'User-Agent': UA}), timeout=60) as r:
                return json.load(r)
        except Exception as e:
            print('retry', k, e, flush=True); time.sleep(20 * (k + 1))
    raise RuntimeError('Commons API failed 5 times')


txt = open(os.path.join(ROOT, 'site', 'data', 'buildings.js')).read()
B = json.loads(txt[txt.index('['):txt.rindex(']') + 1])
files = sorted({im['file'] for b in B for im in b.get('images', []) if im.get('file')})
done = json.load(open(OUT)) if os.path.exists(OUT) else {}
todo = [f for f in files if f not in done]
print(len(files), 'Commons files,', len(todo), 'to look up', flush=True)
missing = []
for i in range(0, len(todo), 50):
    group = todo[i:i + 50]
    for width, key in ((1280, 'w1280'), (500, 'w500')):
        q = api(action='query', titles='|'.join(group), prop='imageinfo', iiprop='url|size', iiurlwidth=width)
        norm = {n['to']: n['from'] for n in q['query'].get('normalized', [])}
        for p in q['query']['pages']:
            name = norm.get(p['title'], p['title'])
            if 'imageinfo' not in p:
                continue
            ii = p['imageinfo'][0]
            e = done.setdefault(name, {'width': ii.get('width'), 'height': ii.get('height')})
            e[key] = ii.get('thumburl') or ii.get('url')
        time.sleep(1)
    if i % 1000 == 0:
        json.dump(done, open(OUT, 'w'), ensure_ascii=False); print(i, 'of', len(todo), flush=True)
json.dump(done, open(OUT, 'w'), ensure_ascii=False)
missing = [f for f in files if f not in done or 'w500' not in done[f] or 'w1280' not in done[f]]
open(os.path.join(ROOT, 'tools', 'photos', 'resolve_report.md'), 'w').write(
    f'# Photo addresses on Wikimedia\n\n{len(files)} Commons files on the wall; {len(files) - len(missing)} found with both sizes; '
    f'{len(missing)} missing (deleted or renamed on Commons):\n\n' + ''.join(f'- {m}\n' for m in missing))
print('done;', len(missing), 'missing', flush=True)
