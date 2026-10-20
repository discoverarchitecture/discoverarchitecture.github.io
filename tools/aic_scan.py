#!/usr/bin/env python3
"""Find public-domain (CC0) works at the Art Institute of Chicago for the most-studied buildings.

  python -u tools/aic_scan.py --first 1000               # top1000.txt, plus every other US building on the wall
  python -u tools/aic_scan.py --first 200 --offset 200 --no-extra
  python -u tools/aic_scan.py --ids robie-house,wainwright-building
  python tools/aic_scan.py --selftest                    # matching rules and sheet layout with dummy data, no network

The museum's open API needs no key. For each building it asks for public-domain works by the building's name (and,
when that finds nothing, by name plus the architect's surname). A work is kept only if all of these hold:
  - is_public_domain is true and image_id is set;
  - its classification or department says architecture, drawing, print, photograph or model (objects such as
    fragments, furniture and glass are dropped);
  - its title names the building, or names the architect together with a word from the building's name.
Writes tools/aic/candidates.json ({id: [{aic_id, title, artist, date, classification, image_id, page, iiif}]}, at most
6 per building) and contact sheets tools/aic/sheets/sheet_NN.jpg (8 buildings per sheet: label, the current main
photo, then a1..a6). See tools/aic/BRIEF.md. Works for any building on the wall: credit "Art Institute of Chicago"
and link `page`.
Needs network access to api.artic.edu and www.artic.edu, so it runs on GitHub Actions (tools/run_request.txt).
"""
import argparse, io, json, re, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_images as fi  # noqa: E402  (tokens, GENERIC, distinctive, DATA, CHOICES, ROOT)
import drawings_scan as ds  # noqa: E402  (box, wrap, ascii_text, save_under, main_photo, real_main, sheet sizes)

ROOT = fi.ROOT
OUT = ROOT / 'tools' / 'aic'
CANDS = OUT / 'candidates.json'
SUMMARY = OUT / 'summary.json'
SHEETS = OUT / 'sheets'
TOP = ROOT / 'tools' / 'top1000.txt'

UA = 'FindGreatArchitecture/0.1 (https://findgreatarchitecture.com; architecture study site; contact via GitHub discoverarchitecture)'
API = 'https://api.artic.edu/api/v1/artworks/search'
FIELDS = 'id,title,artist_title,date_display,classification_title,department_title,image_id,thumbnail,is_public_domain'
IIIF = 'https://www.artic.edu/iiif/2/{}/full/{}/0/default.jpg'
PAUSE = 1.0
MAX_PER_BUILDING = 6
ROWS_PER_SHEET = 8
TW, TH = 280, 215  # thumbnail box on the sheets (the shared tools/drawings_scan.py cell is a bit smaller)

OK_CLASS = re.compile(r'(architectur|drawing|print|photograph|model)', re.I)
DRAWINGLIKE = re.compile(r'(drawing|print|photograph|model|plan|elevation|section|sketch|rendering|perspective)', re.I)
OBJECT_CLASS = re.compile(r'(fragment|furniture|chair|table|ceramic|glass|metalwork|sculpture|textile|decorative|ornament|'
                          r'\btile|vessel|mosaic|lighting|lamp|clock|silver|jewelry|costume|woodwork|plaster|terracotta|'
                          r'stained|carving|panel|architectural element|architectural model fragment)', re.I)


# ---------- HTTP ----------
def fetch(url, timeout=60):
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'AIC-User-Agent': UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
            time.sleep(PAUSE)
            return data
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == 5:
                raise
            wait = int(e.headers.get('Retry-After') or 0) or min(60, 2 ** (attempt + 2))
            print(f'    {e.code}, retrying in {wait}s')
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt == 5:
                raise
            print(f'    {type(e).__name__}, retrying')
            time.sleep(5 * (attempt + 1))


def search(q):
    params = {'q': q, 'query[term][is_public_domain]': 'true', 'fields': FIELDS, 'limit': 15}
    return json.loads(fetch(API + '?' + urllib.parse.urlencode(params), timeout=30)).get('data', [])


# ---------- matching ----------
def words(text):
    return fi.tokens(text)


def name_variants(b):
    """The building's name, and each part when it has a bracketed or slashed second name."""
    raw = b['name']
    parts = [raw] + [p.strip() for p in re.split(r'[()/]|\s[–—-]\s', raw) if p.strip()]
    return list(dict.fromkeys(parts))


