#!/usr/bin/env python3
"""Split the unreviewed candidates into sheets, one per first-pass reviewer.

  python3 tools/films_sheets.py <out folder> [--per 25] [--max 400]

films_batch.py next prints the candidates a reviewer should see, but not the text a judgement rests on. Each sheet
here carries that text: the Wikipedia opening paragraph saved with the candidate, or TMDB's overview, which is the
only thing the quote may be copied from. Nothing else is network-fetched, so a reviewer cannot wander off to a
sales page.

Each sheet is a JSON list. A reviewer writes a draft of the same length, one entry per film, and
films_check_draft.py checks every quote against these same texts before anything is added.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import films_ref
from films_batch import relevant, key_of, load, CANDS, REVIEWED, SEED

# What a reviewer needs to judge a film, and nothing more: no poster paths, no vote counts to be swayed by.
FIELDS = ('title', 'year', 'director', 'runtime_min', 'wd_desc', 'subjects', 'architects', 'instance_of',
          'genres_wd', 'enwiki', 'extract', 'overview', 'sources')


def main(out_dir, per, cap):
    seen = set(load(REVIEWED, [])) | {key_of(f['title'], f.get('year')) for f in load(SEED, [])}
    rows = []
    for c in sorted(load(CANDS, []), key=lambda c: (-len(c.get('architects') or []), -(c.get('votes') or 0))):
        if not relevant(c) or key_of(c['title'], c.get('year')) in seen:
            continue
        seen.add(key_of(c['title'], c.get('year')))          # one sheet entry per key, never two reviewers on one film
        row = {'ref': films_ref.refs_of(c)[0]}
        row.update({f: c[f] for f in FIELDS if c.get(f)})
        if not (row.get('extract') or row.get('overview')):
            continue                                          # no saved text means no quotable source: not reviewable
        rows.append(row)
        if len(rows) >= cap:
            break

    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    sheets = [rows[i:i + per] for i in range(0, len(rows), per)]
    for i, s in enumerate(sheets, 1):
        (out / f'sheet_{i:02d}.json').write_text(json.dumps(s, ensure_ascii=False, indent=1) + '\n')
    print(f'{len(rows)} reviewable candidates -> {len(sheets)} sheets of up to {per} in {out}')
    skipped = sum(1 for c in load(CANDS, []) if relevant(c) and not (c.get('extract') or c.get('overview'))
                  and key_of(c['title'], c.get('year')) not in
                  (set(load(REVIEWED, [])) | {key_of(f['title'], f.get('year')) for f in load(SEED, [])}))
    if skipped:
        print(f'{skipped} left out for having no saved Wikipedia or TMDB text to quote')


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    per = int(a[a.index('--per') + 1]) if '--per' in a else 25
    cap = int(a[a.index('--max') + 1]) if '--max' in a else 400
    main(a[0], per, cap)
