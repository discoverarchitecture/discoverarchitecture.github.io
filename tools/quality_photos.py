#!/usr/bin/env python3
"""Find Commons' best-rated photos (Featured, Quality, Valued) for buildings already on the wall.

  python -u tools/quality_photos.py --first 300            # buildings 1..300 by n
  python -u tools/quality_photos.py --first 300 --offset 300
  python -u tools/quality_photos.py --ids fallingwater,sangath
  python tools/quality_photos.py --selftest                # offline checks, no network

Looks in each building's Commons category, its sub-folders one level down, and Wikidata's main image
(P18). Keeps rated, free, large JPEG/PNG files that are not already in the gallery, not skipped or
removed by hand, not people/events/artworks/signs/night, and that belong to this building.

Writes tools/quality/candidates.json and contact sheets tools/quality/sheets/sheet_NN.jpg.
Needs network access (run it on Actions via tools/run_request.txt) and Pillow for the sheets.
The Opus data-collection chat looks at the sheets; nothing here changes site/.
"""
import argparse, io, json, re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_images as fi  # api, members, candidate_files, batches, strip, OK_LICENSE, JUNK, SURROUNDINGS, tokens, fits, describe

ROOT = fi.ROOT
OUT = ROOT / 'tools' / 'quality'
SHEETS = OUT / 'sheets'
MIN_LONG = 1600
KEEP_PER_BUILDING = 10   # stored in candidates.json
ON_SHEET = 6             # shown on the contact sheet (c1..c6)
PER_SHEET = 10
TW, TH = 280, 190        # thumbnail box on the sheets
GAP, LABEL_H = 14, 20
SHEET_MAX_BYTES = 400_000

NIGHT = re.compile(r'(\bnight|nacht\b|nocturn|\bnuit\b|\bnoche\b|\bnotte\b|\bdusk\b|illuminat|floodlit|fireworks)', re.I)
PEOPLE_EVENT = re.compile(r'(\bpeople\b|\bcrowds?\b|\bvisitors?\b|\btourists?\b|\bstudents?\b|\bwoman\b|\bwomen\b|\bman\b|\bmen\b|\bgirls?\b|\bboys?\b|\bchild(ren)?\b|'
                          r'\baudience\b|\bpeformance\b|\bperformance\b|\bevent\b|\bfair\b|\bparade\b|\bmarathon\b|\bdemonstration\b|\bcelebration\b|\bopening\b)', re.I)
ARTWORK = re.compile(r'(\bpaintings?\b|\bsculptures?\b|\bstatues?\b|\bmurals?\b|\bfrescos?\b|\bstained glass\b|\btapestry\b|\bartwork\b|\binstallation\b|\bposter\b|\bexhibit\b)', re.I)
BAD_CATS = re.compile(r'(night|events? (in|at)|people|crowd|artworks?|paintings? |sculptures? )', re.I)


def norm(t):
    """File titles compared with spaces, not underscores."""
    return t.replace('_', ' ').strip()


def rating(assess):
    """'F', 'Q' or 'V' from the Assessments extmetadata text, or None."""
    a = (assess or '').lower()
    if 'featured' in a or 'poty' in a:
        return 'F'
    if 'quality' in a:
        return 'Q'
    if 'valued' in a:
        return 'V'
    return None


def junk_reason(title, desc, cats):
    """Why a file is not wanted (people, events, artworks, signs, night, junk), or None."""
    text = f'{title} {desc}'
    if fi.JUNK.search(text) or fi.JUNK.search(cats):
        return 'junk'
    if NIGHT.search(text) or NIGHT.search(cats):
        return 'night'
    if PEOPLE_EVENT.search(text):
        return 'people/event'
    if ARTWORK.search(text):
        return 'artwork'
    if BAD_CATS.search(cats):
        return 'category'
    return None


