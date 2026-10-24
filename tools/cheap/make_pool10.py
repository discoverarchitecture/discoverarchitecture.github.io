# usage: python3 tools/cheap/make_pool10.py 10 -> tools/cheap/pool10.json from tools/harvest/recent.json (buildings from 2000 on)
import json,sys,re,unicodedata,collections,math
N=int(sys.argv[1])
sys.path.insert(0,'tools')
from fetch_images import load
def norm(s): return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower())
h,items=load()
onq={b.get('qid') for b in items if b.get('qid')}; names=[norm(b['name']) for b in items]; onname=set(names)
wc=[(b['coords'][0] if isinstance(b['coords'][0],list) else b['coords']) for b in items if b.get('coords')]
def near(c):
    if not c: return False
    la,lo=c
    for d in wc:
        x=math.radians(d[1]-lo)*math.cos(math.radians(la)); y=math.radians(d[0]-la)
        if 6371000*math.hypot(x,y)<60: return True
    return False
arch=collections.Counter(); last=collections.defaultdict(int)
for b in items:
    for a in re.split(r',| and |&',b['by']):
        if a.strip(): arch[norm(a)]+=1; last[norm(a)]=max(last[norm(a)],b.get('y') or 0)
R=json.load(open('tools/harvest/recent.json'))
used=set()
for k in range(1,N):
    f='tools/cheap/pool.json' if k==1 else f'tools/cheap/pool{k}.json'
    used|={x['qid'] for x in json.load(open(f))}
import glob
for f in glob.glob('tools/illustrate/results/*.json'):
    try: used|={x.get('qid') for x in json.load(open(f)) if isinstance(x,dict)}
    except Exception: pass
rej=open('tools/illustrate/rejected.txt').read()+open('tools/illustrate/recheck.md').read()
BAD=re.compile(r'stadium|estadio|stade|arena|ball ?park|ballpark|football|soccer|baseball|field\b|velodrome|race ?track|circuit|airport|terminal|bridge|monument|statue|hotel|motel|inn\b|lodge|resort|shopping|mall|outlet|store|shop\b|parking|\bdam\b|power station|power plant|station|casino|cemetery|ruins|archaeological|concept|unbuilt|project|proposed|demolished|destroyed|former|apartment|condominium|residential|residences|housing|tenement|office|commercial building|skyscraper|tower block|high-rise|\btowers?\b|turm\b|torre\b|castle|fortress|lighthouse|tomb|mausoleum|clock tower|hills\b|city of|district|neighbourhood|neighborhood|complex|headquarters|hospital|prison|factory|warehouse|data center|road|tunnel|highway|interchange|square|plaza|park\b|garden|lock\b|écluse|bus stop|embassy|courthouse|post office|federal building|custom house|armory|bank\b|school building|high school|elementary school|fire station|water tower|movie theater|cinema|carnegie library|estate\b|steg\b|footbridge|carriage house|white guard|cabin\b',re.I)
CORP=re.compile(r'populous|corporation|sekkei|kajima|obayashi|taisei|shimizu|takenaka|nbbj|hok\b|aecom|gensler|starck|hks\b|rmjm|louis a\. simon|james knox taylor|supervising architect|james a\. wetmore|national park service|^Q\d+$',re.I)
HOUSE=re.compile(r'single-family|^house$|residence|\bhouse\b',re.I)
def yr(c):
    ys=[int(m.group()) for k in ('inception','opened') for v in c.get(k) or [] for m in [re.search(r'\d{4}',str(v))] if m]
    return (min(ys), max(ys)) if ys else (0, 0)
out=[]; why=collections.Counter()
for c in R:
    q=c['qid']
    if q in used or q in rej or q in onq: continue
    y0,yy=yr(c)
    if not c.get('label') or (y0 and y0<1998): continue
    lab=c.get('label') or ''
    inst=' '.join(c.get('instance') or [])
    if BAD.search(inst+' '+lab): why['type']+=1; continue
    a=[x for x in c.get('architect') or [] if not re.match(r'^Q\d+$',x)]
    if not a or any(CORP.search(x) for x in a): why['architect']+=1; continue
    if not (c.get('image') or c.get('commons')): why['no image']+=1; continue
    n=norm(lab)
    if n in onname or (len(n)>=10 and any(n in w or (len(w)>=10 and w in n) for w in names)): why['name on wall']+=1; continue
    if near((c.get('coords') or [None])[0]): why['near']+=1; continue
    known=max((arch[norm(x)] for x in a),default=0)
    if known and max(last[norm(x)] for x in a)<1975: why['old architect']+=1; continue
    if known==0 and HOUSE.search(inst+' '+lab): why['unknown house']+=1; continue
    row=dict(c); row['architect']=a
    row.update(year=yy or None, score=c.get('sitelinks',0), known=known)
    out.append(row)
out.sort(key=lambda c:-(c['score']+(3 if c['known'] else 0)))
per=collections.Counter(); pool=[]
for c in out:
    a=norm(c['architect'][0])
    if per[a]>=4: continue
    per[a]+=1; pool.append(c)
    if len(pool)==300: break
print('eligible',len(out),'pool',len(pool),'known',sum(c['known']>0 for c in pool))
print(collections.Counter(c.get('country',[None])[0] for c in pool).most_common(15))
print(collections.Counter((c.get('instance') or [None])[0] for c in pool).most_common(15))
print('lowest score',pool[-1]['score'])
print([(c['label'],c['architect'][0],c['year']) for c in pool[::10]])
json.dump(pool,open(f'tools/cheap/pool{N}.json','w'),ensure_ascii=False)
