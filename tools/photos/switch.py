#!/usr/bin/env python3
"""Moves the wall's extra photos to Wikimedia's own copies, to keep the site under GitHub Pages' 1 GB limit
(owner, 10 Nov 2026). Reads tools/photos/resolved.json (made on GitHub Actions by resolve.py) and changes
site/data/buildings.js:

- Each building's cover photo (its first photo) keeps its small thumbnail here: the wall, the map, search and the
  share images draw it, and it must load fast and work in a canvas.
- Every other thumbnail loads Wikimedia's 500 px copy instead.
- The first hundred buildings' full photos load Wikimedia's 1,280 px copy, as the later buildings already do.
- Our drawings and the Art Institute of Chicago's works stay here, and so does any photo Wikimedia didn't find.

Then it deletes the files nothing points to any more. Run build_pages.py afterwards.

    python3 tools/photos/switch.py          # change the data and delete the files
    python3 tools/photos/switch.py --dry    # only count
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, 'site', 'data', 'buildings.js')
SITE = os.path.join(ROOT, 'site')
dry = '--dry' in sys.argv

R = json.load(open(os.path.join(ROOT, 'tools', 'photos', 'resolved.json')))
text = open(DATA).read()
head, body = text.split('window.BUILDINGS = ', 1)
B = json.loads(body.rstrip().rstrip(';'))
local = lambda s: s and not s.startswith('http')
moved_th = moved_src = kept = 0
for b in B:
    ims = b.get('images', [])
    cover = next((k for k, im in enumerate(ims) if not im['src'].endswith('.svg')), None)
    for k, im in enumerate(ims):
        f = R.get(im.get('file') or '')
        if im['src'].endswith('.svg') or (im.get('file') or '').startswith('AIC:'):
            continue
        if not f or not f.get('w500') or not f.get('w1280'):
            kept += 1
            continue
        if k != cover and local(im['thumb']):
            im['thumb'] = f['w500']; moved_th += 1
        if local(im['src']):
            im['src'] = f['w1280']; moved_src += 1

used = {os.path.normpath(os.path.join(SITE, s)) for b in B for im in b.get('images', [])
        for s in (im['src'], im['thumb']) if local(s)}
ids = {b['id'] for b in B}
drop, size = [], 0
for i in sorted(ids):
    d = os.path.join(SITE, 'images', i)
    for sub in ('', 'thumbs'):
        p = os.path.join(d, sub)
        if not os.path.isdir(p):
            continue
        for n in os.listdir(p):
            fp = os.path.normpath(os.path.join(p, n))
            if n.endswith('.webp') and fp not in used:
                drop.append(fp); size += os.path.getsize(fp)
print(f'{moved_th} thumbnails and {moved_src} full photos now load from Wikimedia; {kept} photos stay here '
      f'(not found on Wikimedia). {len(drop)} files to delete, {size / 1e6:.0f} MB.')
if not dry:
    open(DATA, 'w').write(head + 'window.BUILDINGS = ' + json.dumps(B, ensure_ascii=False, indent=1) + ';\n')
    for fp in drop:
        os.remove(fp)