def belongs(b, title, desc, cats, direct, p18):
    """Guard against a wrong Commons category: the file must be the P18 image, sit directly in the
    building's category, or its own name/description/categories must name the building or its city."""
    if p18:
        return 'p18'
    text = f'{title} {desc} {cats}'
    if fi.fits(b, text):
        return 'names'
    city = b['place'].split(',')[0].strip()
    if city and re.search(r'\b' + re.escape(city) + r'\b', text, re.I):
        return 'city' if not direct else 'direct'
    if direct:
        return 'direct'
    return None


def judge(b, title, info, direct=False, p18=False, taken=frozenset()):
    """One file: returns a candidate dict, or (None, reason) when it is not wanted."""
    if norm(title) in taken:
        return None, 'already have'
    meta = info.get('extmetadata', {})
    rate = rating(fi.strip(meta.get('Assessments')))
    if not rate:
        return None, 'not rated'
    lic = fi.strip(meta.get('LicenseShortName')) or fi.strip(meta.get('UsageTerms'))
    if not fi.OK_LICENSE.search(lic):
        return None, 'licence'
    if info.get('mime') not in ('image/jpeg', 'image/png'):
        return None, 'type'
    w, h = info.get('width', 0), info.get('height', 0)
    if max(w, h) < MIN_LONG:
        return None, 'small'
    desc = fi.strip(meta.get('ImageDescription'))
    cats = info.get('cats', '')
    why = junk_reason(title, desc, cats)
    if why:
        return None, why
    own = belongs(b, title, desc, cats, direct, p18)
    if not own:
        return None, 'other building?'
    return {'file': norm(title), 'rating': rate, 'w': w, 'h': h, 'license': lic, 'desc': desc[:120],
            'cats': [c.replace('Category:', '', 1).strip() for c in re.split(r'\s(?=Category:)', cats) if c.strip()][:6],
            'kind': fi.describe(title, '', meta, cats, b['place'].split(',')[0]), 'why_kept': own}, None


def rank(c):
    return ({'F': 0, 'Q': 1, 'V': 2}[c['rating']], -(c['w'] * c['h']))


# ---------- Commons ----------
def rated_infos(titles):
    """imageinfo + visible categories for files; only the fields we need, no thumbnails."""
    out = {}
    for group in fi.batches(titles):
        q = fi.api(fi.CM, action='query', titles='|'.join(group), prop='imageinfo|categories', iiprop='url|size|mime|extmetadata',
                   iiextmetadatafilter='Assessments|LicenseShortName|UsageTerms|ImageDescription', clshow='!hidden', cllimit='max')
        for p in q.get('query', {}).get('pages', []):
            if 'imageinfo' in p:
                out[norm(p['title'])] = {**p['imageinfo'][0], 'cats': ' '.join(c['title'] for c in p.get('categories', []))}
    return out


def thumb_urls(titles, width=330):
    out = {}
    for group in fi.batches(titles):
        q = fi.api(fi.CM, action='query', titles='|'.join(group), prop='imageinfo', iiprop='url', iiurlwidth=width)
        for p in q.get('query', {}).get('pages', []):
            if 'imageinfo' in p:
                out[norm(p['title'])] = p['imageinfo'][0].get('thumburl') or p['imageinfo'][0].get('url')
    return out


def p18(qid):
    try:
        c = fi.api(fi.WD, action='wbgetclaims', entity=qid, property='P18')
        return ['File:' + x['mainsnak']['datavalue']['value'] for x in c.get('claims', {}).get('P18', []) if x['mainsnak'].get('datavalue')]
    except Exception as e:
        print('    wikidata P18 failed:', e)
        return []


def retry(fn, *a, tries=3):
    for i in range(tries):
        try:
            return fn(*a)
        except Exception as e:
            print(f'    attempt {i + 1} failed: {str(e)[:100]}')
            time.sleep(5 * (i + 1))
    raise RuntimeError('gave up')


