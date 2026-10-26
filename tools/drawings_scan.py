#!/usr/bin/env python3
"""Find free drawings (plans, sections, elevations, sketches) on Wikimedia Commons for the most-studied buildings.

  python -u tools/drawings_scan.py --first 200            # the first 200 ids of tools/top1000.txt
  python -u tools/drawings_scan.py --first 200 --offset 200
  python -u tools/drawings_scan.py --ids villa-savoye,salk-institute
  python tools/drawings_scan.py --selftest                # layout check with dummy data, no network

Looks in three places for each building: its Commons category and sub-folders two levels down (folders named plan,
section, elevation, drawing, sketch, model, blueprint or HABS first), a Commons search for the name with
plan/section/elevation/drawing, and, for US buildings, HABS/HAER sheets (public domain).
A file is kept only if it is a drawing, has a free licence, is at least 700 px on its long side, is a JPEG, PNG, GIF
or TIFF (or a PDF/DjVu with a page thumbnail), and is not already in the building's gallery or skip list.

Writes tools/drawings/candidates.json ({id: [{file, kind, w, h, license, author, desc, cats, thumb}]}, at most 6 per
building, plans and sections first) and contact sheets tools/drawings/sheets/sheet_NN.jpg (8 buildings per sheet:
label, the current main photo, then d1..d6). See tools/drawings/BRIEF.md.
Needs network access to Wikimedia, so it runs on GitHub Actions (tools/run_request.txt).
"""
import argparse, io, json, re, sys, unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_images as fi  # noqa: E402  (api, members, infos, strip, describe, DRAWINGS, OK_LICENSE, fits, score)

ROOT = fi.ROOT
OUT = ROOT / 'tools' / 'drawings'
CANDS = OUT / 'candidates.json'
SHEETS = OUT / 'sheets'
TOP = ROOT / 'tools' / 'top1000.txt'
SITE = ROOT / 'site'

MAX_PER_BUILDING = 6
MAX_PER_KIND = 3  # first pass; the rest fill the remaining places
KIND_ORDER = ['Plan', 'Section', 'Elevation', 'Drawing', 'Sketch', 'Model']
MIN_PX = 700
ROWS_PER_SHEET = 8
TW, TH, LABEL_W, CAP_H = 250, 190, 150, 18  # thumbnail box, label column, caption strip
SHEET_MAX_BYTES = 450_000

DRAW_FOLDER = re.compile(r'(\bplans?\b|floor ?plan|section|elevation|drawing|sketch|\bmodels?\b|blueprint|\bHABS\b|\bHAER\b|'
                         r'Historic American|maquette|zeichnung|grundriss|schnitt|planta|plano|pianta|dessin|disegn|esbo|croquis|axonometr)', re.I)
DRAW_WORD = re.compile(r'(\bplans?\b|floor ?plan|section|elevation|drawing|sketch|blueprint|axonometr|\bsheet \d+ of \d+|measured drawing)', re.I)
BAD_FILE = re.compile(r'(logo|flag|coat of arms|\bseal\b|icon|\.svg$|stamp|banknote|\bcoin\b|poster|locator|\bmap\b|screenshot)', re.I)
HABS_WORDS = re.compile(r'(\bHABS\b|\bHAER\b|Historic American)', re.I)
OK_MIME = ('image/jpeg', 'image/png', 'image/gif', 'image/tiff')
PAGE_MIME = ('application/pdf', 'image/vnd.djvu', 'image/x.djvu', 'image/x-djvu')


def norm(t):
    return t.replace('_', ' ').strip()


