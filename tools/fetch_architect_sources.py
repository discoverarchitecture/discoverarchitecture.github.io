#!/usr/bin/env python3
"""Fetch the sources for the architect write-ups: Wikidata facts and the Wikipedia article text.

  python -u tools/fetch_architect_sources.py --ranks 1-10
  python -u tools/fetch_architect_sources.py --only "Zaha Hadid,OMA"
  python -u tools/fetch_architect_sources.py --ranks 11-40 --qids "OMA=Q1416588"

Reads tools/architect_bios/todo.json. For each architect it finds the Wikidata item (the todo's qid, or a
search on the name when the qid is missing or "manual:"), then keeps: birth and death dates, citizenship,
awards with years, notable works, official website, and the English Wikipedia article (introduction plus the
plain text of the whole article, cut at about 6,000 words). Results are merged into
tools/architect_bios/sources.json (name -> record), so batches can be fetched one after another.
With --buildings NAME, it also fetches the English Wikipedia text (introduction plus design sections, about 800
words) of every wall building by these architects, into tools/architect_bios/building_sources/NAME.json
(building id -> record); --no-architects skips the architect records, --skip leaves names out.
With --pages FILE (a JSON list of addresses), it also saves the plain text of each page into
tools/architect_bios/page_sources.json (address -> record): any-language Wikipedia articles through their API, other
sites as text stripped from the HTML. For architects and buildings with no English article.
Needs network access to wikidata.org and en.wikipedia.org: runs on GitHub Actions (architect-bios.yml).
"""
import argparse, html, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / 'tools' / 'architect_bios'
OUT = DIR / 'sources.json'
UA = 'FindGreatArchitecture/1.0 (https://findgreatarchitecture.com; architect write-ups script)'
WD = 'https://www.wikidata.org/w/api.php'
WP = 'https://en.wikipedia.org/w/api.php'
MAX_WORDS = 6000


def get(url, params):
    url = url + '?' + urllib.parse.urlencode({**params, 'format': 'json'})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as r:
                return json.loads(r.read().decode())
        except Exception as err:
            print('  retry', attempt, err)
            if attempt == 5:
                raise
            time.sleep(5 * (attempt + 1))


def search_qid(name):
    res = get(WD, {'action': 'wbsearchentities', 'search': name, 'language': 'en', 'type': 'item', 'limit': 7})
    for hit in res.get('search', []):
        desc = (hit.get('description') or '').lower()
        if any(w in desc for w in ('architect', 'architecture', 'design', 'firm', 'practice', 'studio')):
            return hit['id'], hit.get('description')
    return None, None


def labels(qids):
    out = {}
    qids = list(dict.fromkeys(qids))
    for i in range(0, len(qids), 50):
        res = get(WD, {'action': 'wbgetentities', 'ids': '|'.join(qids[i:i + 50]), 'props': 'labels', 'languages': 'en'})
        for q, ent in res.get('entities', {}).items():
            out[q] = ent.get('labels', {}).get('en', {}).get('value', q)
    return out


def time_of(snak):
    try:
        t = snak['datavalue']['value']['time']
        prec = snak['datavalue']['value']['precision']
        return t[1:11] if prec >= 11 else t[1:5]
    except (KeyError, TypeError):
        return None


def entity(qid):
    ent = get(WD, {'action': 'wbgetentities', 'ids': qid, 'props': 'claims|sitelinks|descriptions|labels',
                   'languages': 'en'})['entities'][qid]
    claims = ent.get('claims', {})

    def items(p):
        return [c['mainsnak']['datavalue']['value']['id'] for c in claims.get(p, [])
                if c['mainsnak'].get('datavalue')]

    def times(p):
        return [time_of(c['mainsnak']) for c in claims.get(p, []) if time_of(c['mainsnak'])]

    awards = []
    for c in claims.get('P166', []):
        if not c['mainsnak'].get('datavalue'):
            continue
        year = None
        for q in c.get('qualifiers', {}).get('P585', []):
            year = time_of(q)
        awards.append((c['mainsnak']['datavalue']['value']['id'], year))
    refs = items('P27') + items('P800') + items('P31') + items('P17') + items('P159') + items('P112') + [a for a, _ in awards]
    lab = labels(refs) if refs else {}
    sites = [c['mainsnak']['datavalue']['value'] for c in claims.get('P856', []) if c['mainsnak'].get('datavalue')]
    return {
        'qid': qid,
        'label': ent.get('labels', {}).get('en', {}).get('value'),
        'description': ent.get('descriptions', {}).get('en', {}).get('value'),
        'instance_of': [lab.get(q, q) for q in items('P31')],
        'born': (times('P569') or [None])[0],
        'died': (times('P570') or [None])[0],
        'founded': (times('P571') or [None])[0],
        'citizenship': [lab.get(q, q) for q in items('P27')],
        'country': [lab.get(q, q) for q in items('P17')],
        'headquarters': [lab.get(q, q) for q in items('P159')],
        'founded_by': [lab.get(q, q) for q in items('P112')],
        'awards': [{'award': lab.get(a, a), 'year': y} for a, y in awards],
        'notable_works': [lab.get(q, q) for q in items('P800')],
        'website': sites,
        'enwiki': ent.get('sitelinks', {}).get('enwiki', {}).get('title'),
        'wikidata_url': f'https://www.wikidata.org/wiki/{qid}',
    }


