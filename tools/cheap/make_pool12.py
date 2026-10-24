# usage: python3 tools/cheap/make_pool12.py -> tools/cheap/pool12.json from the prize winners (tools/harvest/awards.json and
# award_lists.json). The prize is the design reason, so no type is left out here; the 20% rule for ordinary types is
# kept at the Sonnet check. Not on the wall or judged before, 1900 on (or undated), not near a wall building, at most 4
# per architect.
import json, sys, re, unicodedata, collections, math, glob
sys.path.insert(0, 'tools')
from fetch_images import load
def norm(s): return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower())
h, items = load()
onq = {b.get('qid') for b in items if b.get('qid')}; names = [norm(b['name']) for b in items]; onname = set(names)
wc = [(b['coords'][0] if isinstance(b['coords'][0], list) else b['coords']) for b in items if b.get('coords')]
def near(c):
    if not c: return False
    la, lo = c
    return any(6371000 * math.hypot(math.radians(d[1] - lo) * math.cos(math.radians(la)), math.radians(d[0] - la)) < 60 for d in wc)
used = set()
for f in glob.glob('tools/cheap/pool*.json'):
    try: used |= {x['qid'] for x in json.load(open(f)) if isinstance(x, dict) and 'qid' in x}
    except Exception: pass
for f in glob.glob('tools/illustrate/results/*.json'):
    try: used |= {x.get('qid') for x in json.load(open(f)) if isinstance(x, dict)}
    except Exception: pass
rej = open('tools/illustrate/rejected.txt').read()
allq = {}
for f in ('tools/harvest/awards.json', 'tools/harvest/award_lists.json'):
    for r in json.load(open(f)):
        if r['qid'] in allq: allq[r['qid']]['awards'] = sorted(set(allq[r['qid']]['awards']) | set(r['awards']))
        else: allq[r['qid']] = r
def yr(c):
    ys = [int(m.group()) for k in ('inception', 'opened') for v in c.get(k) or [] for m in [re.search(r'\d{4}', str(v))] if m]
    return min(ys) if ys else 0
out = []; why = collections.Counter()
for c in allq.values():
    q = c['qid']
    if q in used or q in rej or q in onq: why['seen'] += 1; continue
    if not c.get('label'): why['no label'] += 1; continue
    y = yr(c)
    if y and y < 1900: why['before 1900'] += 1; continue
    a = [x for x in c.get('architect') or [] if not re.match(r'^Q\d+$', x)]
    if not a: why['no architect name'] += 1; continue
    n = norm(c['label'])
    if n in onname or (len(n) >= 10 and any(n in w or (len(w) >= 10 and w in n) for w in names)): why['name on wall'] += 1; continue
    if near((c.get('coords') or [None])[0]): why['near'] += 1; continue
    row = dict(c); row['architect'] = a; row['year'] = y or None; row['score'] = len(c['awards']); out.append(row)
print(why)
out.sort(key=lambda c: (-c['score'], c['qid']))
per = collections.Counter(); pool = []
for c in out:
    k = norm(c['architect'][0])
    if per[k] >= 4: continue
    per[k] += 1; pool.append(c)
print('eligible', len(out), 'pool', len(pool))
print(collections.Counter((c.get('country') or [''])[0] for c in pool).most_common(12))
json.dump(pool, open('tools/cheap/pool12.json', 'w'), ensure_ascii=False)
