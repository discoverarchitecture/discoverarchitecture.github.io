#!/usr/bin/env python3
"""Give prepared candidates without an English Wikipedia article a lead from another language's article.

  python -u tools/cheap_leads.py

Reads tools/cheap/prep.json (written by cheap_prep.py), and for each row with no lead looks up the building's
Wikipedia articles on Wikidata, takes the first one in LANGS order and saves its lead (up to 900 characters) as
`lead`, with `lead_lang` and `lead_title`, so the judging model has a source to translate from. Rewrites prep.json.
"""
import json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_images import api, WD  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PREP = ROOT / 'tools' / 'cheap' / 'prep.json'
LANGS = ['de', 'fr', 'nl', 'es', 'it', 'pt', 'ja', 'ca', 'cs', 'sv', 'da', 'nb', 'fi', 'pl', 'sk', 'hu', 'zh', 'ko']


def lead(lang, title):
    q = api(f'https://{lang}.wikipedia.org/w/api.php', action='query', prop='extracts', exintro=1, explaintext=1,
            titles=title, redirects=1)
    pages = q.get('query', {}).get('pages', [])
    page = pages[0] if isinstance(pages, list) and pages else next(iter(pages.values()), {}) if isinstance(pages, dict) else {}
    return ' '.join((page.get('extract') or '').split())[:900]


def main():
    rows = json.loads(PREP.read_text(encoding='utf-8'))
    todo = [r for r in rows if not r.get('lead')]
    links = {}
    for k in range(0, len(todo), 50):
        q = api(WD, action='wbgetentities', ids='|'.join(r['qid'] for r in todo[k:k + 50]), props='sitelinks')
        for qid, ent in q.get('entities', {}).items():
            links[qid] = {s[:-4]: v['title'] for s, v in ent.get('sitelinks', {}).items() if s.endswith('wiki')}
    found = 0
    for r in todo:
        have = links.get(r['qid'], {})
        for lang in LANGS:
            if lang in have:
                try:
                    text = lead(lang, have[lang])
                except Exception as e:
                    print(r['label'], lang, 'failed:', e, flush=True)
                    continue
                if text:
                    r.update(lead=text, lead_lang=lang, lead_title=have[lang])
                    found += 1
                    print(r['label'], '←', lang, flush=True)
                    break
        time.sleep(0.3)
    PREP.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'{found} of {len(todo)} rows without a lead got one from another language')


if __name__ == '__main__':
    main()
