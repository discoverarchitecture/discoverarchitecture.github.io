"""Makes tools/outreach/pinterest_bulk.csv for Pinterest's bulk pin upload (Business hub > Create > Bulk create pins).

Free Wikimedia photos only: the first Exterior photo of each building that is hosted as a .jpg/.png on upload.wikimedia.org.
Run: python3 tools/pinterest_csv.py [first_publish_date YYYY-MM-DD]   (8 pins a day, from 09:00 UTC, 30 days max)
"""
import csv, json, os, re, sys, datetime as dt
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://findgreatarchitecture.com'
BOARD = {  # movement -> (board, how many)
    'Modernism': 'Modernism icons', 'Late modernism': 'Modernism icons', 'Art Deco': 'Modernism icons',
    'Art Nouveau': 'Modernism icons', 'Expressionism': 'Modernism icons',
    'Brutalism': 'Brutalism',
    'Contemporary': 'Contemporary & parametric', 'Parametric': 'Contemporary & parametric',
    'Deconstructivism': 'Contemporary & parametric', 'High-tech': 'Contemporary & parametric',
    'Regionalism': 'Regionalism',
    'Historic precedent': 'Historic precedents',
}
QUOTA = {'Modernism icons': 50, 'Brutalism': 50, 'Contemporary & parametric': 50, 'Regionalism': 30, 'Historic precedents': 20}
DONE = set(open(os.path.join(ROOT, 'tools/outreach/pinterest_week1_ids.txt')).read().split())  # pinned by hand already

pv = json.load(open(os.path.join(ROOT, 'tools/pageviews.json')))
views = lambda k: (lambda v: v if isinstance(v, (int, float)) else v.get('views', 0) if isinstance(v, dict) else 0)(pv.get(k, 0))
wall = {}
for line in open(os.path.join(ROOT, 'site/data/wall.js'), encoding='utf-8'):
    if line.startswith('{"id"'):
        d = json.loads(line.rstrip().rstrip(','))
        wall[d['id']] = d
CC = {}
m = re.search(r'=\s*(\{.*\})', open(os.path.join(ROOT, 'site/data/world.js'), encoding='utf-8').read(), re.S)
try: CC = json.loads(m.group(1)).get('names', {}) if m else {}
except Exception: CC = {}

def photo(i):
    try: d = json.load(open(os.path.join(ROOT, f'site/data/detail/{i}.json'), encoding='utf-8'))
    except Exception: return None
    for im in d.get('images', []):
        s = im.get('src', '')
        s = s.split('?')[0].replace('https://thumb.wikimedia.org/', 'https://upload.wikimedia.org/')  # drop the tracking tail
        if im.get('kind') == 'Exterior' and s.startswith('https://upload.wikimedia.org/') and re.search(r'\.(jpe?g|png)$', s, re.I) and (im.get('w') or 0) >= 1000:
            return dict(im, src=s)
    return None

pools = defaultdict(list)
for i in sorted(wall, key=lambda k: -views(k)):
    b = BOARD.get(wall[i].get('movement'))
    if not b or i in DONE or len(pools[b]) >= QUOTA[b] or not os.path.exists(os.path.join(ROOT, f'site/buildings/{i}/index.html')): continue
    im = photo(i)
    if im: pools[b].append((i, im))

order = []  # alternate boards so no day is all one board
while any(pools.values()):
    for b in QUOTA:
        if pools[b]: order.append((b,) + pools[b].pop(0))

start = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today() + dt.timedelta(days=1)
rows = []
for n, (b, i, im) in enumerate(order):
    w = wall[i]; city = w['place'].split(',')[0].strip()
    by = w['by'].split(' with ')[0]
    title = f"{w['name']} by {by}, {w['year']} · {city}"[:100]
    credit = f"Photo: {im.get('credit', '').split('  from')[0].strip()}, {im.get('license', '')}, via Wikimedia Commons."
    desc = f"{w['study']} {w['type']} · {w['place']} · {w['year']}. Free credited photos and key features for your case study at Find Great Architecture. {credit}"[:500]
    day = start + dt.timedelta(days=n // 8)
    when = dt.datetime.combine(day, dt.time(9, 0)) + dt.timedelta(hours=3 * (n % 8))
    rows.append([title, im['src'], b, '', desc, f'{SITE}/buildings/{i}/?ref=pinterest', when.strftime('%Y-%m-%dT%H:%M:%S'), ', '.join([w['movement'], w['type'], 'architecture case study'])])

out = os.path.join(ROOT, 'tools/outreach/pinterest_bulk.csv')
with open(out, 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f); wr.writerow(['Title', 'Media URL', 'Pinterest board', 'Thumbnail', 'Description', 'Link', 'Publish date', 'Keywords']); wr.writerows(rows)
print(len(rows), 'pins ->', out, '| last publish', rows[-1][6] if rows else '-')
for b in QUOTA: print(b, sum(1 for r in rows if r[2] == b))