# ---------- finding files ----------
def category_files(cat):
    """Files in the category plus drawing-named folders, two levels down. Returns [(title, folder hint)]."""
    found = [(t, '') for t in fi.members(cat, 'file')[:300]]
    plain = 0
    for sub in fi.members(cat, 'subcat')[:40]:
        hint = sub.split(':', 1)[1]
        if DRAW_FOLDER.search(hint):
            found += [(t, hint) for t in fi.members(sub, 'file')[:100]]
            for sub2 in fi.members(sub, 'subcat')[:15]:
                found += [(t, sub2.split(':', 1)[1]) for t in fi.members(sub2, 'file')[:60]]
        elif plain < 25:  # other folders (Interior, Exterior...): only their drawing-named sub-folders
            plain += 1
            for sub2 in fi.members(sub, 'subcat')[:20]:
                h2 = sub2.split(':', 1)[1]
                if DRAW_FOLDER.search(h2):
                    found += [(t, h2) for t in fi.members(sub2, 'file')[:60]]
    return found


def search_hits(b, query, hint):
    """Commons file search; keeps hits whose name or snippet names the building."""
    out = []
    q = fi.api(fi.CM, action='query', list='search', srnamespace=6, srlimit=30, srprop='snippet', srsearch=query)
    for h in q.get('query', {}).get('search', []):
        text = h['title'] + ' ' + re.sub(r'<[^>]+>', ' ', h.get('snippet', ''))
        if fi.fits(b, text):
            out.append((h['title'], hint))
    return out


def search_files(b):
    name = b['name'].replace('"', '')
    return search_hits(b, f'"{name}" plan OR section OR elevation OR drawing', 'search')


def habs_files(b):
    """HABS/HAER sheets of a US building (public domain): a file search and any HABS-named folder."""
    name = b['name'].replace('"', '')
    out = search_hits(b, f'"{name}" HABS OR HAER OR "Historic American Buildings Survey" sheet', 'HABS')
    q = fi.api(fi.CM, action='query', list='search', srnamespace=14, srlimit=5, srsearch=f'HABS "{name}"')
    for h in q.get('query', {}).get('search', []):
        if fi.fits(b, h['title']):
            out += [(t, 'HABS') for t in fi.members(h['title'], 'file')[:100]]
    return out


# ---------- judging files ----------
def kind_of(title, hint, meta, cats, city):
    """A drawing kind from the file name, folder, categories and description, or None if it is not a drawing."""
    k = fi.describe(title, hint, meta, cats, city)
    if k in fi.DRAWINGS:
        return k
    named = ' '.join([title, hint, cats])
    if fi.PHOTO_OF.search(title):
        return None
    if HABS_WORDS.search(named) and DRAW_WORD.search(named):
        return 'Drawing'
    return None


def split_cats(text):
    return [c.replace('Category:', '').strip() for c in re.split(r'\s(?=Category:)', text) if c.strip()]


def judge(b, files, info, gallery, skip):
    """Candidates from (title, hint) pairs and their Commons info, best first."""
    city = b['place'].split(',')[0]
    pool, seen = [], set()
    for t, hint in files:
        t = norm(t)
        if t in seen or t in gallery or t in skip:
            continue
        seen.add(t)
        if BAD_FILE.search(t) and not DRAW_WORD.search(t):
            continue
        i = info.get(t)
        if not i:
            continue
        mime = i.get('mime')
        if mime not in OK_MIME and not (mime in PAGE_MIME and i.get('thumburl')):
            continue
        w, h = i.get('width', 0), i.get('height', 0)
        if max(w, h) < MIN_PX or i.get('size', 0) > 60_000_000:
            continue
        meta = i.get('extmetadata', {})
        lic = fi.strip(meta.get('LicenseShortName')) or fi.strip(meta.get('UsageTerms'))
        if not fi.OK_LICENSE.search(lic):
            continue
        kind = kind_of(t, hint, meta, i.get('cats', ''), city)
        if not kind or kind == 'Model':  # first 200: nearly all "models" were photos of miniatures and Lego
            continue
        pool.append({'file': t, 'kind': kind, 's': fi.score(i, b, t) + (1 if hint == 'HABS' else 0), 'w': w, 'h': h, 'license': lic,
                     'author': fi.strip(meta.get('Artist'))[:100] or fi.strip(meta.get('Credit'))[:100],
                     'desc': re.sub(r'\s+', ' ', fi.strip(meta.get('ImageDescription')))[:120],
                     'cats': split_cats(i.get('cats', ''))[:6],
                     'thumb': i.get('thumburl') or i.get('url')})
    return choose(pool)