# ---------- data ----------
def load_buildings():
    t = (ROOT / 'site' / 'data' / 'buildings.js').read_text(encoding='utf-8')
    return json.loads(t[t.index('['):t.rindex(']') + 1])


def hand_lists():
    choices = json.loads((ROOT / 'tools' / 'image_choices.json').read_text(encoding='utf-8'))
    review = json.loads(fi.HAND_REVIEW.read_text(encoding='utf-8')) if fi.HAND_REVIEW.exists() else {}
    removed = {}
    for r in review.get('remove', []):
        removed.setdefault(r['id'], set()).add(norm(r['file']))
    return choices, removed


def lead_of(b):
    """(file, image dict) of the current main photo: the first image that has a Commons file."""
    for im in b.get('images', []):
        if im.get('file') and im.get('kind') not in fi.DRAWINGS and not str(im.get('thumb', '')).endswith('.svg'):
            return norm(im['file']), im
    return (norm(b['lead']) if b.get('lead') else None), None


def scan(b, choices, removed):
    ch = choices.get(b['id'], {})
    cat = ch.get('category') or b.get('commons')
    taken = {norm(i['file']) for i in b.get('images', []) if i.get('file')}
    lead, _ = lead_of(b)
    if b.get('lead'):
        taken.add(norm(b['lead']))
    taken |= {norm(s) for s in ch.get('skip', [])} | removed.get(b['id'], set())
    files = []  # (title, direct, p18)
    seen = set()
    if cat:
        for c in [cat] + ch.get('more', []):
            for t, hint in fi.candidate_files(c):
                if norm(t) not in seen:
                    seen.add(norm(t))
                    files.append((t, hint == '', False))
    if b.get('qid'):
        for t in p18(b['qid']):
            if norm(t) in seen:
                files = [(x, d, True if norm(x) == norm(t) else p) for x, d, p in files]
            else:
                seen.add(norm(t))
                files.append((t, False, True))
    titles = [t for t, _, _ in files] + ([lead] if lead else [])
    info = rated_infos(titles) if titles else {}
    lead_rated = bool(lead and lead in info and rating(fi.strip(info[lead].get('extmetadata', {}).get('Assessments'))))
    found, why = [], {}
    for t, direct, is18 in files:
        i = info.get(norm(t))
        if not i:
            continue
        c, reason = judge(b, t, i, direct, is18, taken)
        if c:
            found.append(c)
        else:
            why[reason] = why.get(reason, 0) + 1
    found.sort(key=rank)
    return {'lead': lead, 'lead_rated': lead_rated, 'found': found[:KEEP_PER_BUILDING], 'category': cat,
            'category_fits': bool(cat and fi.fits(b, cat)), 'scanned': len(files)}, why


# ---------- sheets ----------
def font(size):
    from PIL import ImageFont
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def fetch_thumb(url, local=None):
    from PIL import Image, ImageOps
    try:
        if local and Path(local).exists():
            im = Image.open(local)
        else:
            im = Image.open(io.BytesIO(fi.fetch(url, timeout=120)))
        im = ImageOps.exif_transpose(im).convert('RGB')
        im.thumbnail((TW, TH))
        return im
    except Exception as e:
        print('    thumb failed:', str(e)[:80])
        return None