def wikipedia(title):
    res = get(WP, {'action': 'query', 'prop': 'extracts', 'explaintext': 1, 'titles': title, 'redirects': 1,
                   'formatversion': 2})
    page = res['query']['pages'][0]
    text = page.get('extract', '')
    intro = text.split('\n==', 1)[0].strip()
    text = re.sub(r'\n==+ (References|Notes|Sources|Further reading|External links|Bibliography|See also) ==+.*',
                  '', text, flags=re.S)
    words = text.split(' ')
    if len(words) > MAX_WORDS:
        text = ' '.join(words[:MAX_WORDS]) + ' [...]'
    return {'title': page.get('title'), 'url': 'https://en.wikipedia.org/wiki/' + page.get('title', '').replace(' ', '_'),
            'intro': intro, 'text': text}


SECTION_WORDS = ('architect', 'design', 'structure', 'construction', 'building', 'description', 'exterior',
                 'interior', 'layout', 'features', 'facade', 'façade', 'roof', 'material', 'plan')
BUILDING_WORDS = 800


def building_text(title):
    """Introduction plus the sections whose heading is about the design, cut at about 800 words."""
    page = wikipedia(title)
    parts = [page['intro']]
    for m in re.finditer(r'\n==+ ([^=]+?) ==+\n(.*?)(?=\n==+ [^=]+? ==+\n|$)', page['text'], re.S):
        if any(w in m.group(1).lower() for w in SECTION_WORDS):
            parts.append(m.group(1).strip() + ': ' + m.group(2).strip())
    words = ' '.join(parts).split(' ')
    page['text'] = ' '.join(words[:BUILDING_WORDS]) + (' [...]' if len(words) > BUILDING_WORDS else '')
    page.pop('intro')
    return page


def surname(name):
    """The word that should appear in a building's article: the last word of a person's name, or a firm's name."""
    words = [w for w in re.split(r'[\s,]+', name.lower()) if w not in ('architekten', 'architects', 'associates')]
    return words[-1] if words else name.lower()


def buildings(entries, name):
    site = ROOT / 'site' / 'data' / 'buildings.js'
    items = json.loads(site.read_text().split('window.BUILDINGS = ', 1)[1].rstrip().rstrip(';'))
    by = {b['id']: b for b in items}
    out_dir = DIR / 'building_sources'
    out_dir.mkdir(exist_ok=True)
    out = {}
    for e in entries:
        for bid in e.get('building_ids', []):
            b = by.get(bid)
            if not b or bid in out:
                continue
            rec = {'name': b['name'], 'architect': e['name'], 'qid': b.get('qid')}
            try:
                qid = b.get('qid')
                title = None
                if qid:
                    ent = get(WD, {'action': 'wbgetentities', 'ids': qid, 'props': 'sitelinks'})['entities'][qid]
                    title = ent.get('sitelinks', {}).get('enwiki', {}).get('title')
                else:
                    # no Wikidata item on the wall: search Wikipedia for "<building> <architect>" and keep the
                    # first article that names the architect (a name-only search picked wrong items before)
                    hits = get(WP, {'action': 'query', 'list': 'search', 'srsearch': f"{b['name']} {e['name']}",
                                    'srlimit': 3, 'formatversion': 2})['query']['search']
                    rec['found_by_search'] = True
                    for h in hits:
                        page = building_text(h['title'])
                        if surname(e['name']) in page['text'].lower():
                            rec.update(page)
                            break
                if title:
                    rec.update(building_text(title))
            except Exception as err:
                rec['error'] = str(err)
            print(f"   {bid}: {rec.get('title')}")
            out[bid] = rec
            time.sleep(0.5)
    path = out_dir / f'{name}.json'
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print('wrote', path, len(out))