def choose(pool):
    """At most MAX_PER_BUILDING: plans and sections first, no more than MAX_PER_KIND of one kind on the first pass."""
    rank = {k: n for n, k in enumerate(KIND_ORDER)}
    pool = sorted(pool, key=lambda p: (rank.get(p['kind'], 9), -p['s']))
    first, count = [], {}
    for p in pool:
        if count.get(p['kind'], 0) < MAX_PER_KIND and len(first) < MAX_PER_BUILDING:
            first.append(p)
            count[p['kind']] = count.get(p['kind'], 0) + 1
    rest = [p for p in pool if p not in first]
    picks = sorted((first + rest)[:MAX_PER_BUILDING], key=lambda p: (rank.get(p['kind'], 9), -p['s']))
    return [{k: v for k, v in p.items() if k != 's'} for p in picks]


def scan_building(b, choices):
    ch = choices.get(b['id'], {})
    skip = {norm(x) for x in ch.get('skip', [])}
    gallery = {norm(i['file']) for i in b.get('images', []) if i.get('file')}
    cat = ch.get('category') or b.get('commons')
    if not cat:
        cat, _ = fi.commons_category(b)
    files = []
    for c in [cat] + list(ch.get('more', [])):
        if c:
            try:
                files += category_files(c)
            except Exception as e:
                print('    category failed:', c, e)
    for finder in [search_files] + ([habs_files] if b['place'].rstrip().endswith(', US') else []):
        try:
            files += finder(b)
        except Exception as e:
            print('    search failed:', finder.__name__, e)
    seen, uniq = set(), []
    for t, h in files:
        if norm(t) not in seen:
            seen.add(norm(t))
            uniq.append((t, h))
    uniq = uniq[:700]
    info = {norm(k): v for k, v in fi.infos([t for t, _ in uniq]).items()} if uniq else {}
    return judge(b, uniq, info, gallery, skip)


# ---------- contact sheets ----------
def main_photo(b):
    for i in b.get('images', []):
        th = i.get('thumb', '')
        if th and not th.endswith('.svg') and (SITE / th).exists():
            return SITE / th
    return None


def real_main(b):
    from PIL import Image
    p = main_photo(b)
    try:
        return Image.open(p).convert('RGB') if p else None
    except Exception:
        return None


def real_tile(url):
    from PIL import Image, ImageOps
    small = re.sub(r'(?<=[/-])\d+px-', '330px-', url) if 'px-' in url else url
    for u in dict.fromkeys([small, url]):
        try:
            return ImageOps.exif_transpose(Image.open(io.BytesIO(fi.fetch(u, timeout=120)))).convert('RGB')
        except Exception as e:
            print('    thumb failed:', e)
    return None


