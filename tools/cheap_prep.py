#!/usr/bin/env python3
"""Prepare candidate buildings for a cheap model to judge (the Haiku experiment, 20 Oct 2026).

  python -u tools/cheap_prep.py tools/cheap/pool.json --n 60

Network work runs here, on GitHub Actions, so the model reading the result never browses: for each candidate
(a Wikidata harvest row: qid, label, enwiki, architect, inception, country, coords, commons, image) it saves the
English Wikipedia lead (up to 900 characters) and up to six free photos from the building's own Commons category,
rated photos (Featured, Quality, Valued) first, with licence, size, description and categories. A row marked
"fill": true (from the scored list, without the harvest's facts) first gets them from Wikidata. It writes
tools/cheap/prep.json and contact sheets tools/cheap/sheets/sheet_NN.jpg (8 buildings each: Wikidata's main
photo, then the candidates p1 to p6).
"""
import argparse, io, json, sys, time, urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_images import api, fetch, members, infos, strip, OK_LICENSE, JUNK, CM  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'tools' / 'cheap'
WP = 'https://en.wikipedia.org/w/api.php'


def lead_text(title):
    if not title:
        return ''
    q = api(WP, action='query', prop='extracts', exintro=1, explaintext=1, titles=title, redirects=1)
    pages = q.get('query', {}).get('pages', [])
    page = pages[0] if isinstance(pages, list) and pages else next(iter(pages.values()), {}) if isinstance(pages, dict) else {}
    return ' '.join((page.get('extract') or '').split())[:900]


def rating(meta):
    a = strip(meta.get('Assessments')).lower()
    return 'F' if ('featured' in a or 'poty' in a) else 'Q' if 'quality' in a else 'V' if 'valued' in a else ''


def photos(r):
    cat = 'Category:' + (r.get('commons') or [''])[0]
    files = [t for t in members(cat, 'file')][:150]
    main = 'File:' + r['image'][0] if r.get('image') else None
    if main and main not in files:
        files.insert(0, main)
    info = infos(files)
    out = []
    for t in files:
        i = info.get(t)
        if not i or i.get('mime') not in ('image/jpeg', 'image/png'):
            continue
        meta = i.get('extmetadata', {})
        lic = strip(meta.get('LicenseShortName')) or strip(meta.get('UsageTerms'))
        if not OK_LICENSE.search(lic) or max(i.get('width', 0), i.get('height', 0)) < 1200:
            continue
        desc = ' '.join(strip(meta.get('ImageDescription')).split())[:160]
        out.append({'file': t, 'rating': rating(meta), 'w': i['width'], 'h': i['height'], 'license': lic,
                    'author': strip(meta.get('Artist'))[:80], 'desc': desc, 'cats': i.get('cats', '')[:200],
                    'junk': bool(JUNK.search(t + ' ' + desc)), 'main': t == main, 'thumb': i.get('thumburl')})
    out.sort(key=lambda p: (not p['main'], p['rating'] == '', p['junk'], -(p['w'] * p['h'])))
    return out[:7]


def sheets(rows):
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
    except OSError:
        font = ImageFont.load_default()
    (OUT / 'sheets').mkdir(parents=True, exist_ok=True)
    W, H, PER = 240, 180, 8
    for s in range(0, len(rows), PER):
        chunk = rows[s:s + PER]
        sheet = Image.new('RGB', (W * 7, (H + 18) * len(chunk)), 'white')
        d = ImageDraw.Draw(sheet)
        for k, r in enumerate(chunk):
            y = k * (H + 18)
            d.text((4, y + 2), f"{s + k}  {r['label']} — {', '.join(r.get('architect') or [])[:40]} ({r.get('year')})", fill='black', font=font)
            for c, p in enumerate(r['photos'][:7]):
                try:
                    url = p['thumb'].replace('/1280px-', '/330px-') if p.get('thumb') else None
                    im = Image.open(io.BytesIO(fetch(url, timeout=60))).convert('RGB')
                    im.thumbnail((W - 6, H - 4))
                    sheet.paste(im, (c * W + 2, y + 18))
                except Exception:
                    d.text((c * W + 10, y + 80), 'no thumb', fill='red', font=font)
                d.rectangle([c * W + 2, y + 18, c * W + 44, y + 34], fill='white')
                d.text((c * W + 5, y + 19), ('main' if p['main'] else f'p{c}') + (' ' + p['rating'] if p['rating'] else ''), fill='black', font=font)
                time.sleep(0.4)
        sheet.save(OUT / 'sheets' / f'sheet_{s // PER:02d}.jpg', quality=78)


def fill(pool):
    """Fetches the harvest's facts for rows that only carry a qid, name and architect."""
    from harvest import entities, labels
    todo = [r['qid'] for r in pool if r.get('fill')]
    if not todo:
        return
    recs = entities(todo)
    refs = {v for r in recs.values() for key in ('architect', 'country', 'located', 'instance')
            for v in r.get(key, []) if isinstance(v, str) and v.startswith('Q')}
    names = labels(refs)
    for r in pool:
        rec = recs.get(r['qid']) if r.get('fill') else None
        if rec:
            for key in ('architect', 'country', 'located', 'instance'):
                if key in rec:
                    rec[key] = [names.get(v, v) if isinstance(v, str) else v for v in rec[key]]
            r.update({k: v for k, v in rec.items() if v and k != 'qid'})
    print(len(recs), 'rows filled from Wikidata', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pool')
    ap.add_argument('--n', type=int, default=60)
    a = ap.parse_args()
    pool = json.loads((ROOT / a.pool).read_text(encoding='utf-8'))[:a.n]
    fill(pool)
    rows = []
    for k, r in enumerate(pool):
        try:
            r = {key: r.get(key) for key in ('qid', 'label', 'enwiki', 'architect', 'year', 'country', 'located', 'coords', 'commons', 'instance', 'sitelinks')}
            r['lead'] = lead_text(r.get('enwiki'))
            r['photos'] = photos(pool[k])
            rows.append(r)
            print(k, r['label'], len(r['photos']), 'photos', flush=True)
        except Exception as e:
            print(k, 'failed:', e, flush=True)
        time.sleep(0.5)
    OUT.mkdir(exist_ok=True)
    (OUT / 'prep.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    sheets(rows)
    print(len(rows), 'prepared')


if __name__ == '__main__':
    main()