def phrase(text):
    t = fi.unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower()
    return ' '.join(re.findall(r'[a-z0-9]+', t))


def surnames(by):
    out = set()
    for part in re.split(r'\s(?:and|&|with|\+)\s|[,;/&]', by or ''):
        w = [x for x in words(part) if x not in ('and', 'the', 'associates', 'partners', 'company', 'office')]
        toks = re.findall(r'[A-Za-zÀ-ɏ\'-]+', part)
        if toks:
            last = list(words(toks[-1]))
            out |= set(last)
    return out - fi.GENERIC


def title_match(b, title):
    """3 = the whole name is in the title, 2 = every distinctive word is, 0 = no (an architect-plus-word match is separate)."""
    t = ' ' + phrase(title) + ' '
    for v in name_variants(b):
        p = phrase(v)
        if len(p) >= 4 and f' {p} ' in t:
            return 3
    tt = words(title)
    for v in name_variants(b):
        d = words(v) - fi.GENERIC - words(b['place']) - words(b['by'])
        if d and d <= tt:
            return 2
    return 0


def artist_match(b, artist):
    s = surnames(b['by'])
    return bool(s and s & words(artist or ''))


def word_match(b, title):
    d = fi.distinctive(b) or words(b['name']) - fi.GENERIC
    return bool(d & words(title))


def judge(b, hits):
    """Keep the works that pass the brief's rules, best first, at most 6. hits: AIC search results (dicts)."""
    kept, seen = [], set()
    for h in hits:
        aid = h.get('id')
        if aid in seen or not aid:
            continue
        seen.add(aid)
        if h.get('is_public_domain') is not True or not h.get('image_id'):
            continue
        cls = (h.get('classification_title') or '')
        kinds = cls + ' ' + (h.get('department_title') or '')
        if not OK_CLASS.search(kinds):
            continue
        if OBJECT_CLASS.search(cls) and not DRAWINGLIKE.search(cls):
            continue
        title = h.get('title') or ''
        tm = title_match(b, title)
        am = artist_match(b, h.get('artist_title'))
        if not tm and not (am and word_match(b, title)):
            continue
        rank = (tm or 1) * 2 + (1 if am else 0) + (1 if DRAWINGLIKE.search(cls) else 0) \
            + (1 if (h.get('department_title') or '').lower().startswith('architecture') else 0)
        thumb = h.get('thumbnail') or {}
        kept.append((rank, {
            'aic_id': aid, 'title': title[:160], 'artist': (h.get('artist_title') or '')[:100],
            'date': (h.get('date_display') or '')[:40], 'classification': cls,
            'image_id': h['image_id'], 'page': f'https://www.artic.edu/artworks/{aid}',
            'iiif': IIIF.format(h['image_id'], '843,'),
            'w': thumb.get('width') or 0, 'h': thumb.get('height') or 0,
        }))
    kept.sort(key=lambda x: -x[0])
    return [c for _, c in kept[:MAX_PER_BUILDING]]


def scan_building(b):
    name = re.sub(r'\s*\(.*?\)', '', b['name']).strip() or b['name']
    cands = judge(b, search(name))
    if not cands:
        s = sorted(surnames(b['by']))
        if s:
            cands = judge(b, search(f'{name} {s[-1]}'))
    return cands


# ---------- contact sheets ----------
def real_thumb(c):
    from PIL import Image, ImageOps
    for size in ('400,', '843,'):
        try:
            return ImageOps.exif_transpose(Image.open(io.BytesIO(fetch(IIIF.format(c['image_id'], size), timeout=120)))).convert('RGB')
        except Exception as e:
            print('    thumb failed:', c['aic_id'], size, e)
    return None