def box(im, caption, font):
    from PIL import Image, ImageDraw
    cell = Image.new('RGB', (TW, TH), (235, 235, 235))
    if im is not None:
        im = im.copy()
        im.thumbnail((TW - 2, TH - CAP_H - 2))
        cell.paste(im, ((TW - im.width) // 2, 1))
    d = ImageDraw.Draw(cell)
    d.rectangle([0, TH - CAP_H, TW, TH], fill=(255, 255, 255))
    d.text((3, TH - CAP_H + 3), ascii_text(caption)[:44], fill=(0, 0, 0), font=font)
    d.rectangle([0, 0, TW - 1, TH - 1], outline=(190, 190, 190))
    return cell


def ascii_text(t):
    """The sheet's built-in font has no accents or dashes."""
    return unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode()


def wrap(text, width):
    lines, line = [], ''
    for w in text.split():
        if len(line) + len(w) + 1 > width and line:
            lines.append(line)
            line = w
        else:
            line = (line + ' ' + w).strip()
    return lines + ([line] if line else [])


def save_under(sheet, path, limit=SHEET_MAX_BYTES):
    for q in (74, 68, 62, 56, 50, 44, 38):
        buf = io.BytesIO()
        sheet.save(buf, 'JPEG', quality=q, optimize=True)
        if buf.tell() <= limit:
            break
    path.write_bytes(buf.getvalue())
    return buf.tell()


def write_sheets(rows, first_number, tile_for, main_for, folder=None):
    """rows: [(index, building, [candidates])]. tile_for(url) and main_for(b) give PIL images (or None)."""
    from PIL import Image, ImageDraw, ImageFont
    folder = folder or SHEETS
    folder.mkdir(parents=True, exist_ok=True)
    try:
        font, big = ImageFont.load_default(size=11), ImageFont.load_default(size=12)
    except TypeError:
        font = big = ImageFont.load_default()
    for s in range(0, len(rows), ROWS_PER_SHEET):
        part = rows[s:s + ROWS_PER_SHEET]
        sheet = Image.new('RGB', (LABEL_W + 7 * TW, len(part) * TH), (255, 255, 255))
        d = ImageDraw.Draw(sheet)
        for r, (idx, b, cands) in enumerate(part):
            y = r * TH
            d.rectangle([0, y, LABEL_W - 1, y + TH - 1], outline=(190, 190, 190))
            for n, line in enumerate(wrap(ascii_text(f"{idx} {b['id']} - {b['name']}"), 22)[:11]):
                d.text((4, y + 4 + n * 14), line, fill=(0, 0, 0), font=big)
            sheet.paste(box(main_for(b), 'current main photo', font), (LABEL_W, y))
            for k in range(6):
                if k < len(cands):
                    c = cands[k]
                    cell = box(tile_for(c['thumb']), f"d{k + 1} {c['kind']} {c['w']}x{c['h']}", font)
                else:
                    cell = Image.new('RGB', (TW, TH), (250, 250, 250))
                sheet.paste(cell, (LABEL_W + (k + 1) * TW, y))
        path = folder / f'sheet_{first_number + s // ROWS_PER_SHEET:02d}.jpg'
        print(f'  {path.name}: {len(part)} buildings, {save_under(sheet, path) // 1024} KB', flush=True)


# ---------- main ----------
def load_buildings():
    t = fi.DATA.read_text(encoding='utf-8')
    return {b['id']: b for b in json.loads(t.split('window.BUILDINGS = ', 1)[1].rstrip().rstrip(';'))}


def selftest():
    """Parsing, filters, ranking and a sheet, with dummy data and no network."""
    import random
    from PIL import Image
    b = {'id': 'test-house', 'name': 'Test House', 'by': 'A. Architect', 'place': 'Plano, US'}
    meta = lambda lic: {'LicenseShortName': {'value': lic}, 'ImageDescription': {'value': 'x'}, 'Artist': {'value': 'Someone'}}
    def inf(w, h, lic='CC BY-SA 4.0', mime='image/jpeg', cats=''):
        return {'width': w, 'height': h, 'mime': mime, 'size': 1000, 'extmetadata': meta(lic), 'cats': cats, 'thumburl': 'https://x/1280px-a.jpg'}
    files = [(t, '') for t in ['File:Test House floor plan.jpg', 'File:Test House section A-A.png', 'File:Test House.jpg',
                               'File:Test House plan small.jpg', 'File:Test House elevation NC.jpg', 'File:Test House sketch.pdf',
                               'File:Test House logo.svg', 'File:Test House elevation north.jpg']]
    files += [('File:Test House HABS sheet 3 of 9.tif', 'HABS'), ('File:IMG 1.jpg', 'Floor plans of Test House')]
    info = {norm(t): inf(2000, 1500) for t, _ in files}
    info['File:Test House plan small.jpg'] = inf(500, 400)
    info['File:Test House elevation NC.jpg'] = inf(2000, 1500, 'CC BY-NC 4.0')
    info['File:Test House sketch.pdf'] = inf(2000, 1500, mime='application/pdf')
    info['File:Test House HABS sheet 3 of 9.tif'] = inf(3000, 2000, 'Public domain', 'image/tiff')
    info['File:IMG 1.jpg'] = inf(3000, 2000, cats='Category:Floor plans of Test House Category:Plano')
    got = judge(b, files, info, {'File:Test House section A-A.png'}, set())
    for c in got:
        print(' ', c['kind'], c['file'], c['cats'])
    names = [c['file'] for c in got]
    for bad in ('File:Test House section A-A.png', 'File:Test House plan small.jpg', 'File:Test House elevation NC.jpg',
                'File:Test House.jpg', 'File:Test House logo.svg'):
        assert bad not in names, bad
    for good in ('File:Test House floor plan.jpg', 'File:Test House HABS sheet 3 of 9.tif', 'File:IMG 1.jpg', 'File:Test House sketch.pdf'):
        assert good in names, good
    assert got[0]['kind'] == 'Plan' and got[-1]['kind'] in ('Sketch', 'Drawing', 'Elevation')
    print('judge ok;', len(got), 'kept')
    rows = [(i + 1, {'id': f'building-{i}', 'name': f'A rather long building name number {i}'},
             [dict(got[j % len(got)], w=2000, h=1500) for j in range(1 + i % 6)]) for i in range(11)]
    def tile(_=None):
        im = Image.new('RGB', (330, 240), tuple(random.randint(60, 255) for _ in range(3)))
        for _ in range(80):
            x, y = random.randint(0, 300), random.randint(0, 220)
            im.paste((0, 0, 0), (x, y, x + random.randint(2, 30), y + 2))
        return im
    out = Path('/tmp/drawings_selftest')
    write_sheets(rows, 1, tile, lambda b: tile(), out)
    print('sheets in', out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--first', type=int, default=200)
    ap.add_argument('--offset', type=int, default=0)
    ap.add_argument('--ids', default='')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    books = load_buildings()
    if a.ids:
        ids, offset = [x for x in a.ids.split(',') if x], 0
    else:
        top = [l.strip() for l in TOP.read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
        ids, offset = top[a.offset:a.offset + a.first], a.offset
    choices = json.loads(fi.CHOICES.read_text(encoding='utf-8')) if fi.CHOICES.exists() else {}
    OUT.mkdir(parents=True, exist_ok=True)
    result = json.loads(CANDS.read_text(encoding='utf-8')) if CANDS.exists() else {}
    scanned, with_c, total, rows = 0, 0, 0, []
    for n, bid in enumerate(ids):
        idx = offset + n + 1
        b = books.get(bid)
        if not b:
            print(f'{idx:4d} {bid}: not in buildings.js')
            continue
        scanned += 1
        try:
            cands = scan_building(b, choices)
        except Exception as e:
            print(f'{idx:4d} {bid}: failed {type(e).__name__}: {e}')
            cands = []
        result[bid] = cands
        if cands:
            with_c += 1
            total += len(cands)
            rows.append((idx, b, cands))
        print(f'{idx:4d} {bid}: {len(cands)} candidates ' + ' '.join(c['kind'][0] for c in cands), flush=True)
        if n % 10 == 9:
            CANDS.write_text(json.dumps(result, ensure_ascii=False, indent=0), encoding='utf-8')
    CANDS.write_text(json.dumps(result, ensure_ascii=False, indent=0), encoding='utf-8')
    print(f'scanned {scanned}, with candidates {with_c}, candidates {total}')
    first = (offset // 200) * 30 + 1 if not a.ids else 91  # sheets for each 200 get their own number range
    write_sheets(rows, first, real_tile, real_main)


if __name__ == '__main__':
    main()
