#!/usr/bin/env python3
"""Check a first-pass draft of film entries against the sources it claims to rest on.

  python3 tools/films_check_draft.py <candidates.json> <draft1.json> [draft2.json ...]

A draft entry says what a film is about and quotes the words it got that from. This checks the quote is really
there, character for character, in that film's saved Wikipedia opening paragraph. A quote that has been retyped,
tidied or stitched together from two sentences fails, because a summary resting on words nobody wrote is exactly
the invented fact the brief forbids. Also checks the genres are from the fixed seven and the summary is short
enough. Prints a report and exits non-zero if anything failed, so a bad draft cannot slip through quietly.
"""
import json, re, sys, unicodedata
from pathlib import Path

GENRES = ['Portrait of an architect', 'Building story', 'City & urbanism', 'Housing & social',
          'Design process', 'Movement & history', 'Landscape & sustainability']
KINDS = ['feature', 'series', 'episode', 'lecture']


def norm(s):
    """Fold the quote marks, dashes and runs of space that a copy through JSON can change, and nothing else."""
    s = unicodedata.normalize('NFKC', s or '')
    s = s.replace('‘', "'").replace('’', "'").replace('“', '"').replace('”', '"')
    s = s.replace('–', '-').replace('—', '-').replace('−', '-').replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip().lower()


def main(cand_path, draft_paths):
    cands = {c['qid']: c for c in json.loads(Path(cand_path).read_text()) if c.get('qid')}
    rows, bad = [], []
    for dp in draft_paths:
        for d in json.loads(Path(dp).read_text()):
            qid, title = d.get('qid'), d.get('title', '?')
            where = f'{Path(dp).name} {title[:40]}'
            if d.get('verdict') == 'reject':
                rows.append(('reject', title, d.get('why', '')))
                continue
            c = cands.get(qid)
            if not c:
                bad.append(f'{where}: qid {qid!r} is not in the candidates'); continue
            q, extract = d.get('summary_quote'), c.get('extract') or ''
            if not q:
                bad.append(f'{where}: kept, but quotes nothing')
            elif norm(q) not in norm(extract):
                bad.append(f'{where}: the quote is not in the source paragraph\n      quoted: {q[:110]}')
            if not d.get('summary'):
                bad.append(f'{where}: no summary')
            elif len(d['summary']) > 200:
                bad.append(f'{where}: summary is {len(d["summary"])} characters, over 200')
            for g in d.get('genres') or []:
                if g not in GENRES:
                    bad.append(f'{where}: {g!r} is not one of the seven genres')
            if not d.get('genres'):
                bad.append(f'{where}: no genre')
            if d.get('kind') not in KINDS:
                bad.append(f'{where}: kind {d.get("kind")!r} is not one of {KINDS}')
            rows.append(('keep', title, d.get('summary', '')))

    keeps = [r for r in rows if r[0] == 'keep']
    print(f'{len(rows)} drafted: {len(keeps)} keep, {len(rows) - len(keeps)} reject')
    if rows:
        share = 100 * (len(rows) - len(keeps)) / len(rows)
        flag = ' — STOP level passed, ask before adding' if share >= 60 else (' — warn level passed' if share >= 40 else '')
        print(f'rejected {share:.0f}% of candidates{flag}')
    if bad:
        print(f'\n{len(bad)} FAILED the source check:')
        for b in bad:
            print('  -', b)
        share = 100 * len(bad) / max(len(rows), 1)
        print(f'\nfacts failing the source check: {share:.0f}% (warn 3%, stop 6%)')
        return 1
    print('\nEvery kept film quotes words that are really in its source paragraph.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2:]))