def write_sheets(rows, first_number, tile_for, main_for, folder=None):
    """rows: [(index, building, [candidates])]. tile_for(candidate) and main_for(b) give PIL images (or None)."""
    from PIL import Image, ImageDraw, ImageFont
    folder = folder or SHEETS
    folder.mkdir(parents=True, exist_ok=True)
    try:
        font, big = ImageFont.load_default(size=11), ImageFont.load_default(size=12)
    except TypeError:
        font = big = ImageFont.load_default()
    LW = ds.LABEL_W
    for s in range(0, len(rows), ROWS_PER_SHEET):
        part = rows[s:s + ROWS_PER_SHEET]
        sheet = Image.new('RGB', (LW + 7 * TW, len(part) * TH), (255, 255, 255))
        d = ImageDraw.Draw(sheet)
        for r, (idx, b, cands) in enumerate(part):
            y = r * TH
            d.rectangle([0, y, LW - 1, y + TH - 1], outline=(190, 190, 190))
            for n, line in enumerate(ds.wrap(ds.ascii_text(f"{idx} {b['id']} - {b['name']}"), 22)[:11]):
                d.text((4, y + 4 + n * 14), line, fill=(0, 0, 0), font=big)
            sheet.paste(cell(main_for(b), 'current main photo', font), (LW, y))
            for k in range(6):
                if k < len(cands):
                    c = cands[k]
                    label = f"a{k + 1} {c['classification'] or 'work'} {c['date']}"
                    img = cell(tile_for(c), label, font)
                    sheet.paste(img, (LW + (k + 1) * TW, y))
                    d.text((LW + (k + 1) * TW + 3, y + 2), ds.ascii_text(c['title'])[:46], fill=(120, 0, 0), font=font)
                else:
                    sheet.paste(Image.new('RGB', (TW, TH), (250, 250, 250)), (LW + (k + 1) * TW, y))
        path = folder / f'sheet_{first_number + s // ROWS_PER_SHEET:02d}.jpg'
        print(f'  {path.name}: {len(part)} buildings, {ds.save_under(sheet, path) // 1024} KB', flush=True)