def build_sheet(rows, path):
    """rows: [(label, lead_img or None, [(tag, img or None), ...])] -> one JPEG under SHEET_MAX_BYTES."""
    from PIL import Image, ImageDraw
    col = TW + GAP
    row_h = LABEL_H + TH + 6
    sheet = Image.new('RGB', (col * (1 + ON_SHEET) + GAP, row_h * len(rows) + 4), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    f, small = font(15), font(13)
    for r, (label, lead, cands) in enumerate(rows):
        y = r * row_h + 4
        d.text((6, y), label, fill=(0, 0, 0), font=f)
        d.rectangle([0, y + 1, 3, y + LABEL_H + TH], fill=(218, 58, 38))
        for k, (tag, im) in enumerate([('main', lead)] + list(cands)):
            x = GAP + k * col + (GAP // 2 if k else 0)  # a wider gap after the current main photo
            box = (x, y + LABEL_H)
            d.rectangle([box[0], box[1], box[0] + TW, box[1] + TH], fill=(235, 235, 235))
            if im:
                sheet.paste(im, (box[0] + (TW - im.width) // 2, box[1] + (TH - im.height) // 2))
            d.rectangle([box[0], box[1], box[0] + len(tag) * 8 + 8, box[1] + 16], fill=(255, 255, 255))
            d.text((box[0] + 3, box[1] + 1), tag, fill=(0, 0, 0), font=small)
    SHEETS.mkdir(parents=True, exist_ok=True)
    for q in (80, 72, 64, 56, 48, 40):
        buf = io.BytesIO()
        sheet.save(buf, 'JPEG', quality=q, optimize=True)
        if buf.tell() <= SHEET_MAX_BYTES:
            break
    path.write_bytes(buf.getvalue())
    return buf.tell()


def make_sheets(entries, b_by_id):
    """entries: [(b, result)] in order of n, only buildings with candidates."""
    for old in SHEETS.glob('sheet_*.jpg'):
        old.unlink()
    for s in range(0, len(entries), PER_SHEET):
        rows, urls = [], {}
        part = entries[s:s + PER_SHEET]
        need = [c['file'] for _, r in part for c in r['found'][:ON_SHEET]] + [r['lead'] for _, r in part if r['lead']]
        try:
            urls = retry(thumb_urls, need)
        except Exception as e:
            print('thumb urls failed:', e)
        for b, r in part:
            _, lead_im = lead_of(b)
            local = ROOT / 'site' / lead_im['thumb'] if lead_im and lead_im.get('thumb') else None
            lead = fetch_thumb(urls.get(r['lead']), local) if (r['lead'] or local) else None
            cands = [(f"c{k + 1} {c['rating']}", fetch_thumb(urls.get(c['file']))) for k, c in enumerate(r['found'][:ON_SHEET])]
            mark = 'RATED' if r['lead_rated'] else 'plain'
            rows.append((f"{b['n']} {b['id']} — {b['name']} ({b['place']})  [main: {mark}]", lead, cands))
        n = s // PER_SHEET + 1
        size = build_sheet(rows, SHEETS / f'sheet_{n:02d}.jpg')
        print(f'sheet_{n:02d}.jpg: {len(part)} buildings, {size // 1000} KB')


# ---------- main ----------
def selftest():
    from PIL import Image
    assert rating('featured') == 'F' and rating('Quality, valued') == 'Q' and rating('valued') == 'V' and rating('') is None
    b = {'id': 'x', 'name': 'Falling Water House', 'by': 'Frank Lloyd Wright', 'place': 'Mill Run, US'}
    meta = lambda a='quality', lic='CC BY-SA 4.0', d='Fallingwater, Mill Run': {'Assessments': {'value': a}, 'LicenseShortName': {'value': lic}, 'ImageDescription': {'value': d}}
    mk = lambda **kw: {'mime': 'image/jpeg', 'width': 3000, 'height': 2000, 'extmetadata': meta(**kw.pop('m', {})), 'cats': 'Category:Falling Water', **kw}
    assert judge(b, 'File:A.jpg', mk(), direct=True)[0]['rating'] == 'Q'
    assert judge(b, 'File:A.jpg', mk(m={'a': ''}))[1] == 'not rated'
    assert judge(b, 'File:A.jpg', mk(m={'lic': 'CC BY-NC 4.0'}))[1] == 'licence'
    assert judge(b, 'File:A.jpg', mk(width=1200, height=800))[1] == 'small'
    assert judge(b, 'File:A.jpg', mk(mime='image/svg+xml'))[1] == 'type'
    assert judge(b, 'File:A_b.jpg', mk(), taken={'File:A b.jpg'})[1] == 'already have'
    assert judge(b, 'File:Night view.jpg', mk(), direct=True)[1] == 'night'
    assert judge(b, 'File:A.jpg', mk(m={'d': 'Crowd in the lobby'}), direct=True)[1] in ('junk', 'people/event')
    assert judge(b, 'File:A.jpg', mk(m={'d': 'A painting on a wall'}), direct=True)[1] == 'artwork'
    other = mk(m={'d': 'Some house in Pittsburgh'}); other['cats'] = 'Category:Houses'
    assert judge(b, 'File:IMG1.jpg', other)[1] == 'other building?'
    assert judge(b, 'File:IMG1.jpg', other, direct=True)[0]['why_kept'] == 'direct'
    assert judge(b, 'File:IMG1.jpg', other, p18=True)[0]['why_kept'] == 'p18'
    cityonly = mk(m={'d': 'A house in Mill Run'}); cityonly['cats'] = 'Category:Houses'
    assert judge(b, 'File:IMG1.jpg', cityonly)[0]['why_kept'] == 'city'
    c = judge(b, 'File:A.jpg', mk(), direct=True)[0]
    assert c['cats'] == ['Falling Water'], c['cats']
    # sheet layout with dummy images
    OUT.mkdir(parents=True, exist_ok=True)
    dummy = lambda col: Image.new('RGB', (TW, 150), col)
    rows = [(f'{i} id-{i} — Name ({i})', dummy((200, 90, 90)), [(f'c{k + 1} F', dummy((90, 90, 200 - k * 20))) for k in range(ON_SHEET if i % 2 else 2)]) for i in range(PER_SHEET)]
    import tempfile
    p = Path(tempfile.mkdtemp()) / 'sheet.jpg'
    global SHEETS
    SHEETS = p.parent
    size = build_sheet(rows, p)
    im = Image.open(p)
    print('selftest ok; dummy sheet', im.size, size // 1000, 'KB at', p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--first', type=int, default=0)
    ap.add_argument('--offset', type=int, default=0)
    ap.add_argument('--ids', default='')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--no-sheets', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    items = sorted(load_buildings(), key=lambda b: b['n'])
    if a.ids:
        want = set(a.ids.split(','))
        items = [b for b in items if b['id'] in want]
    elif a.first:
        items = items[a.offset:a.offset + a.first]
    choices, removed = hand_lists()
    OUT.mkdir(parents=True, exist_ok=True)
    result, entries, errors, totals = {}, [], [], {}
    for k, b in enumerate(items, 1):
        try:
            r, why = retry(scan, b, choices, removed)
        except Exception as e:
            errors.append(f"{b['id']}: {e}")
            print(f"[{k}/{len(items)}] {b['id']}: FAILED")
            continue
        for w, n in why.items():
            totals[w] = totals.get(w, 0) + n
        flag = '' if r['category_fits'] else '  (category name does not fit)'
        print(f"[{k}/{len(items)}] {b['n']} {b['id']}: scanned {r['scanned']}, {len(r['found'])} rated{flag}")
        if r['found']:
            result[b['id']] = {key: r[key] for key in ('lead', 'lead_rated', 'found', 'category', 'category_fits', 'scanned')}
            entries.append((b, r))
        if k % 25 == 0:
            (OUT / 'candidates.json').write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding='utf-8')
    (OUT / 'candidates.json').write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding='utf-8')
    (OUT / 'scan_report.txt').write_text(
        f'buildings scanned: {len(items) - len(errors)} of {len(items)}\nwith rated candidates: {len(result)}\n'
        f'files dropped by reason: {json.dumps(totals)}\nerrors: {len(errors)}\n' + '\n'.join(errors) + '\n', encoding='utf-8')
    print('scanned', len(items), 'with candidates', len(result), 'dropped', totals, 'errors', len(errors))
    if not a.no_sheets:
        make_sheets(entries, {b['id']: b for b in items})


if __name__ == '__main__':
    main()
