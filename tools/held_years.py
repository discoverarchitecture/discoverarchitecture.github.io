#!/usr/bin/env python3
"""Look for a sourced year for buildings held back for want of one.

  python -u tools/held_years.py    # reads tools/cheap/held_all.json, writes tools/cheap/held_years.json

For each held building it saves Wikidata's dates (inception P571, opening P1619, start P580, end P582,
demolished P576, with any qualifiers) and, from its English Wikipedia article and the article in the language
its lead came from, the whole introduction and every sentence of the article that pairs a year with a word for
building, opening or completing. A reviewer then picks the completion year and quotes the sentence that gives it.
Needs open internet access, so it runs on GitHub Actions (run-tool.yml).
"""
import json, re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_images import api, WD  # noqa: E402
from harvest import value  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
IN = ROOT / 'tools' / 'cheap' / 'held_all.json'
OUT = ROOT / 'tools' / 'cheap' / 'held_years.json'
DATES = {'P571': 'inception', 'P1619': 'opened', 'P580': 'start', 'P582': 'end', 'P576': 'demolished'}
WORDS = re.compile(r'complet|finish|open|inaugur|built|construct|erect|consecrat|dedicat|fertig|eröffn|erbaut|errichtet|geweiht|'
                   r'inaugur|achev|constru|ouvert|voltooid|geopend|gebouwd|termin|abiert|complet|costru|inaugura|aperto|'
                   r'dokonč|otevř|postav|valmistu|avattiin|rakennet|färdig|invig|byggd|竣工|開館|完成|建設', re.I)
YEAR = re.compile(r'\b(1[89]\d\d|20[0-2]\d)\b')


def wiki(lang, title, intro):
    q = api(f'https://{lang}.wikipedia.org/w/api.php', action='query', prop='extracts', explaintext=1,
            titles=title, redirects=1, **({'exintro': 1} if intro else {}))
    pages = q.get('query', {}).get('pages', [])
    page = pages[0] if isinstance(pages, list) and pages else next(iter(pages.values()), {}) if isinstance(pages, dict) else {}
    return ' '.join((page.get('extract') or '').split())


def sentences(text):
    out = []
    for s in re.split(r'(?<=[.!?。])\s+', text):
        if YEAR.search(s) and WORDS.search(s):
            out.append(s[:400])
    return out[:12]


def main():
    rows = json.loads(IN.read_text(encoding='utf-8'))
    for k in range(0, len(rows), 50):
        q = api(WD, action='wbgetentities', ids='|'.join(r['qid'] for r in rows[k:k + 50]), props='claims|sitelinks')
        for r in rows[k:k + 50]:
            ent = q.get('entities', {}).get(r['qid'], {})
            r['wikidata'] = {}
            for p, name in DATES.items():
                vals = []
                for c in ent.get('claims', {}).get(p, []):
                    if c['mainsnak'].get('snaktype') != 'value':
                        continue
                    quals = {qp: [value(x) for x in qv] for qp, qv in c.get('qualifiers', {}).items()}
                    vals.append({'value': value(c['mainsnak']), 'qualifiers': quals} if quals else value(c['mainsnak']))
                if vals:
                    r['wikidata'][name] = vals
            r['sitelinks'] = {s[:-4]: v['title'] for s, v in ent.get('sitelinks', {}).items() if s.endswith('wiki')}
    for r in rows:
        r['articles'] = []
        langs = ['en'] + [l for l in (r.get('lead_lang'), 'de', 'fr', 'nl', 'es', 'it', 'cs', 'ja', 'sv', 'fi') if l and l != 'en']
        for lang in langs:
            title = r['sitelinks'].get(lang)
            if not title or any(a['lang'] == lang for a in r['articles']):
                continue
            try:
                intro = wiki(lang, title, True)[:2500]
                full = wiki(lang, title, False)[:40000]
            except Exception as e:
                print(r['id'], lang, 'failed:', e, flush=True)
                continue
            r['articles'].append({'lang': lang, 'title': title, 'intro': intro, 'year_sentences': sentences(full)})
            if len(r['articles']) >= 3:
                break
            time.sleep(0.3)
        print(r['id'], len(r['articles']), 'articles', flush=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'Wrote {len(rows)} held buildings to {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    sys.exit(main())