def cell(im, caption, font):
    from PIL import Image, ImageDraw
    c = Image.new('RGB', (TW, TH), (235, 235, 235))
    if im is not None:
        im = im.copy()
        im.thumbnail((TW - 2, TH - ds.CAP_H - 16))
        c.paste(im, ((TW - im.width) // 2, 15))
    d = ImageDraw.Draw(c)
    d.rectangle([0, TH - ds.CAP_H, TW, TH], fill=(255, 255, 255))
    d.text((3, TH - ds.CAP_H + 3), ds.ascii_text(caption)[:46], fill=(0, 0, 0), font=font)
    d.rectangle([0, 0, TW - 1, TH - 1], outline=(190, 190, 190))
    return c


# ---------- main ----------
def selftest():
    """Matching rules and a sheet, with dummy data and no network."""
    import random
    from PIL import Image
    b = {'id': 'robie-house', 'name': 'Robie House', 'by': 'Frank Lloyd Wright', 'place': 'Chicago, US'}
    g = {'id': 'guaranty-building', 'name': 'Guaranty Building (Prudential Building)', 'by': 'Adler & Sullivan', 'place': 'Buffalo, US'}
    def h(i, title, artist='Frank Lloyd Wright', cls='Architectural drawing', dept='Architecture and Design', img='abc', pd=True):
        return {'id': i, 'title': title, 'artist_title': artist, 'date_display': '1909', 'classification_title': cls,
                'department_title': dept, 'image_id': img, 'is_public_domain': pd, 'thumbnail': {'width': 800, 'height': 600}}
    hits = [
        h(1, 'Frederick C. Robie House, Chicago, Illinois, Plan'),                       # whole name missing, "Robie House" present -> 3
        h(2, 'Robie House: Perspective'),                                               # 3
        h(3, 'Sketch for Robie house'),                                                 # 3 (case)
        h(4, 'Perspective, Robie', cls='Drawing'),                                      # architect + word -> kept
        h(5, 'Perspective, Robie', artist='Someone Else', cls='Drawing'),              # wrong architect, no name -> dropped
        h(6, 'Robie House window', cls='Stained glass', dept='Architecture and Design'),   # object -> dropped
        h(7, 'Robie House', cls='Photograph', dept='Photography', pd=False),           # not public domain -> dropped
        h(8, 'Robie House', img=None),                                                  # no image -> dropped
        h(9, 'Robie House', cls='Chair', dept='Textiles'),                             # classification fails -> dropped
        h(10, 'Dana House Elevation'),                                                  # other project -> dropped
        h(11, 'Robie House, Print', cls='Print', dept='Prints and Drawings', artist='Unknown'),   # name only -> kept
        h(12, 'Plan of a House for Mr Robie', cls='Architectural drawing'),             # architect + word ('robie') -> kept
        h(1, 'Duplicate of 1'),
    ]
    got = judge(b, hits)
    ids = [c['aic_id'] for c in got]
    print('robie:', ids)
    for good in (1, 2, 3, 4, 11, 12):
        assert good in ids, good
    for bad in (5, 6, 7, 8, 9, 10):
        assert bad not in ids, bad
    assert len(ids) == len(set(ids))
    assert got[0]['page'] == 'https://www.artic.edu/artworks/%d' % got[0]['aic_id']
    assert got[0]['iiif'] == 'https://www.artic.edu/iiif/2/abc/full/843,/0/default.jpg'
    gh = [h(21, 'Guaranty Building, Buffalo, Elevation', artist='Louis Henry Sullivan'),
          h(22, 'Prudential Building, Section', artist='Adler & Sullivan'),
          h(23, 'Elevation, Meyer Building', artist='Louis Henry Sullivan'),
          h(24, 'Stock Exchange Building', artist='Adler & Sullivan')]
    gi = [c['aic_id'] for c in judge(g, gh)]
    print('guaranty:', gi)
    assert 21 in gi and 22 in gi and 23 not in gi and 24 not in gi
    assert len(judge(b, [h(100 + i, f'Robie House {i}') for i in range(12)])) == MAX_PER_BUILDING
    print('judge ok')
    rows = [(i + 1, {'id': f'building-{i}', 'name': f'A rather long building name number {i}'},
             [dict(got[j % len(got)], date='1909') for j in range(1 + i % 6)]) for i in range(11)]
    def tile(_=None):
        im = Image.new('RGB', (400, 300), tuple(random.randint(60, 255) for _ in range(3)))
        for _ in range(100):
            x, y = random.randint(0, 370), random.randint(0, 280)
            im.paste((0, 0, 0), (x, y, x + random.randint(2, 30), y + 2))
        return im
    out = Path('/tmp/aic_selftest')
    write_sheets(rows, 1, tile, lambda b: tile(), out)
    print('sheets in', out)


def load_buildings():
    t = fi.DATA.read_text(encoding='utf-8')
    return json.loads(t.split('window.BUILDINGS = ', 1)[1].rstrip().rstrip(';'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--first', type=int, default=1000)
    ap.add_argument('--offset', type=int, default=0)
    ap.add_argument('--ids', default='')
    ap.add_argument('--no-extra', action='store_true', help='skip the other US buildings (they are added when offset is 0)')
    ap.add_argument('--sheet-start', type=int, default=1)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    allb = load_buildings()
    books = {b['id']: b for b in allb}
    if a.ids:
        ids = [x for x in a.ids.split(',') if x]
    else:
        top = [l.strip() for l in TOP.read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
        ids = top[a.offset:a.offset + a.first]
        if a.offset == 0 and not a.no_extra:
            have = set(top)
            ids += [b['id'] for b in allb if b['place'].rstrip().endswith(', US') and b['id'] not in have]
    OUT.mkdir(parents=True, exist_ok=True)
    result = json.loads(CANDS.read_text(encoding='utf-8')) if CANDS.exists() else {}
    searched, with_c, total, rows = 0, 0, 0, []
    for n, bid in enumerate(ids):
        b = books.get(bid)
        if not b:
            print(f'{n + 1:4d} {bid}: not in buildings.js')
            continue
        searched += 1
        try:
            cands = scan_building(b)
        except Exception as e:
            print(f'{n + 1:4d} {bid}: failed {type(e).__name__}: {e}')
            cands = []
        result[bid] = cands
        if cands:
            with_c += 1
            total += len(cands)
            rows.append((n + 1, b, cands))
        print(f'{n + 1:4d} {bid}: {len(cands)} works ' + ' | '.join(c['title'][:40] for c in cands[:3]), flush=True)
        if n % 25 == 24:
            CANDS.write_text(json.dumps(result, ensure_ascii=False, indent=0), encoding='utf-8')
    CANDS.write_text(json.dumps(result, ensure_ascii=False, indent=0), encoding='utf-8')
    SUMMARY.write_text(json.dumps({'searched': searched, 'with_hits': with_c, 'works': total}, indent=1), encoding='utf-8')
    print(f'searched {searched}, with hits {with_c}, works {total}')
    write_sheets(rows, a.sheet_start, real_thumb, ds.real_main)


if __name__ == '__main__':
    main()