PAGES_OUT = DIR / 'page_sources.json'


def page_text(url):
    """Plain text of one page: a Wikipedia article in any language through its API, anything else from its HTML."""
    m = re.match(r'https://([a-z-]+)\.wikipedia\.org/wiki/(.+)', url)
    if m:
        lang, title = m.group(1), urllib.parse.unquote(m.group(2)).replace('_', ' ')
        res = get(f'https://{lang}.wikipedia.org/w/api.php', {'action': 'query', 'prop': 'extracts', 'explaintext': 1,
                                                             'titles': title, 'redirects': 1, 'formatversion': 2})
        page = res['query']['pages'][0]
        title, text = page.get('title'), page.get('extract', '')
    else:
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'en'})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode(r.headers.get_content_charset() or 'utf-8', 'replace')
        t = re.search(r'<title[^>]*>(.*?)</title>', raw, re.S | re.I)
        title = html.unescape(t.group(1).strip()) if t else None
        raw = re.sub(r'<(script|style|noscript|svg)\b.*?</\1>', ' ', raw, flags=re.S | re.I)
        raw = re.sub(r'<br\s*/?>|</(p|div|li|h[1-6]|tr)>', '\n', raw, flags=re.I)
        text = html.unescape(re.sub(r'<[^>]+>', ' ', raw))
        text = '\n'.join(re.sub(r'[ \t\r\f\v]+', ' ', line).strip() for line in text.split('\n'))
        text = re.sub(r'\n{2,}', '\n', text).strip()
    words = text.split(' ')
    if len(words) > MAX_WORDS:
        text = ' '.join(words[:MAX_WORDS]) + ' [...]'
    return {'url': url, 'title': title, 'text': text}


def pages(listfile):
    urls = json.loads((ROOT / listfile).read_text())
    out = json.loads(PAGES_OUT.read_text()) if PAGES_OUT.exists() else {}
    for url in urls:
        try:
            out[url] = page_text(url)
            print('  page', url, len(out[url]['text'].split()), 'words')
        except Exception as err:
            out[url] = {'url': url, 'error': str(err)}
            print('  page FAILED', url, err)
        time.sleep(1)
    PAGES_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print('wrote', PAGES_OUT, len(out))


def pick(todo, ranks, only):
    if only:
        names = {n.strip() for n in only.split(',')}
        return [e for e in todo if e['name'] in names]
    if ranks:
        a, _, b = ranks.partition('-')
        return [e for e in todo if int(a) <= e['rank'] <= int(b or a)]
    return todo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ranks')
    ap.add_argument('--only')
    ap.add_argument('--buildings', help='also fetch wall buildings into building_sources/NAME.json')
    ap.add_argument('--no-architects', action='store_true')
    ap.add_argument('--skip', help='names to leave out, comma-separated')
    ap.add_argument('--qids', help='overrides, "Name=Q123,Other=search phrase"')
    ap.add_argument('--pages', help='JSON list of addresses to save as text into page_sources.json')
    args = ap.parse_args()
    if args.pages:
        pages(args.pages)
        if not (args.ranks or args.only):
            return
    todo = json.loads((DIR / 'todo.json').read_text())
    over = dict(p.split('=', 1) for p in (args.qids or '').split(',') if '=' in p)
    out = json.loads(OUT.read_text()) if OUT.exists() else {}
    skip = {n.strip() for n in (args.skip or '').split(',') if n.strip()}
    entries = [e for e in pick(todo, args.ranks, args.only) if e['name'] not in skip]
    if args.buildings:
        buildings(entries, args.buildings)
    if args.no_architects:
        return
    for e in entries:
        name = e['name']
        qid = over.get(name) or e.get('qid')
        note = None
        if not qid or not re.fullmatch(r'Q\d+', str(qid)):
            # "manual:Name", a missing qid or an override that is a search phrase: search Wikidata
            text = str(qid)[7:] if str(qid).startswith('manual:') else (qid if qid else name)
            qid, note = search_qid(text)
        print(f"{e['rank']:>3} {name}: {qid} {note or ''}")
        rec = {'name': name, 'rank': e['rank'], 'qid_found_by_search': bool(note)}
        if qid:
            try:
                rec['wikidata'] = entity(qid)
                if rec['wikidata'].get('enwiki'):
                    rec['wikipedia'] = wikipedia(rec['wikidata']['enwiki'])
            except Exception as err:
                rec['error'] = str(err)
        out[name] = rec
        time.sleep(1)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print('wrote', OUT, len(out))


if __name__ == '__main__':
    main()
